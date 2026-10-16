"""Tests for the Python starter shipped in
skills/mcp-server-builder/references/starter-scaffold.md.

The starter lives in markdown, so these tests extract every file from it exactly as a
reader would copy it, then check it. Two groups:

1. Extraction and static checks (standard library only, always run): every file in the
   tree is present, the Python parses, the tool names follow the naming rule, every
   tool declares its class, and no refusal is raised as a plain exception.
2. Behaviour (needs the `mcp` package, skipped without it): the starter's own pytest
   suite passes, the refusal wording reaches a stdio client, broken input is refused,
   and a valid token is accepted.

To run group 2, install the SDK version the starter pins, in a virtual environment:

    python3 -m venv .venv
    .venv/bin/pip install "mcp==2.3.0" pytest pytest-asyncio
    .venv/bin/python -m unittest discover -s plugins/agent-builder/tests -v

With plain `python3` and no `mcp`, group 2 reports as skipped, not passed.
"""

from __future__ import annotations

import ast
import asyncio
import importlib
import importlib.util
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
SCAFFOLD = PLUGIN / "skills" / "mcp-server-builder" / "references" / "starter-scaffold.md"

EXPECTED_FILES = {
    "pyproject.toml",
    "src/example_server/__init__.py",
    "src/example_server/auth.py",
    "src/example_server/tools.py",
    "src/example_server/app.py",
    "tests/test_registration.py",
    "tests/test_tools.py",
    "tests/test_stdio.py",
}
SECTION = re.compile(r"^## ((?:src|tests)/\S+|pyproject\.toml)\n\n```\w+\n(.*?)^```", re.S | re.M)
TOOL_NAME = re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)+$")  # lowercase, underscore, verb first
HAS_MCP = importlib.util.find_spec("mcp") is not None


def extract(markdown: str) -> dict[str, str]:
    """Return {relative path: file content} for every file section in the scaffold."""
    return {m.group(1): m.group(2) for m in SECTION.finditer(markdown)}


def write_tree(files: dict[str, str], root: Path) -> None:
    for rel, body in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")


class TestExtraction(unittest.TestCase):
    """Normal, broken and edge input for the extractor itself."""

    def test_scaffold_yields_exactly_the_documented_tree(self):
        files = extract(SCAFFOLD.read_text(encoding="utf-8"))
        self.assertEqual(set(files), EXPECTED_FILES)

    def test_tree_block_matches_sections(self):
        text = SCAFFOLD.read_text(encoding="utf-8")
        tree = re.search(r"## Tree\n\n```text\n(.*?)```", text, re.S).group(1)
        listed = {line.strip() for line in tree.splitlines()[1:] if line.strip()}
        self.assertEqual(listed, EXPECTED_FILES)

    def test_empty_markdown_yields_nothing(self):
        self.assertEqual(extract(""), {})

    def test_unclosed_fence_is_not_extracted(self):
        self.assertEqual(extract("## src/a.py\n\n```python\nprint(1)\n"), {})

    def test_heading_without_code_block_is_ignored(self):
        self.assertEqual(extract("## src/a.py\n\nJust prose.\n"), {})

    def test_heading_for_a_non_file_is_ignored(self):
        self.assertEqual(extract("## Running it\n\n```bash\npytest\n```\n"), {})


class TestStatic(unittest.TestCase):
    """Checks that need nothing but the standard library."""

    @classmethod
    def setUpClass(cls):
        cls.files = extract(SCAFFOLD.read_text(encoding="utf-8"))
        cls.trees = {p: ast.parse(b, filename=p) for p, b in cls.files.items() if p.endswith(".py")}

    def _tool_decorators(self):
        """Yield (function name, helper used) for every @app.tool(**helper(...))."""
        for node in ast.walk(self.trees["src/example_server/tools.py"]):
            if not isinstance(node, ast.FunctionDef):
                continue
            for dec in node.decorator_list:
                if (isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute)
                        and dec.func.attr == "tool"):
                    helper = None
                    for kw in dec.keywords:
                        if kw.arg is None and isinstance(kw.value, ast.Call):
                            helper = getattr(kw.value.func, "id", None)
                    yield node.name, helper

    def test_every_python_file_parses(self):
        self.assertEqual(len(self.trees), 7)

    def test_pyproject_pins_the_sdk_exactly(self):
        self.assertRegex(self.files["pyproject.toml"], r'"mcp==\d+\.\d+\.\d+"')

    def test_tool_names_are_lowercase_verb_first(self):
        names = [n for n, _ in self._tool_decorators()]
        self.assertEqual(sorted(names), ["add_item", "list_items"])
        for n in names:
            self.assertRegex(n, TOOL_NAME)

    def test_every_tool_declares_its_class_through_a_helper(self):
        for name, helper in self._tool_decorators():
            self.assertIn(helper, {"read_only", "write", "destructive"}, name)

    def test_annotation_helper_sets_every_hint(self):
        src = self.files["src/example_server/tools.py"]
        for hint in ("readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint", "title"):
            self.assertIn(f"{hint}=", src)

    def test_refusals_are_tool_errors_not_plain_exceptions(self):
        """A plain exception's text never reaches the model on SDK 2.x; only ToolError's does."""
        auth = self.trees["src/example_server/auth.py"]
        bases = {n.name: [getattr(b, "id", None) for b in n.bases]
                 for n in ast.walk(auth) if isinstance(n, ast.ClassDef)}
        self.assertEqual(bases["NotAuthorised"], ["ToolError"])
        for path in ("src/example_server/tools.py", "src/example_server/auth.py"):
            for node in ast.walk(self.trees[path]):
                if isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call):
                    self.assertIn(getattr(node.exc.func, "id", None), {"ToolError", "NotAuthorised"},
                                  f"{path}:{node.lineno} raises a non-ToolError")

    def test_token_accessor_fails_closed(self):
        app = self.trees["src/example_server/app.py"]
        fn = next(n for n in ast.walk(app) if isinstance(n, ast.FunctionDef) and n.name == "token_of_request")
        returns = [n.value for n in ast.walk(fn) if isinstance(n, ast.Return)]
        self.assertTrue(returns and all(isinstance(v, ast.Constant) and v.value is None for v in returns))

    def test_no_secrets_or_internal_names(self):
        blob = "\n".join(self.files.values())
        self.assertNotRegex(blob, r"\bsk-[A-Za-z0-9_-]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----")


@unittest.skipUnless(HAS_MCP, "needs the mcp package; see the module docstring to install it")
class TestBehaviour(unittest.TestCase):
    """Runs the extracted starter for real against the installed SDK."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls._tmp.name)
        write_tree(extract(SCAFFOLD.read_text(encoding="utf-8")), cls.root)
        cls.src = str(cls.root / "src")
        sys.path.insert(0, cls.src)
        for mod in [m for m in sys.modules if m == "example_server" or m.startswith("example_server.")]:
            del sys.modules[mod]
        cls.auth = importlib.import_module("example_server.auth")
        cls.app_mod = importlib.import_module("example_server.app")

    @classmethod
    def tearDownClass(cls):
        sys.path.remove(cls.src)
        cls._tmp.cleanup()

    def _env(self):
        env = dict(os.environ)
        env["PYTHONPATH"] = self.src + os.pathsep + env.get("PYTHONPATH", "")
        return env

    @unittest.skipUnless(importlib.util.find_spec("pytest") and importlib.util.find_spec("pytest_asyncio"),
                         "needs pytest and pytest-asyncio")
    def test_starter_own_suite_passes(self):
        # The stdio test spawns `python -m example_server.app` with the SDK's minimal
        # environment, so PYTHONPATH does not reach it. Running from src/ stands in for
        # the documented `pip install -e .`: `-m` puts the working directory on sys.path.
        proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                               "-c", str(self.root / "pyproject.toml"), "--rootdir", str(self.root),
                               str(self.root / "tests")],
                              cwd=self.src, env=self._env(), capture_output=True, text=True, timeout=180)
        self.assertEqual(proc.returncode, 0, proc.stdout[-3000:] + proc.stderr[-2000:])
        self.assertRegex(proc.stdout, r"\b9 passed\b")

    # normal input
    def test_valid_token_resolves(self):
        self.assertEqual(self.auth.require_caller("demo-token"), "demo-account")

    def test_listing_has_both_tools_and_prompt(self):
        app = self.app_mod.build_app()
        tools = asyncio.run(app.list_tools())
        prompts = asyncio.run(app.list_prompts())
        self.assertEqual({t.name for t in tools}, {"list_items", "add_item"})
        self.assertEqual([p.name for p in prompts], ["get-started"])

    # broken input
    def test_missing_empty_and_unknown_tokens_all_refuse_with_one_wording(self):
        for token in (None, "", "not-a-real-token"):
            with self.assertRaises(self.auth.NotAuthorised) as ctx:
                self.auth.require_caller(token)
            self.assertEqual(str(ctx.exception), self.auth.NOT_AUTHENTICATED)

    def test_rate_limited_is_still_a_refusal(self):
        self.assertTrue(issubclass(self.auth.RateLimited, self.auth.NotAuthorised))

    def test_refusal_text_reaches_the_model_in_process(self):
        """Not signed in: the model must see the actionable wording, not a generic error."""
        from mcp.server.mcpserver.exceptions import ToolError
        app = self.app_mod.build_app()
        with self.assertRaises(ToolError) as ctx:
            asyncio.run(app.call_tool("list_items", {}))
        self.assertIn(self.auth.NOT_AUTHENTICATED, str(ctx.exception))

    # edge input
    def test_blank_title_is_refused_with_actionable_wording(self):
        from mcp.server.mcpserver.exceptions import ToolError
        tools = importlib.import_module("example_server.tools")
        app = self.app_mod.MCPServer("t")
        tools.register(app, token_of_request=lambda: "demo-token")
        with self.assertRaises(ToolError) as ctx:
            asyncio.run(app.call_tool("add_item", {"title": "   "}))
        self.assertIn("must come from the person", str(ctx.exception))
        ok = asyncio.run(app.call_tool("add_item", {"title": "  Spare key  "}))
        self.assertIn("Spare key", str(ok))
        self.assertNotIn("  Spare key  ", str(ok))

    def test_missing_argument_is_rejected_by_schema(self):
        from mcp.server.mcpserver.exceptions import ToolError
        tools = importlib.import_module("example_server.tools")
        app = self.app_mod.MCPServer("t")
        tools.register(app, token_of_request=lambda: "demo-token")
        with self.assertRaises(ToolError):
            asyncio.run(app.call_tool("add_item", {}))

    def test_transport_security_lists_the_public_host(self):
        ts = self.app_mod.transport_security(["mcp.example.com"])
        self.assertTrue(ts.enable_dns_rebinding_protection)
        self.assertEqual(ts.allowed_hosts, ["mcp.example.com"])

    def test_operator_only_names_are_hidden_but_still_registered(self):
        app_mod = self.app_mod
        original = app_mod.OPERATOR_ONLY
        try:
            app_mod.OPERATOR_ONLY = frozenset({"add_item"})
            app = app_mod.build_app()
            listed = {t.name for t in asyncio.run(app.list_tools())}
            self.assertEqual(listed, {"list_items"})
            from mcp.server.mcpserver.exceptions import ToolError
            with self.assertRaises(ToolError) as ctx:  # still gated at call time
                asyncio.run(app.call_tool("add_item", {"title": "x"}))
            self.assertIn(self.auth.NOT_AUTHENTICATED, str(ctx.exception))
        finally:
            app_mod.OPERATOR_ONLY = original


if __name__ == "__main__":
    unittest.main()

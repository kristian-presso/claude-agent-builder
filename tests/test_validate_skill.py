"""Unit tests for skills/skill-builder/scripts/validate_skill.py.

Standard library only. Run from the repository root or the plugin folder:

    python3 -m unittest discover -s plugins/agent-builder/tests -v
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
SCRIPT = PLUGIN / "skills" / "skill-builder" / "scripts" / "validate_skill.py"

_spec = importlib.util.spec_from_file_location("validate_skill", SCRIPT)
vs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vs)

GOOD_DESCRIPTION = (
    "Summarises a weekly sales CSV export into three bullet points. "
    "Use when someone asks for the weekly sales summary."
)


def skill_md(name="weekly-sales", description=GOOD_DESCRIPTION, body="# Weekly sales\n\nDo the thing.\n"):
    return f"---\nname: {name}\ndescription: {description}\n---\n\n{body}"


class SkillDirCase(unittest.TestCase):
    """Builds throwaway skill folders and runs the validator on them."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def make(self, files: dict[str, str], folder="weekly-sales", parent: Path | None = None) -> Path:
        base = (parent or self.root) / folder
        for rel, content in files.items():
            p = base / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
        base.mkdir(parents=True, exist_ok=True)
        return base

    def run_check(self, folder: Path, extra=()):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = vs.check(folder.resolve(), list(extra))
        return code, out.getvalue()


class TestSplitFrontmatter(unittest.TestCase):
    def test_simple_pairs(self):
        fields, body = vs.split_frontmatter("---\nname: a\ndescription: b c\n---\nbody\n")
        self.assertEqual(fields, {"name": "a", "description": "b c"})
        self.assertEqual(body, "body\n")

    def test_quoted_values_are_unquoted(self):
        fields, _ = vs.split_frontmatter("---\nname: 'a'\ndescription: \"b: c\"\n---\n")
        self.assertEqual(fields["name"], "a")
        self.assertEqual(fields["description"], "b: c")

    def test_folded_block_value(self):
        text = "---\nname: a\ndescription: >\n  first line\n  second line\n---\nx"
        fields, _ = vs.split_frontmatter(text)
        self.assertEqual(fields["description"], "first line second line")

    def test_crlf_line_endings_parse(self):
        fields, body = vs.split_frontmatter("---\r\nname: a\r\ndescription: b\r\n---\r\nbody\r\n")
        self.assertEqual(fields, {"name": "a", "description": "b"})
        self.assertIn("body", body)

    def test_value_containing_triple_dash_does_not_end_frontmatter(self):
        fields, _ = vs.split_frontmatter("---\nname: a\ndescription: b---c\n---\nbody")
        self.assertEqual(fields["description"], "b---c")

    def test_no_opening_fence(self):
        self.assertIsNone(vs.split_frontmatter("name: a\n---\n"))

    def test_no_closing_fence(self):
        self.assertIsNone(vs.split_frontmatter("---\nname: a\n"))

    def test_line_without_colon_is_rejected(self):
        self.assertIsNone(vs.split_frontmatter("---\nname a\n---\n"))

    def test_empty_input(self):
        self.assertIsNone(vs.split_frontmatter(""))


class TestPatterns(unittest.TestCase):
    def test_xml_tag_matches_real_tags(self):
        for s in ("<example>", "</b>", "<br/>", '<tag attr="x">'):
            self.assertTrue(vs.XML_TAG.search(s), s)

    def test_xml_tag_ignores_prose_comparisons(self):
        for s in ("under 5 MB (< 5)", "3 > 2", "a -> b", "x < y and y > z"):
            self.assertIsNone(vs.XML_TAG.search(s), s)

    def test_name_pattern(self):
        self.assertTrue(vs.NAME_PATTERN.match("weekly-sales-2"))
        for bad in ("Weekly", "weekly--sales", "-weekly", "weekly_sales", "weekly sales", ""):
            self.assertIsNone(vs.NAME_PATTERN.match(bad), bad)


class TestCheckNormal(SkillDirCase):
    def test_minimal_valid_skill_passes(self):
        folder = self.make({"SKILL.md": skill_md()})
        code, out = self.run_check(folder)
        self.assertEqual(code, 0, out)
        self.assertIn("PASSED", out)

    def test_valid_reference_link_resolves(self):
        body = "See [the guide](references/guide.md) when needed.\n"
        folder = self.make({"SKILL.md": skill_md(body=body), "references/guide.md": "# Guide\n"})
        code, out = self.run_check(folder)
        self.assertEqual(code, 0, out)
        self.assertIn("resolves", out)

    def test_external_and_anchor_links_are_ignored(self):
        body = "[docs](https://example.com) and [below](#configuration)\n"
        code, out = self.run_check(self.make({"SKILL.md": skill_md(body=body)}))
        self.assertEqual(code, 0, out)

    def test_placeholders_allowed_under_templates(self):
        folder = self.make({"SKILL.md": skill_md(), "templates/t.md": "{{NAME}} TODO\n"})
        code, out = self.run_check(folder)
        self.assertEqual(code, 0, out)

    def test_cli_exit_codes(self):
        good = self.make({"SKILL.md": skill_md()})
        bad = self.make({"SKILL.md": skill_md(name="Bad Name")}, folder="bad")
        ok = subprocess.run([sys.executable, str(SCRIPT), str(good)], capture_output=True, text=True)
        ko = subprocess.run([sys.executable, str(SCRIPT), str(bad)], capture_output=True, text=True)
        self.assertEqual(ok.returncode, 0, ok.stdout + ok.stderr)
        self.assertEqual(ko.returncode, 1, ko.stdout + ko.stderr)


class TestCheckBroken(SkillDirCase):
    def test_missing_skill_md(self):
        folder = self.make({"README.md": "x"})
        code, out = self.run_check(folder)
        self.assertEqual(code, 1)
        self.assertIn("not found", out)

    def test_no_frontmatter(self):
        code, out = self.run_check(self.make({"SKILL.md": "# Just a heading\n"}))
        self.assertEqual(code, 1)
        self.assertIn("frontmatter", out)

    def test_bad_name_and_mismatch(self):
        code, out = self.run_check(self.make({"SKILL.md": skill_md(name="My Helper")}))
        self.assertEqual(code, 1)
        self.assertIn("must be lowercase", out)
        self.assertIn("does not match the folder", out)

    def test_reserved_word_in_name(self):
        folder = self.make({"SKILL.md": skill_md(name="claude-helper")}, folder="claude-helper")
        code, out = self.run_check(folder)
        self.assertEqual(code, 1)
        self.assertIn("reserved word 'claude'", out)

    def test_name_too_long(self):
        name = "a" * 65
        code, out = self.run_check(self.make({"SKILL.md": skill_md(name=name)}, folder=name))
        self.assertEqual(code, 1)
        self.assertIn("limit is 64", out)

    def test_missing_name(self):
        text = f"---\ndescription: {GOOD_DESCRIPTION}\n---\nbody\n"
        code, out = self.run_check(self.make({"SKILL.md": text}))
        self.assertEqual(code, 1)
        self.assertIn("name is missing", out)

    def test_missing_description(self):
        code, out = self.run_check(self.make({"SKILL.md": "---\nname: weekly-sales\n---\nbody\n"}))
        self.assertEqual(code, 1)
        self.assertIn("description is missing", out)

    def test_description_too_long(self):
        desc = "Use when asked. " + "x" * 1100
        code, out = self.run_check(self.make({"SKILL.md": skill_md(description=desc)}))
        self.assertEqual(code, 1)
        self.assertIn("limit is 1024", out)

    def test_description_xml_tag(self):
        desc = "Summarises sales. <example>weekly</example> Use when asked."
        code, out = self.run_check(self.make({"SKILL.md": skill_md(description=desc)}))
        self.assertEqual(code, 1)
        self.assertIn("XML tags", out)

    def test_body_over_limit(self):
        body = "line\n" * 600
        code, out = self.run_check(self.make({"SKILL.md": skill_md(body=body)}))
        self.assertEqual(code, 1)
        self.assertIn("keep it under 500", out)

    def test_broken_link(self):
        body = "See [missing](references/nope.md).\n"
        code, out = self.run_check(self.make({"SKILL.md": skill_md(body=body)}))
        self.assertEqual(code, 1)
        self.assertIn("does not resolve", out)

    def test_link_outside_folder(self):
        body = "See [outside](../../etc/passwd).\n"
        code, out = self.run_check(self.make({"SKILL.md": skill_md(body=body)}))
        self.assertEqual(code, 1)
        self.assertIn("outside the skill folder", out)

    def test_leftover_placeholder(self):
        code, out = self.run_check(self.make({"SKILL.md": skill_md(body="Fill {{NAME}} here. TODO\n")}))
        self.assertEqual(code, 1)
        self.assertIn("leftover placeholder '{{NAME}}'", out)
        self.assertIn("leftover placeholder 'TODO'", out)

    def test_secret_detected(self):
        fake = "sk-" + "A1b2C3d4E5f6G7h8I9j0K1"  # fabricated, matches the shape only
        folder = self.make({"SKILL.md": skill_md(), "scripts/run.py": f"KEY = '{fake}'\n"})
        code, out = self.run_check(folder)
        self.assertEqual(code, 1)
        self.assertIn("looks like it contains a secret", out)

    def test_check_text_is_case_insensitive(self):
        folder = self.make({"SKILL.md": skill_md(body="Built for Example Client Ltd.\n")})
        code, out = self.run_check(folder, ["example client"])
        self.assertEqual(code, 1)
        self.assertIn("contains 'example client'", out)


class TestCheckEdge(SkillDirCase):
    def test_description_exactly_at_limit_passes(self):
        stem = "Use when asked. "
        desc = stem + "x" * (vs.DESCRIPTION_MAX - len(stem))
        self.assertEqual(len(desc), vs.DESCRIPTION_MAX)
        code, out = self.run_check(self.make({"SKILL.md": skill_md(description=desc)}))
        self.assertEqual(code, 0, out)

    def test_name_exactly_at_limit_passes(self):
        name = "a" * vs.NAME_MAX
        code, out = self.run_check(self.make({"SKILL.md": skill_md(name=name)}, folder=name))
        self.assertEqual(code, 0, out)

    def test_body_between_warn_and_fail_only_warns(self):
        body = "line\n" * 450
        code, out = self.run_check(self.make({"SKILL.md": skill_md(body=body)}))
        self.assertEqual(code, 0, out)
        self.assertIn("warn  body is", out)

    def test_lone_angle_brackets_in_description_are_allowed(self):
        desc = "Flags changes > 10% and files < 5 MB. Use when asked for the weekly summary."
        code, out = self.run_check(self.make({"SKILL.md": skill_md(description=desc)}))
        self.assertEqual(code, 0, out)

    def test_first_person_description_warns_but_passes(self):
        desc = "I can summarise sales. Use when asked for the weekly summary."
        code, out = self.run_check(self.make({"SKILL.md": skill_md(description=desc)}))
        self.assertEqual(code, 0, out)
        self.assertIn("third person", out)

    def test_description_without_use_when_warns(self):
        code, out = self.run_check(self.make({"SKILL.md": skill_md(description="Summarises sales.")}))
        self.assertEqual(code, 0, out)
        self.assertIn("does not seem to say when", out)

    def test_long_reference_without_contents_warns(self):
        folder = self.make({"SKILL.md": skill_md(), "references/big.md": "# Big\n" + "x\n" * 120})
        code, out = self.run_check(folder)
        self.assertEqual(code, 0, out)
        self.assertIn("no contents list", out)

    def test_long_reference_with_contents_does_not_warn(self):
        ref = "# Big\n\n## Contents\n\n- a\n" + "x\n" * 120
        folder = self.make({"SKILL.md": skill_md(), "references/big.md": ref})
        _, out = self.run_check(folder)
        self.assertNotIn("no contents list", out)

    def test_sibling_skill_link_warns_not_fails(self):
        skills = self.root / "skills"
        self.make({"SKILL.md": skill_md(name="other"), "references/x.md": "x"}, folder="other", parent=skills)
        body = "See [sibling](../other/references/x.md).\n"
        folder = self.make({"SKILL.md": skill_md(body=body)}, parent=skills)
        code, out = self.run_check(folder)
        self.assertEqual(code, 0, out)
        self.assertIn("sibling skill", out)

    def test_link_with_anchor_resolves(self):
        body = "See [part](references/guide.md#section).\n"
        folder = self.make({"SKILL.md": skill_md(body=body), "references/guide.md": "# Guide\n"})
        code, out = self.run_check(folder)
        self.assertEqual(code, 0, out)

    def test_non_utf8_file_does_not_crash(self):
        folder = self.make({"SKILL.md": skill_md()})
        (folder / "scripts").mkdir()
        (folder / "scripts" / "data.txt").write_bytes(b"\xff\xfe\x00bad bytes")
        code, out = self.run_check(folder)
        self.assertEqual(code, 0, out)

    def test_non_utf8_markdown_reference_does_not_crash(self):
        folder = self.make({"SKILL.md": skill_md()})
        (folder / "references").mkdir()
        (folder / "references" / "latin1.md").write_bytes("caf\xe9 notes\n".encode("latin-1"))
        code, out = self.run_check(folder)
        self.assertEqual(code, 0, out)

    def test_non_utf8_skill_md_fails_cleanly(self):
        folder = self.make({"README.md": "x"})
        (folder / "SKILL.md").write_bytes(b"---\nname: weekly-sales\ndescription: caf\xe9\n---\n")
        code, out = self.run_check(folder)
        self.assertEqual(code, 1)
        self.assertIn("not valid UTF-8", out)

    def test_crlf_skill_md_passes(self):
        folder = self.make({"README.md": "x"})
        (folder / "SKILL.md").write_bytes(skill_md().replace("\n", "\r\n").encode("utf-8"))
        code, out = self.run_check(folder)
        self.assertEqual(code, 0, out)

    def test_empty_description_value_block(self):
        text = "---\nname: weekly-sales\ndescription: >\n---\nbody\n"
        code, out = self.run_check(self.make({"SKILL.md": text}))
        self.assertEqual(code, 1)
        self.assertIn("description is missing", out)


if __name__ == "__main__":
    unittest.main()

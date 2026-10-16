# agent-builder tests

Unit tests for the scripts and starter code this plugin ships. Python `unittest` only.

| File | Covers |
| --- | --- |
| `test_validate_skill.py` | `skills/skill-builder/scripts/validate_skill.py`: normal, broken and edge skill folders. Standard library only. |
| `test_starter_scaffold.py` | The Python starter in `skills/mcp-server-builder/references/starter-scaffold.md`, extracted from the markdown exactly as a reader would copy it. |

## Run

Standard library only (the starter's behaviour tests report as skipped):

```bash
python3 -m unittest discover -s plugins/agent-builder/tests -v
```

Everything, including the starter's behaviour tests and its own pytest suite, needs the SDK
version the starter pins:

```bash
python3 -m venv .venv
.venv/bin/pip install "mcp==2.3.0" pytest pytest-asyncio
.venv/bin/python -m unittest discover -s plugins/agent-builder/tests -v
```

Run from the repository root. When the starter's pin moves, change it here too.

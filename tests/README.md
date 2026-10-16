# agent-builder tests

Unit tests for the scripts and starter code this plugin ships. Python `unittest` only.

| File | Covers |
| --- | --- |
| `test_validate_skill.py` | `skills/skill-builder/scripts/validate_skill.py`: normal, broken and edge skill folders. Standard library only. |
| `test_starter_scaffold.py` | The Python starter in `skills/mcp-server-builder/references/starter-scaffold.md`, extracted from the markdown exactly as a reader would copy it. |
| `test_mcp_operations_sql.py` | Every SQL block in `skills/mcp-operations/references/event-contract.md` and `signals.md`, run against seeded data in a real PostgreSQL. Skipped unless `PGHOST` is set. |

## Run

Standard library only (the starter's behaviour tests report as skipped):

```bash
python3 -m unittest discover -s tests -v
```

Everything, including the starter's behaviour tests and its own pytest suite, needs the SDK
version the starter pins:

```bash
python3 -m venv .venv
.venv/bin/pip install "mcp==2.3.0" pytest pytest-asyncio
.venv/bin/python -m unittest discover -s tests -v
```

The SQL tests need a PostgreSQL you can create tables in. A throwaway one:

```bash
initdb -D /tmp/pg -A trust -U pg && pg_ctl -D /tmp/pg -o "-k /tmp -p 5499" start
PGHOST=/tmp PGPORT=5499 PGUSER=pg PGDATABASE=postgres python3 -m unittest discover -s tests -p "test_mcp_operations_sql.py" -v
```

CI runs them against a PostgreSQL 16 service. Last run locally against PostgreSQL 16 on
16/10/2026.

Run from the repository root. When the starter's pin moves, change it here too.

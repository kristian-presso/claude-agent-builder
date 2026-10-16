"""Run every SQL block in the mcp-operations references against a real Postgres.

The blocks are extracted from the markdown exactly as a reader would copy them, run in
order against seeded data, and the signal queries are checked for the findings the seed
was built to produce.

Skipped unless PGHOST (and optionally PGPORT, PGUSER, PGDATABASE) point at a Postgres
you can create tables in. A throwaway one:

    initdb -D /tmp/pg -A trust -U pg && pg_ctl -D /tmp/pg -o "-k /tmp -p 5499" start
    PGHOST=/tmp PGPORT=5499 PGUSER=pg PGDATABASE=postgres python3 -m unittest ...
"""
import os
import re
import shutil
import subprocess
import unittest
from pathlib import Path

REFS = Path(__file__).resolve().parent.parent / "skills" / "mcp-operations" / "references"
SQL_BLOCK = re.compile(r"```sql\n(.*?)```", re.S)
SCHEMA = "kn_test_mcp_ops"


def blocks(name: str) -> list[str]:
    return SQL_BLOCK.findall((REFS / name).read_text(encoding="utf-8"))


def psql(sql: str) -> str:
    out = subprocess.run(
        ["psql", "-X", "-q", "-v", "ON_ERROR_STOP=1", "-At", "-F", "|", "-c",
         f"set search_path to {SCHEMA}; {sql}"],
        capture_output=True, text=True, timeout=60,
        env={**os.environ, "PGOPTIONS": ""},
    )
    if out.returncode:
        raise AssertionError(f"SQL failed:\n{sql}\n{out.stderr}")
    return out.stdout.strip()


SEED = """
insert into mcp_events (product, account_id, name, outcome, refusal_code, query, result_bytes,
                        duration_ms, access, client, server_version, created_at)
select 'demo', 'acct' || (g % 4), 'search_orders',
       case when g % 5 = 0 then 'empty' else 'ok' end, null,
       case when g % 5 = 0 then 'late refunds' else 'orders' end, 30000, 100 + g, 'read',
       'claude-ai/1.0', '1.0.0', now() - (g || ' minutes')::interval * 60
from generate_series(1, 40) g;
-- refusal loops: same tool refused twice in one flow, for 4 accounts
insert into mcp_events (product, account_id, name, outcome, refusal_code, duration_ms, access,
                        client, server_version, created_at)
select 'demo', 'loop' || a, 'refund_order', 'refused', 'amount_not_confirmed', 50, 'write',
       'claude-ai/1.0', '1.1.0', now() - interval '2 hours' + (r || ' minutes')::interval
from generate_series(1, 4) a, generate_series(1, 2) r;
-- then a successful write after 6 earlier calls in one flow
insert into mcp_events (product, account_id, name, outcome, refusal_code, duration_ms, access,
                        client, server_version, created_at)
values ('demo', 'loop1', 'refund_order', 'ok', null, 80, 'write', 'claude-ai/1.0', '1.1.0',
        now() - interval '2 hours' + interval '5 minutes'),
       ('demo', 'acct9', 'cancel_order', 'refused', 'uncoded', 40, 'write', 'claude-ai/1.0',
        '1.1.0', now() - interval '1 day'),
       ('demo', 'acct9', 'cancel_order', 'error', null, 40, 'write', 'claude-ai/1.0',
        '1.1.0', now() - interval '1 day');
"""


@unittest.skipUnless(os.environ.get("PGHOST") and shutil.which("psql"), "needs PGHOST and psql")
class TestSignalsSQL(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run(["psql", "-X", "-q", "-c", f"drop schema if exists {SCHEMA} cascade; create schema {SCHEMA};"],
                       check=True, capture_output=True)
        create = blocks("event-contract.md")[0]
        psql(create)
        psql(SEED)
        cls.signals = blocks("signals.md")
        psql(cls.signals[0])  # the flows view

    @classmethod
    def tearDownClass(cls):
        subprocess.run(["psql", "-X", "-q", "-c", f"drop schema if exists {SCHEMA} cascade;"],
                       capture_output=True)

    def test_contract_check_query_runs(self):
        out = psql(blocks("event-contract.md")[1])
        outcomes = {line.split("|")[0] for line in out.splitlines()}
        self.assertTrue(outcomes <= {"ok", "empty", "refused", "error"})

    def test_every_signal_block_runs(self):
        self.assertGreaterEqual(len(self.signals), 7)
        for sql in self.signals[1:]:
            psql(sql)

    def test_per_tool_health_counts(self):
        rows = {r.split("|")[0]: r.split("|") for r in psql(self.signals[1]).splitlines()}
        self.assertIn("refund_order", rows)
        self.assertEqual(rows["refund_order"][2], "8")  # refused count

    def test_refusal_loop_found_above_floor(self):
        out = psql(self.signals[2])
        self.assertRegex(out, r"^refund_order\|4$")

    def test_zero_hit_query_found(self):
        out = psql(self.signals[3])
        self.assertTrue(out.startswith("late refunds|"), out)

    def test_errors_by_version(self):
        versions = [r.split("|")[0] for r in psql(self.signals[4]).splitlines()]
        self.assertEqual(versions, ["1.0.0", "1.1.0"])

    def test_long_path(self):
        out = psql(self.signals[5])
        median, flows = out.split("|")
        self.assertEqual(flows, "1")
        self.assertEqual(float(median), 3.0)  # two refusals then the successful write

    def test_uncoded(self):
        self.assertEqual(psql(self.signals[6]), "cancel_order|1")


if __name__ == "__main__":
    unittest.main()

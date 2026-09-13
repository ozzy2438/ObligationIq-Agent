"""Durable, deliberately serial paid execution. No lease timeout can erase spend."""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from uuid import uuid4


class BudgetError(RuntimeError):
    pass


class UnresolvedReservation(BudgetError):
    pass


def utc_now():
    return datetime.now(timezone.utc)


class Ledger:
    def __init__(self, path: Path, daily_limit: Decimal, project_limit: Decimal):
        self.path = Path(path)
        self.daily_limit = int(daily_limit * 1_000_000)
        self.project_limit = int(project_limit * 1_000_000)
        if not 0 < self.daily_limit <= self.project_limit <= 10_000_000:
            raise BudgetError("Invalid ledger limits")
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with self.connection() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS reservations (
                    id TEXT PRIMARY KEY, day TEXT NOT NULL, reserved INTEGER NOT NULL,
                    actual INTEGER, state TEXT NOT NULL
                    CHECK (state IN ('reserved','committed','released','ambiguous'))
                );
                CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, response TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS calls (id INTEGER PRIMARY KEY, record TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS reconciliations (
                    reservation_id TEXT PRIMARY KEY, run_id TEXT NOT NULL,
                    settled INTEGER NOT NULL, reason TEXT NOT NULL
                );
            """)
            columns = {row[1] for row in db.execute("PRAGMA table_info(reservations)")}
            if "run_id" not in columns:
                db.execute("ALTER TABLE reservations ADD COLUMN run_id TEXT")
            if "model" not in columns:
                db.execute("ALTER TABLE reservations ADD COLUMN model TEXT")
        self.path.chmod(0o600)

    @contextmanager
    def connection(self):
        db = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        try:
            db.execute("PRAGMA synchronous=FULL")
            yield db
        finally:
            db.close()

    @contextmanager
    def transaction(self):
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                yield db
                db.commit()
            except BaseException:
                db.rollback()
                raise

    @staticmethod
    def _clear(db):
        if db.execute("SELECT 1 FROM reservations WHERE state IN ('reserved','ambiguous')").fetchone():
            raise UnresolvedReservation("Prior reservation is active or ambiguous; reconciliation required")

    def ensure_clear(self):
        with self.connection() as db:
            self._clear(db)

    def reserve(self, maximum: int, run_id: str | None = None, model: str | None = None) -> str:
        if type(maximum) is not int or maximum <= 0:
            raise BudgetError("Reservation must be positive integer micro-AUD")
        day = utc_now().date().isoformat()
        identifier = uuid4().hex
        with self.transaction() as db:
            self._clear(db)
            total, daily = db.execute("""
                SELECT COALESCE(SUM(actual),0),
                       COALESCE(SUM(CASE WHEN day=? THEN actual ELSE 0 END),0)
                FROM reservations WHERE state='committed'
            """, (day,)).fetchone()
            if total + maximum > self.project_limit or daily + maximum > self.daily_limit:
                raise BudgetError("Insufficient remaining daily or lifetime balance")
            db.execute("""INSERT INTO reservations
                        (id,day,reserved,actual,state,run_id,model)
                        VALUES (?,?,?,NULL,'reserved',?,?)""",
                       (identifier, day, maximum, run_id, model))
        return identifier

    def settle_ambiguous(self, identifier: str, run_id: str, record: dict):
        """Charge an ambiguous call at its maximum; never release or infer zero spend."""
        if not run_id:
            raise BudgetError("Ambiguous settlement requires a run identifier")
        with self.transaction() as db:
            row = db.execute(
                "SELECT day,reserved,state,run_id,model FROM reservations WHERE id=?", (identifier,)).fetchone()
            if not row or row[2] != "ambiguous" or row[3] not in {None, run_id}:
                raise UnresolvedReservation("Ambiguous reservation is not recoverable by this run")
            count = db.execute("SELECT COUNT(*) FROM reconciliations WHERE run_id=?", (run_id,)).fetchone()[0]
            if count >= 5:
                raise UnresolvedReservation("Ambiguous settlement limit exceeded for this run")
            total, daily = db.execute("""
                SELECT COALESCE(SUM(actual),0),
                       COALESCE(SUM(CASE WHEN day=? THEN actual ELSE 0 END),0)
                FROM reservations WHERE state='committed'
            """, (row[0],)).fetchone()
            if total + row[1] > self.project_limit or daily + row[1] > self.daily_limit:
                raise BudgetError("Ambiguous settlement would exceed a ledger limit")
            db.execute("UPDATE reservations SET actual=reserved,state='committed',run_id=? WHERE id=?",
                       (run_id, identifier))
            db.execute("INSERT INTO reconciliations VALUES (?,?,?,?)",
                       (identifier, run_id, row[1], "ambiguous_settlement"))
            record.setdefault("model", row[4])
            db.execute("INSERT INTO calls(record) VALUES (?)", (json.dumps(record),))
        return row[1]

    def recover_ambiguous(self, run_id: str):
        """Recover interrupted calls from the same run before admitting new work."""
        with self.connection() as db:
            rows = db.execute(
                "SELECT id,reserved,model FROM reservations WHERE state='ambiguous' AND run_id=? ORDER BY rowid",
                (run_id,)).fetchall()
        for identifier, maximum, model in rows:
            self.settle_ambiguous(identifier, run_id, {
                "timestamp": utc_now().isoformat(), "status": "ambiguous_settlement",
                "reason": "ambiguous_settlement", "run_id": run_id,
                "reservation_id": identifier,
                "model": model,
                "estimated_aud": str(Decimal(maximum) / Decimal(1_000_000)),
            })
        return len(rows)

    def finish(self, identifier, actual: int, key: str, response: dict, record: dict):
        if type(actual) is not int or actual < 0:
            raise BudgetError("Invalid actual cost")
        overrun = False
        with self.transaction() as db:
            row = db.execute("SELECT reserved,state FROM reservations WHERE id=?", (identifier,)).fetchone()
            if not row or row[1] != "reserved":
                raise UnresolvedReservation("Reservation cannot be settled twice or is unresolved")
            overrun = actual > row[0]
            db.execute("UPDATE reservations SET actual=?,state=? WHERE id=?",
                       (actual, "ambiguous" if overrun else "committed", identifier))
            if not overrun:
                db.execute("INSERT OR REPLACE INTO cache VALUES (?,?)", (key, json.dumps(response)))
            db.execute("INSERT INTO calls(record) VALUES (?)", (json.dumps(record),))
        if overrun:
            raise UnresolvedReservation("Actual cost exceeded reservation; reconciliation required")

    def fail(self, identifier, *, confirmed_not_sent: bool, record: dict):
        with self.transaction() as db:
            result = db.execute("UPDATE reservations SET state=? WHERE id=? AND state='reserved'",
                                ("released" if confirmed_not_sent else "ambiguous", identifier))
            if result.rowcount != 1:
                raise UnresolvedReservation("Reservation is not releasable")
            db.execute("INSERT INTO calls(record) VALUES (?)", (json.dumps(record),))

    def cached(self, key):
        with self.connection() as db:
            row = db.execute("SELECT response FROM cache WHERE key=?", (key,)).fetchone()
            return json.loads(row[0]) if row else None

    def log(self, record):
        with self.transaction() as db:
            db.execute("INSERT INTO calls(record) VALUES (?)", (json.dumps(record),))

    def summary(self):
        with self.connection() as db:
            spent, held = db.execute("""
                SELECT COALESCE(SUM(CASE WHEN state='committed' THEN actual ELSE 0 END),0),
                       COALESCE(SUM(CASE WHEN state IN ('reserved','ambiguous')
                           THEN MAX(reserved,COALESCE(actual,0)) ELSE 0 END),0)
                FROM reservations
            """).fetchone()
        return {"committed_microaud": spent, "held_microaud": held}

    def cost_summary(self):
        with self.connection() as db:
            worst, settled, held = db.execute("""
                SELECT COALESCE(SUM(CASE WHEN state='committed' THEN actual ELSE 0 END),0),
                       COALESCE((SELECT SUM(settled) FROM reconciliations),0),
                       COALESCE(SUM(CASE WHEN state IN ('reserved','ambiguous')
                           THEN MAX(reserved,COALESCE(actual,0)) ELSE 0 END),0)
                FROM reservations
            """).fetchone()
        return {"confirmed_usage_microaud": worst - settled,
                "ambiguous_settled_microaud": settled,
                "worst_case_microaud": worst, "held_microaud": held}

    def call_records(self):
        with self.connection() as db:
            return [json.loads(row[0]) for row in db.execute("SELECT record FROM calls ORDER BY id")]

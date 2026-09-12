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
            """)
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

    def reserve(self, maximum: int) -> str:
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
            db.execute("INSERT INTO reservations VALUES (?,?,?,NULL,'reserved')",
                       (identifier, day, maximum))
        return identifier

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

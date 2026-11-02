"""Dependency-free report subscription and request example, using local SQLite."""

import re
import sqlite3


AVAILABLE_REPORTS = frozenset({"daily-operations", "monthly-operations"})
USER_ID = re.compile(r"^[A-Za-z0-9_-]{1,48}$")


class ReportService:
    def __init__(self, database):
        self.connection = sqlite3.connect(str(database))
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.executescript("""
            CREATE TABLE IF NOT EXISTS subscriptions (
              id INTEGER PRIMARY KEY,
              user_id TEXT NOT NULL,
              report_code TEXT NOT NULL,
              UNIQUE(user_id, report_code)
            );
            CREATE TABLE IF NOT EXISTS report_requests (
              id INTEGER PRIMARY KEY,
              user_id TEXT NOT NULL,
              description TEXT NOT NULL,
              status TEXT NOT NULL DEFAULT 'submitted'
            );
        """)
        self.connection.commit()

    @staticmethod
    def _user(value):
        normalized = value.strip() if isinstance(value, str) else ""
        if not USER_ID.fullmatch(normalized):
            raise ValueError("user_id must contain 1-48 ASCII letters, digits, _ or -")
        return normalized

    def subscribe(self, user_id, report_code):
        user = self._user(user_id)
        code = report_code.strip().lower() if isinstance(report_code, str) else ""
        if code not in AVAILABLE_REPORTS:
            raise ValueError("report_code is not in the published catalog")
        with self.connection:
            inserted = self.connection.execute(
                "INSERT OR IGNORE INTO subscriptions (user_id, report_code) VALUES (?, ?)",
                (user, code),
            ).rowcount == 1
            number = self.connection.execute(
                "SELECT id FROM subscriptions WHERE user_id=? AND report_code=?", (user, code)
            ).fetchone()[0]
        return {"id": f"SUB-{number:04d}", "user_id": user, "report_code": code, "created": inserted}

    def subscriptions(self, user_id):
        user = self._user(user_id)
        rows = self.connection.execute(
            "SELECT report_code FROM subscriptions WHERE user_id=? ORDER BY report_code", (user,)
        ).fetchall()
        return [row[0] for row in rows]

    def request_report(self, user_id, description):
        user = self._user(user_id)
        detail = description.strip() if isinstance(description, str) else ""
        if len(detail) < 10 or len(detail) > 500:
            raise ValueError("description length must be 10-500 characters")
        with self.connection:
            number = self.connection.execute(
                "INSERT INTO report_requests (user_id, description) VALUES (?, ?)",
                (user, detail),
            ).lastrowid
        return {"id": f"REQ-{number:04d}", "status": "submitted", "user_id": user}

    def close(self):
        self.connection.close()

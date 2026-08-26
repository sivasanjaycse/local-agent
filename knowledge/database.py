"""
Knowledge Base — Module 8

Persistent, localized memory structure of the AI agent.
Uses a lightweight SQLite database to securely store:

  - Historical workflow executions (accepted & rejected)
  - Application usage frequency per intent
  - Website usage frequency per intent
  - Temporal preferences (hour-of-day / day-of-week patterns)
  - User-defined custom workflows

Provides the contextual grounding required by the Workflow
Recommendation Module (Module 4) and the Preference Learning
Module (Module 7).

Reference: Paper Section III-A, Module 8.
"""

import json
import os
import sqlite3
from datetime import datetime


class KnowledgeBase:
    """SQLite-backed knowledge base for the desktop workflow agent."""

    def __init__(self, db_path=None):
        """
        Initialize the database connection and create tables.

        Args:
            db_path: Path to the SQLite file.  Defaults to
                     ``knowledge.db`` in the project root.
        """
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "knowledge.db",
            )

        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    # ================================================================ #
    #  Schema                                                          #
    # ================================================================ #

    def _create_tables(self):
        """Create all tables if they don't already exist."""
        cursor = self.conn.cursor()

        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS workflow_history (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp        TEXT    NOT NULL,
                hour_of_day      INTEGER NOT NULL,
                day_of_week      INTEGER NOT NULL,
                intent           TEXT    NOT NULL,
                user_input       TEXT    NOT NULL,
                normalized_input TEXT    NOT NULL,
                workflow_json    TEXT    NOT NULL,
                confirmed        INTEGER NOT NULL,
                executed         INTEGER NOT NULL DEFAULT 0,
                execution_error  TEXT    DEFAULT NULL
            );

            CREATE TABLE IF NOT EXISTS app_usage (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                application   TEXT    NOT NULL,
                intent        TEXT    NOT NULL,
                use_count     INTEGER NOT NULL DEFAULT 1,
                last_used     TEXT    NOT NULL,
                UNIQUE(application, intent)
            );

            CREATE TABLE IF NOT EXISTS website_usage (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                website_name  TEXT    NOT NULL,
                website_url   TEXT    NOT NULL,
                intent        TEXT    NOT NULL,
                use_count     INTEGER NOT NULL DEFAULT 1,
                last_used     TEXT    NOT NULL,
                UNIQUE(website_name, intent)
            );

            CREATE TABLE IF NOT EXISTS temporal_preferences (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                hour_of_day   INTEGER NOT NULL,
                day_of_week   INTEGER NOT NULL,
                intent        TEXT    NOT NULL,
                frequency     INTEGER NOT NULL DEFAULT 1,
                UNIQUE(hour_of_day, day_of_week, intent)
            );

            CREATE TABLE IF NOT EXISTS custom_workflows (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT    NOT NULL UNIQUE,
                intent        TEXT    NOT NULL,
                workflow_json TEXT    NOT NULL,
                created_at    TEXT    NOT NULL,
                last_used     TEXT
            );
        """)

        self.conn.commit()

    # ================================================================ #
    #  Write operations                                                #
    # ================================================================ #

    def log_workflow(
        self,
        intent,
        user_input,
        normalized_input,
        workflow,
        confirmed,
        executed=False,
        error=None,
    ):
        """
        Record a complete workflow interaction event.

        Called at the end of every pipeline run — whether the user
        accepted, rejected, or the execution failed.
        """
        now = datetime.now()

        self.conn.execute(
            """
            INSERT INTO workflow_history
                (timestamp, hour_of_day, day_of_week, intent,
                 user_input, normalized_input, workflow_json,
                 confirmed, executed, execution_error)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                now.isoformat(),
                now.hour,
                now.weekday(),
                intent,
                user_input,
                normalized_input,
                json.dumps(workflow),
                1 if confirmed else 0,
                1 if executed else 0,
                error,
            ),
        )

        self.conn.commit()

    def update_app_usage(self, application, intent):
        """Increment (or insert) the usage counter for an application."""
        now = datetime.now().isoformat()

        self.conn.execute(
            """
            INSERT INTO app_usage (application, intent, use_count, last_used)
            VALUES (?, ?, 1, ?)
            ON CONFLICT(application, intent)
            DO UPDATE SET
                use_count = use_count + 1,
                last_used = excluded.last_used
            """,
            (application, intent, now),
        )

        self.conn.commit()

    def update_website_usage(self, website_name, website_url, intent):
        """Increment (or insert) the usage counter for a website."""
        now = datetime.now().isoformat()

        self.conn.execute(
            """
            INSERT INTO website_usage
                (website_name, website_url, intent, use_count, last_used)
            VALUES (?, ?, ?, 1, ?)
            ON CONFLICT(website_name, intent)
            DO UPDATE SET
                use_count  = use_count + 1,
                last_used  = excluded.last_used,
                website_url = excluded.website_url
            """,
            (website_name, website_url, intent, now),
        )

        self.conn.commit()

    def update_temporal_preference(self, intent):
        """Record current time-of-day/day-of-week for this intent."""
        now = datetime.now()

        self.conn.execute(
            """
            INSERT INTO temporal_preferences
                (hour_of_day, day_of_week, intent, frequency)
            VALUES (?, ?, ?, 1)
            ON CONFLICT(hour_of_day, day_of_week, intent)
            DO UPDATE SET frequency = frequency + 1
            """,
            (now.hour, now.weekday(), intent),
        )

        self.conn.commit()

    def save_custom_workflow(self, name, intent, workflow):
        """Save a user-defined custom workflow."""
        now = datetime.now().isoformat()

        self.conn.execute(
            """
            INSERT INTO custom_workflows
                (name, intent, workflow_json, created_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(name)
            DO UPDATE SET
                intent        = excluded.intent,
                workflow_json = excluded.workflow_json,
                created_at    = excluded.created_at
            """,
            (name, intent, json.dumps(workflow), now),
        )

        self.conn.commit()

    # ================================================================ #
    #  Read operations                                                 #
    # ================================================================ #

    def get_top_apps(self, intent, limit=5):
        """
        Return the most-used applications for a given intent,
        ordered by usage count descending.

        Returns:
            list[dict] with keys: application, use_count, last_used
        """
        rows = self.conn.execute(
            """
            SELECT application, use_count, last_used
            FROM app_usage
            WHERE intent = ?
            ORDER BY use_count DESC
            LIMIT ?
            """,
            (intent, limit),
        ).fetchall()

        return [dict(row) for row in rows]

    def get_top_websites(self, intent, limit=5):
        """
        Return the most-used websites for a given intent,
        ordered by usage count descending.

        Returns:
            list[dict] with keys: website_name, website_url,
                                  use_count, last_used
        """
        rows = self.conn.execute(
            """
            SELECT website_name, website_url, use_count, last_used
            FROM website_usage
            WHERE intent = ?
            ORDER BY use_count DESC
            LIMIT ?
            """,
            (intent, limit),
        ).fetchall()

        return [dict(row) for row in rows]

    def get_temporal_intents(self, hour=None, day=None):
        """
        Return the most frequent intents for a given time window.

        Args:
            hour: Hour of day (0-23). Defaults to current hour.
            day:  Day of week (0=Mon). Defaults to current day.

        Returns:
            list[dict] with keys: intent, frequency
        """
        now = datetime.now()
        if hour is None:
            hour = now.hour
        if day is None:
            day = now.weekday()

        rows = self.conn.execute(
            """
            SELECT intent, frequency
            FROM temporal_preferences
            WHERE hour_of_day = ? AND day_of_week = ?
            ORDER BY frequency DESC
            """,
            (hour, day),
        ).fetchall()

        return [dict(row) for row in rows]

    def get_recent_history(self, limit=20):
        """
        Return the most recent workflow history entries.

        Returns:
            list[dict] with all workflow_history columns.
        """
        rows = self.conn.execute(
            """
            SELECT * FROM workflow_history
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

        return [dict(row) for row in rows]

    def get_custom_workflow(self, name):
        """Look up a custom workflow by name."""
        row = self.conn.execute(
            """
            SELECT * FROM custom_workflows
            WHERE name = ?
            """,
            (name,),
        ).fetchone()

        if row:
            result = dict(row)
            result["workflow_json"] = json.loads(result["workflow_json"])
            return result

        return None

    # ================================================================ #
    #  Metrics helpers                                                 #
    # ================================================================ #

    def get_workflow_acceptance_rate(self):
        """
        WAR metric: ratio of accepted workflows to total recommended.

        Returns:
            dict with keys: accepted, total, rate (0.0 – 1.0)
        """
        row = self.conn.execute(
            """
            SELECT
                COUNT(*)                    AS total,
                SUM(CASE WHEN confirmed = 1 THEN 1 ELSE 0 END) AS accepted
            FROM workflow_history
            """
        ).fetchone()

        total = row["total"] or 0
        accepted = row["accepted"] or 0

        return {
            "accepted": accepted,
            "total": total,
            "rate": accepted / total if total > 0 else 0.0,
        }

    def get_execution_reliability(self):
        """
        ER metric: ratio of successful executions to total executed.

        Returns:
            dict with keys: successful, total_executed, rate (0.0 – 1.0)
        """
        row = self.conn.execute(
            """
            SELECT
                COUNT(*)                   AS total_executed,
                SUM(CASE WHEN execution_error IS NULL THEN 1 ELSE 0 END) AS successful
            FROM workflow_history
            WHERE confirmed = 1 AND executed = 1
            """
        ).fetchone()

        total = row["total_executed"] or 0
        successful = row["successful"] or 0

        return {
            "successful": successful,
            "total_executed": total,
            "rate": successful / total if total > 0 else 0.0,
        }

    # ================================================================ #
    #  Cleanup                                                         #
    # ================================================================ #

    def close(self):
        """Close the database connection."""
        self.conn.close()

"""SQLite persistence for measurements, alerts and alert status history."""

import os
import sqlite3
from contextlib import closing
from pathlib import Path
from datetime import datetime, timezone


DEFAULT_DB_PATH = (
    Path(__file__).resolve().parents[2] / "data" / "moon_alerts.sqlite3"
)
DB_PATH = Path(os.getenv("MOON_ALERT_DB", str(DEFAULT_DB_PATH)))


def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(DB_PATH), timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _now():
    return datetime.now(timezone.utc).isoformat()


def _alert_dict(row):
    if row is None:
        return None
    result = dict(row)
    result["is_demo"] = bool(result["is_demo"])
    return result


def init_db():
    with closing(_connect()) as connection:
        with connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS measurements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    simulation_id TEXT NOT NULL,
                    observation_day INTEGER,
                    indicator TEXT NOT NULL,
                    measurement_type TEXT NOT NULL,
                    value REAL NOT NULL,
                    unit TEXT NOT NULL,
                    measured_at TEXT NOT NULL,
                    source TEXT NOT NULL,
                    provenance_json TEXT
                );

                CREATE INDEX IF NOT EXISTS idx_measurements_series
                ON measurements(simulation_id, indicator, source, measured_at);

                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    simulation_id TEXT NOT NULL,
                    rule_id TEXT NOT NULL,
                    measurement_id INTEGER NOT NULL,
                    indicator TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active',
                    value REAL NOT NULL,
                    unit TEXT NOT NULL,
                    measured_at TEXT NOT NULL,
                    source TEXT NOT NULL,
                    explanation TEXT NOT NULL,
                    reference TEXT NOT NULL,
                    is_demo INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    acknowledged_at TEXT,
                    resolved_at TEXT,
                    UNIQUE(simulation_id, rule_id),
                    FOREIGN KEY(measurement_id) REFERENCES measurements(id)
                );

                CREATE INDEX IF NOT EXISTS idx_alerts_status
                ON alerts(status, created_at);

                CREATE TABLE IF NOT EXISTS alert_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_id INTEGER NOT NULL,
                    previous_status TEXT,
                    new_status TEXT NOT NULL,
                    changed_at TEXT NOT NULL,
                    note TEXT,
                    FOREIGN KEY(alert_id) REFERENCES alerts(id) ON DELETE CASCADE
                );
                """
            )


def record_measurement(
    *,
    simulation_id,
    observation_day,
    indicator,
    measurement_type,
    value,
    unit,
    measured_at,
    source,
    provenance_json,
):
    with closing(_connect()) as connection:
        with connection:
            cursor = connection.execute(
                """
                INSERT INTO measurements (
                    simulation_id, observation_day, indicator,
                    measurement_type, value, unit, measured_at,
                    source, provenance_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(simulation_id), observation_day, indicator,
                    measurement_type, float(value), unit, measured_at,
                    source, provenance_json,
                ),
            )
            return cursor.lastrowid


def get_recent_values(simulation_id, indicator, source, limit):
    with closing(_connect()) as connection:
        rows = connection.execute(
            """
            SELECT value FROM measurements
            WHERE simulation_id = ? AND indicator = ? AND source = ?
            ORDER BY measured_at DESC, id DESC
            LIMIT ?
            """,
            (str(simulation_id), indicator, source, limit),
        ).fetchall()
        return [float(row["value"]) for row in rows]


def create_alert(
    *,
    simulation_id,
    rule_id,
    measurement_id,
    indicator,
    severity,
    value,
    unit,
    measured_at,
    source,
    explanation,
    reference,
    is_demo,
):
    with closing(_connect()) as connection:
        with connection:
            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO alerts (
                    simulation_id, rule_id, measurement_id, indicator,
                    severity, status, value, unit, measured_at, source,
                    explanation, reference, is_demo, created_at
                ) VALUES (?, ?, ?, ?, ?, 'active', ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(simulation_id), rule_id, measurement_id, indicator,
                    severity, float(value), unit, measured_at, source,
                    explanation, reference, int(is_demo), _now(),
                ),
            )
            row = connection.execute(
                "SELECT * FROM alerts WHERE simulation_id = ? AND rule_id = ?",
                (str(simulation_id), rule_id),
            ).fetchone()

            if cursor.rowcount == 1:
                connection.execute(
                    """
                    INSERT INTO alert_events (
                        alert_id, previous_status, new_status, changed_at, note
                    ) VALUES (?, NULL, 'active', ?, 'Alert created')
                    """,
                    (row["id"], _now()),
                )

            return _alert_dict(row)


def list_alerts(status=None, simulation_id=None):
    query = "SELECT * FROM alerts WHERE 1 = 1"
    parameters = []

    if status is not None:
        query += " AND status = ?"
        parameters.append(status)

    if simulation_id is not None:
        query += " AND simulation_id = ?"
        parameters.append(str(simulation_id))

    query += " ORDER BY created_at DESC, id DESC"

    with closing(_connect()) as connection:
        rows = connection.execute(query, parameters).fetchall()
        return [_alert_dict(row) for row in rows]


def get_alert(alert_id):
    with closing(_connect()) as connection:
        row = connection.execute(
            "SELECT * FROM alerts WHERE id = ?", (alert_id,)
        ).fetchone()
        return _alert_dict(row)


def update_alert_status(alert_id, new_status, note=None):
    allowed = {
        "active": {"acknowledged", "resolved"},
        "acknowledged": {"resolved"},
        "resolved": set(),
    }

    with closing(_connect()) as connection:
        with connection:
            row = connection.execute(
                "SELECT * FROM alerts WHERE id = ?", (alert_id,)
            ).fetchone()

            if row is None:
                return None

            current_status = row["status"]

            if current_status == new_status:
                return _alert_dict(row)

            if new_status not in allowed[current_status]:
                raise ValueError(
                    f"Invalid alert transition: {current_status} -> {new_status}."
                )

            now = _now()
            acknowledged_at = row["acknowledged_at"]
            resolved_at = row["resolved_at"]

            if new_status == "acknowledged":
                acknowledged_at = now
            elif new_status == "resolved":
                resolved_at = now

            connection.execute(
                """
                UPDATE alerts
                SET status = ?, acknowledged_at = ?, resolved_at = ?
                WHERE id = ?
                """,
                (new_status, acknowledged_at, resolved_at, alert_id),
            )

            connection.execute(
                """
                INSERT INTO alert_events (
                    alert_id, previous_status, new_status, changed_at, note
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (alert_id, current_status, new_status, now, note),
            )

            updated = connection.execute(
                "SELECT * FROM alerts WHERE id = ?", (alert_id,)
            ).fetchone()
            return _alert_dict(updated)


def list_alert_events(alert_id):
    with closing(_connect()) as connection:
        rows = connection.execute(
            """
            SELECT * FROM alert_events
            WHERE alert_id = ?
            ORDER BY changed_at ASC, id ASC
            """,
            (alert_id,),
        ).fetchall()
        return [dict(row) for row in rows]

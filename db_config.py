"""
db_config.py — database connection factory.

Supports two backends selected via the DB_BACKEND environment variable
(or .env file):

    DB_BACKEND=sqlite   (default — zero setup, ships with Python)
    DB_BACKEND=mysql    (requires a running MySQL server)

All credentials are loaded from .env so they are never hardcoded here.
"""

import os
import sqlite3
import logging
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the project root (same directory as this file)
_ENV_PATH = Path(__file__).parent / ".env"
load_dotenv(_ENV_PATH)

logger = logging.getLogger(__name__)

# ── backend selection ────────────────────────────────────────────────────────
DB_BACKEND = os.getenv("DB_BACKEND", "sqlite").lower()

# ── SQLite config ────────────────────────────────────────────────────────────
_SQLITE_PATH = Path(__file__).parent / os.getenv("SQLITE_PATH", "atm.db")

# ── MySQL config (only used when DB_BACKEND=mysql) ───────────────────────────
_MYSQL_CONFIG = {
    "host":     os.getenv("MYSQL_HOST",     "localhost"),
    "user":     os.getenv("MYSQL_USER",     "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "atm"),
}


# ── Schema DDL ───────────────────────────────────────────────────────────────
_DDL_USERS = """
CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name   VARCHAR(100),
    father_name VARCHAR(100),
    email       VARCHAR(100),
    address     VARCHAR(200),
    city        VARCHAR(50),
    province    VARCHAR(50),
    pin_code    VARCHAR(10),
    cnic        VARCHAR(20),
    card_number VARCHAR(20) UNIQUE,
    pin_hash    VARCHAR(64),
    balance     DECIMAL(12,2) DEFAULT 0,
    is_blocked  INTEGER DEFAULT 0
)
"""

_DDL_TRANSACTIONS = """
CREATE TABLE IF NOT EXISTS transactions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    card_number VARCHAR(20),
    type        VARCHAR(20),
    amount      DECIMAL(12,2),
    date        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""


def get_db_connection():
    """
    Return an open database connection for the configured backend.
    Returns None and logs an error if the connection fails.
    """
    if DB_BACKEND == "sqlite":
        try:
            conn = sqlite3.connect(str(_SQLITE_PATH))
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            return conn
        except Exception as exc:
            logger.error("SQLite connection failed: %s", exc)
            _show_db_error(str(exc))
            return None

    elif DB_BACKEND == "mysql":
        try:
            import mysql.connector
            conn = mysql.connector.connect(**_MYSQL_CONFIG)
            return conn
        except Exception as exc:
            logger.error("MySQL connection failed: %s", exc)
            _show_db_error(str(exc))
            return None

    else:
        msg = f"Unknown DB_BACKEND '{DB_BACKEND}'. Set DB_BACKEND=sqlite or mysql in .env"
        logger.error(msg)
        _show_db_error(msg)
        return None


def init_database():
    """Create tables if they do not already exist."""
    conn = get_db_connection()
    if conn is None:
        return

    try:
        cur = conn.cursor()
        if DB_BACKEND == "sqlite":
            cur.execute(_DDL_USERS)
            cur.execute(_DDL_TRANSACTIONS)
            conn.commit()
        else:
            cur.execute(_DDL_USERS.replace("AUTOINCREMENT", "AUTO_INCREMENT"))
            cur.execute(_DDL_TRANSACTIONS.replace("AUTOINCREMENT", "AUTO_INCREMENT"))
            conn.commit()
        logger.info("Database initialised successfully (%s)", DB_BACKEND)
    except Exception as exc:
        logger.error("Error initialising database: %s", exc)
    finally:
        conn.close()


def _show_db_error(message: str):
    """Show a Tkinter error dialog without crashing if Tk is unavailable."""
    try:
        import tkinter.messagebox as mb
        mb.showerror("Database Error", f"Failed to connect to database:\n{message}")
    except Exception:
        print(f"[DB ERROR] {message}")

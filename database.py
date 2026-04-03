"""
database.py — all CRUD operations for the ATM simulator.

PIN security
------------
PINs are NEVER stored or compared as plain text.
bcrypt is used: create_user() hashes before insert,
verify_login() uses bcrypt.checkpw(), update_pin() hashes before update.

Backend compatibility
---------------------
Works with both SQLite (default) and MySQL via db_config.get_db_connection().
Parameter placeholders differ (%s for MySQL, ? for SQLite) — a small helper
_ph() selects the right one at runtime.
"""

import random
import logging
import bcrypt

from db_config import get_db_connection, DB_BACKEND

logger = logging.getLogger(__name__)


# ── placeholder helper ───────────────────────────────────────────────────────
def _ph():
    """Return the correct parameter placeholder for the active backend."""
    return "%s" if DB_BACKEND == "mysql" else "?"


# ── PIN hashing helpers ──────────────────────────────────────────────────────
def hash_pin(plain_pin: str) -> str:
    """Return a bcrypt hash of the 4-digit PIN."""
    return bcrypt.hashpw(plain_pin.encode(), bcrypt.gensalt()).decode()


def verify_pin(plain_pin: str, stored_hash: str) -> bool:
    """Return True if plain_pin matches the stored bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_pin.encode(), stored_hash.encode())
    except Exception as exc:
        logger.error("PIN verification error: %s", exc)
        return False


# ── card / PIN generation ─────────────────────────────────────────────────────
def generate_card_details():
    """Generate a random 16-digit card number and 4-digit PIN."""
    card_no = "".join(str(random.randint(0, 9)) for _ in range(16))
    formatted = " ".join(card_no[i:i+4] for i in range(0, 16, 4))
    pin = "".join(str(random.randint(0, 9)) for _ in range(4))
    return formatted, pin


# ── row-to-dict helper ────────────────────────────────────────────────────────
def _row_to_dict(row):
    """Convert a sqlite3.Row or mysql dict-cursor row to a plain dict."""
    if row is None:
        return None
    if isinstance(row, dict):
        return dict(row)
    return dict(zip(row.keys(), tuple(row)))


# ── user operations ───────────────────────────────────────────────────────────
def create_user(user_data: dict):
    """
    Insert a new user.  Returns (True, (formatted_card, plain_pin)) on
    success, or (False, error_message) on failure.
    """
    conn = get_db_connection()
    if not conn:
        return False, "Database connection failed"

    try:
        cur = conn.cursor()
        p = _ph()

        # Find a unique card number
        while True:
            formatted_card, plain_pin = generate_card_details()
            card_db = formatted_card.replace(" ", "")
            cur.execute(f"SELECT id FROM users WHERE card_number = {p}", (card_db,))
            if not cur.fetchone():
                break

        pin_hash = hash_pin(plain_pin)

        query = f"""
            INSERT INTO users (
                full_name, father_name, email, address, city, province,
                pin_code, cnic, card_number, pin_hash, balance
            ) VALUES ({p},{p},{p},{p},{p},{p},{p},{p},{p},{p},{p})
        """
        values = (
            user_data["full_name"],
            user_data["father_name"],
            user_data["email"],
            user_data["address"],
            user_data["city"],
            user_data["province"],
            user_data["pin_code"],
            user_data["cnic"],
            card_db,
            pin_hash,
            0.00,
        )
        cur.execute(query, values)
        conn.commit()
        return True, (formatted_card, plain_pin)

    except Exception as exc:
        logger.error("create_user error: %s", exc)
        return False, f"Database error: {exc}"
    finally:
        conn.close()


def verify_login(card_number: str, plain_pin: str):
    """
    Verify login credentials.
    Returns (True, user_dict) on success, or (False, error_message) on failure.
    Respects the is_blocked flag — blocked cards are always rejected.
    """
    conn = get_db_connection()
    if not conn:
        return False, "Database connection failed"

    try:
        cur = conn.cursor()
        p = _ph()
        card_db = card_number.replace(" ", "")

        cur.execute(
            f"SELECT * FROM users WHERE card_number = {p}",
            (card_db,)
        )
        row = cur.fetchone()

        if not row:
            return False, "Invalid card number or PIN"

        user = _row_to_dict(row)

        if user.get("is_blocked"):
            return False, "This card has been blocked due to too many failed attempts"

        if not verify_pin(plain_pin, user.get("pin_hash", "")):
            return False, "Invalid card number or PIN"

        return True, user

    except Exception as exc:
        logger.error("verify_login error: %s", exc)
        return False, f"Database error: {exc}"
    finally:
        conn.close()


def block_card(card_number: str) -> bool:
    """Permanently block a card in the database."""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        p = _ph()
        card_db = card_number.replace(" ", "")
        cur.execute(f"UPDATE users SET is_blocked = 1 WHERE card_number = {p}", (card_db,))
        conn.commit()
        logger.warning("Card blocked: %s", card_db)
        return True
    except Exception as exc:
        logger.error("block_card error: %s", exc)
        return False
    finally:
        conn.close()


def get_user_by_card(card_number: str):
    """Return a user dict for the given card number, or None."""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor()
        p = _ph()
        card_db = card_number.replace(" ", "")
        cur.execute(f"SELECT * FROM users WHERE card_number = {p}", (card_db,))
        return _row_to_dict(cur.fetchone())
    except Exception as exc:
        logger.error("get_user_by_card error: %s", exc)
        return None
    finally:
        conn.close()


def update_balance(card_number: str, new_balance: float) -> bool:
    """Update the balance for a given card."""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        p = _ph()
        card_db = card_number.replace(" ", "")
        cur.execute(
            f"UPDATE users SET balance = {p} WHERE card_number = {p}",
            (new_balance, card_db)
        )
        conn.commit()
        return True
    except Exception as exc:
        logger.error("update_balance error: %s", exc)
        return False
    finally:
        conn.close()


def add_transaction(card_number: str, trans_type: str, amount: float) -> bool:
    """Record a transaction."""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        p = _ph()
        card_db = card_number.replace(" ", "")
        cur.execute(
            f"INSERT INTO transactions (card_number, type, amount) VALUES ({p},{p},{p})",
            (card_db, trans_type, amount)
        )
        conn.commit()
        return True
    except Exception as exc:
        logger.error("add_transaction error: %s", exc)
        return False
    finally:
        conn.close()


def get_transactions(card_number: str, limit: int = 10) -> list:
    """Return the most recent transactions for a card (newest first)."""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        p = _ph()
        card_db = card_number.replace(" ", "")
        cur.execute(
            f"""SELECT * FROM transactions
                WHERE card_number = {p}
                ORDER BY date DESC
                LIMIT {p}""",
            (card_db, limit)
        )
        return [_row_to_dict(r) for r in cur.fetchall()]
    except Exception as exc:
        logger.error("get_transactions error: %s", exc)
        return []
    finally:
        conn.close()


def update_pin(card_number: str, new_plain_pin: str) -> bool:
    """Hash new_plain_pin and store the hash."""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        p = _ph()
        card_db = card_number.replace(" ", "")
        new_hash = hash_pin(new_plain_pin)
        cur.execute(
            f"UPDATE users SET pin_hash = {p} WHERE card_number = {p}",
            (new_hash, card_db)
        )
        conn.commit()
        return True
    except Exception as exc:
        logger.error("update_pin error: %s", exc)
        return False
    finally:
        conn.close()

import sqlite3
from datetime import datetime, timedelta
import hashlib
import hmac
import os
import secrets

_DB_PATH = "history.db"
_PWD_ITERATIONS = 200_000
_RESET_CODE_ITERATIONS = 120_000
_RESET_CODE_TTL_MINUTES = 10
_RESET_MAX_ATTEMPTS = 5

def _utc_now_str():
    return datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S")

def _hash_password(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PWD_ITERATIONS)

def _hash_reset_code(code: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", code.encode("utf-8"), salt, _RESET_CODE_ITERATIONS)

def init_db():
    conn = sqlite3.connect(_DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS summary_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            method TEXT,
            original_length INTEGER,
            summary_length INTEGER,
            process_time REAL,
            original_text TEXT,
            summary_text TEXT,
            novelty_score REAL,
            rouge_l_score REAL
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            email TEXT,
            password_salt TEXT NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS password_reset_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            code_salt TEXT NOT NULL,
            code_hash TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            attempts INTEGER NOT NULL DEFAULT 0,
            used INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

def save_summary(method, orig_len, sum_len, p_time, orig_text, sum_text, novelty=0.0, rouge_l=0.0):
    conn = sqlite3.connect(_DB_PATH)
    c = conn.cursor()
    date_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    c.execute('''
        INSERT INTO summary_history 
        (created_at, method, original_length, summary_length, process_time, original_text, summary_text, novelty_score, rouge_l_score) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (date_str, method, orig_len, sum_len, p_time, orig_text, sum_text, novelty, rouge_l))
    conn.commit()
    conn.close()

def get_history():
    conn = sqlite3.connect(_DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM summary_history ORDER BY id DESC LIMIT 50")
    rows = c.fetchall()
    conn.close()
    return rows

def create_user(username: str, password: str, email: str | None = None):
    username = (username or "").strip()
    email = (email or "").strip() or None
    if not username or not password:
        return False, "Thiếu username hoặc password."

    salt = os.urandom(16)
    pwd_hash = _hash_password(password, salt)

    try:
        conn = sqlite3.connect(_DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO users (created_at, username, email, password_salt, password_hash) VALUES (?, ?, ?, ?, ?)",
            (_utc_now_str(), username, email, salt.hex(), pwd_hash.hex()),
        )
        conn.commit()
        return True, "Đăng ký thành công."
    except sqlite3.IntegrityError:
        return False, "Username đã tồn tại."
    finally:
        try:
            conn.close()
        except Exception:
            pass

def authenticate_user(username: str, password: str):
    username = (username or "").strip()
    if not username or not password:
        return False, None, "Thiếu username hoặc password."

    conn = sqlite3.connect(_DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, username, email, password_salt, password_hash FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()

    if not row:
        return False, None, "Sai username hoặc password."

    user_id, uname, email, salt_hex, hash_hex = row
    salt = bytes.fromhex(salt_hex)
    expected = bytes.fromhex(hash_hex)
    actual = _hash_password(password, salt)

    if not hmac.compare_digest(expected, actual):
        return False, None, "Sai username hoặc password."

    return True, {"id": user_id, "username": uname, "email": email}, "Đăng nhập thành công."

def _get_user_by_identifier(identifier: str):
    identifier = (identifier or "").strip()
    if not identifier:
        return None

    conn = sqlite3.connect(_DB_PATH)
    c = conn.cursor()
    if "@" in identifier:
        c.execute("SELECT id, username, email FROM users WHERE email = ?", (identifier,))
    else:
        c.execute("SELECT id, username, email FROM users WHERE username = ?", (identifier,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    user_id, username, email = row
    return {"id": user_id, "username": username, "email": email}

def create_password_reset_code(identifier: str):
    """
    Create a one-time reset code for a user (by username or email).
    Returns: (ok: bool, email: str|None, msg: str)
    """
    user = _get_user_by_identifier(identifier)
    if not user:
        # Don't reveal whether user exists
        return False, None, "Nếu tài khoản tồn tại và có email, hệ thống sẽ gửi mã đặt lại mật khẩu."

    email = (user.get("email") or "").strip()
    if not email:
        return False, None, "Tài khoản này chưa có email nên không thể đặt lại mật khẩu."

    code = f"{secrets.randbelow(1_000_000):06d}"
    salt = os.urandom(16)
    code_hash = _hash_reset_code(code, salt)

    now = datetime.utcnow()
    expires = now + timedelta(minutes=_RESET_CODE_TTL_MINUTES)

    conn = sqlite3.connect(_DB_PATH)
    c = conn.cursor()
    # Invalidate previous unused codes for this user
    c.execute("UPDATE password_reset_codes SET used = 1 WHERE user_id = ? AND used = 0", (user["id"],))
    c.execute(
        "INSERT INTO password_reset_codes (created_at, user_id, code_salt, code_hash, expires_at, attempts, used) VALUES (?, ?, ?, ?, ?, 0, 0)",
        (_utc_now_str(), user["id"], salt.hex(), code_hash.hex(), expires.isoformat()),
    )
    conn.commit()
    conn.close()

    return True, email, code

def reset_password_with_code(identifier: str, code: str, new_password: str):
    """
    Verify reset code and update password.
    Returns: (ok: bool, msg: str)
    """
    user = _get_user_by_identifier(identifier)
    if not user:
        return False, "Mã không hợp lệ hoặc đã hết hạn."

    code = (code or "").strip()
    if not code or not new_password:
        return False, "Thiếu mã hoặc mật khẩu mới."
    if len(new_password) < 6:
        return False, "Password tối thiểu 6 ký tự."

    conn = sqlite3.connect(_DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        SELECT id, code_salt, code_hash, expires_at, attempts, used
        FROM password_reset_codes
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (user["id"],),
    )
    row = c.fetchone()
    if not row:
        conn.close()
        return False, "Mã không hợp lệ hoặc đã hết hạn."

    reset_id, salt_hex, hash_hex, expires_at, attempts, used = row
    if used:
        conn.close()
        return False, "Mã không hợp lệ hoặc đã hết hạn."

    try:
        expires_dt = datetime.fromisoformat(expires_at)
    except Exception:
        expires_dt = datetime.utcnow() - timedelta(days=1)

    if datetime.utcnow() > expires_dt:
        c.execute("UPDATE password_reset_codes SET used = 1 WHERE id = ?", (reset_id,))
        conn.commit()
        conn.close()
        return False, "Mã không hợp lệ hoặc đã hết hạn."

    if attempts >= _RESET_MAX_ATTEMPTS:
        c.execute("UPDATE password_reset_codes SET used = 1 WHERE id = ?", (reset_id,))
        conn.commit()
        conn.close()
        return False, "Bạn đã nhập sai quá nhiều lần. Vui lòng yêu cầu mã mới."

    salt = bytes.fromhex(salt_hex)
    expected = bytes.fromhex(hash_hex)
    actual = _hash_reset_code(code, salt)
    if not hmac.compare_digest(expected, actual):
        c.execute("UPDATE password_reset_codes SET attempts = attempts + 1 WHERE id = ?", (reset_id,))
        conn.commit()
        conn.close()
        return False, "Mã không hợp lệ hoặc đã hết hạn."

    # Update password
    pwd_salt = os.urandom(16)
    pwd_hash = _hash_password(new_password, pwd_salt)
    c.execute(
        "UPDATE users SET password_salt = ?, password_hash = ? WHERE id = ?",
        (pwd_salt.hex(), pwd_hash.hex(), user["id"]),
    )
    c.execute("UPDATE password_reset_codes SET used = 1 WHERE id = ?", (reset_id,))
    conn.commit()
    conn.close()
    return True, "Đổi mật khẩu thành công. Bạn có thể đăng nhập lại."

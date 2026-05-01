import sqlite3
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
DB_PATH = 'auth.db'

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        with open('schema.sql', 'r') as f:
            conn.executescript(f.read())
        conn.commit()

def seed_admin():
    with get_connection() as conn:
        admin = conn.execute("SELECT * FROM users WHERE email = 'admin@gmail.com'").fetchone()
        if not admin:
            pw_hash = bcrypt.generate_password_hash('Admin@1234').decode('utf-8')
            conn.execute(
                "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
                ('admin', 'admin@gmail.com', pw_hash, 'admin')
            )
            conn.commit()

def register_user(username, email, password, role):
    try:
        pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        with get_connection() as conn:
            cur = conn.execute(
                "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
                (username, email, pw_hash, role)
            )
            conn.commit()
            return True, cur.lastrowid
    except sqlite3.IntegrityError:
        return False, "Username or email already exists."

def verify_login(email, password):
    with get_connection() as conn:
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if user and bcrypt.check_password_hash(user['password_hash'], password):
            conn.execute("UPDATE users SET last_login = datetime('now') WHERE id = ?", (user['id'],))
            conn.commit()
            return dict(user)
    return None
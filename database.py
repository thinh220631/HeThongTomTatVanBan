import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('history.db')
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
    conn.commit()
    conn.close()

def save_summary(method, orig_len, sum_len, p_time, orig_text, sum_text, novelty=0.0, rouge_l=0.0):
    conn = sqlite3.connect('history.db')
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
    conn = sqlite3.connect('history.db')
    c = conn.cursor()
    c.execute("SELECT * FROM summary_history ORDER BY id DESC LIMIT 50")
    rows = c.fetchall()
    conn.close()
    return rows
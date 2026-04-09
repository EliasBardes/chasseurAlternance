import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "jobs.db"


def get_connection():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT,
            location TEXT,
            url TEXT UNIQUE,
            source TEXT,
            contract_type TEXT,
            date_posted TEXT,
            date_scraped TEXT DEFAULT (date('now'))
        )
    """)
    conn.commit()
    conn.close()


def insert_jobs(jobs: list[dict]) -> int:
    conn = get_connection()
    inserted = 0
    for job in jobs:
        try:
            conn.execute(
                """INSERT INTO jobs (title, company, location, url, source, contract_type, date_posted)
                   VALUES (:title, :company, :location, :url, :source, :contract_type, :date_posted)""",
                job,
            )
            inserted += 1
        except sqlite3.IntegrityError:
            pass
    conn.commit()
    conn.close()
    return inserted


def get_jobs(contract_type=None, city=None):
    conn = get_connection()
    query = "SELECT * FROM jobs WHERE 1=1"
    params = []
    if contract_type:
        query += " AND contract_type = ?"
        params.append(contract_type)
    if city:
        query += " AND location LIKE ?"
        params.append(f"%{city}%")
    query += " AND LOWER(title) NOT LIKE '%openclassroom%'"
    query += " AND LOWER(company) NOT LIKE '%openclassroom%'"
    query += " ORDER BY COALESCE(date_posted, date_scraped) DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

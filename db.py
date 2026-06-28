"""
DriveIQ Database — SQLite (no server needed, runs everywhere)
db file: driveiq.db (auto-created on first run)
"""

import sqlite3
import os

DB_PATH = "driveiq.db"


def init_db():
    """Create the database and tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            email TEXT,
            phone TEXT,
            location TEXT,
            experience TEXT,
            target_role TEXT,
            resume_text TEXT,
            resume_score REAL,
            technical_fit REAL,
            automotive_relevance REAL,
            leadership_signals REAL,
            authenticity_score REAL,
            interview_score REAL,
            verdict TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def save_application(data: dict) -> int:
    """
    Save applicant data to the database.
    Returns the new row ID.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO applications (
            first_name, last_name, email, phone, location,
            experience, target_role, resume_text,
            resume_score, technical_fit, automotive_relevance,
            leadership_signals, authenticity_score,
            interview_score, verdict
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("first_name", ""),
        data.get("last_name", ""),
        data.get("email", ""),
        data.get("phone", ""),
        data.get("location", ""),
        data.get("experience", ""),
        data.get("target_role", ""),
        data.get("resume_text", "")[:5000],  # limit size
        data.get("resume_score", 0),
        data.get("technical_fit", 0),
        data.get("automotive_relevance", 0),
        data.get("leadership_signals", 0),
        data.get("authenticity_score", 0),
        data.get("interview_score", 0),
        data.get("verdict", ""),
    ))
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


def get_all_applications():
    """Fetch all applications (for admin use)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applications ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

import sqlite3
from datetime import datetime

DB_NAME = "notes_bot.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id TEXT NOT NULL,
            file_unique_id TEXT NOT NULL,
            file_name TEXT,
            title TEXT NOT NULL,
            subject TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            user_name TEXT,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            full_name TEXT,
            joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_user(user_id, full_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, full_name)
        VALUES (?, ?)
    ''', (user_id, full_name))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users')
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users

def get_stats():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM notes')
    note_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    conn.close()
    return user_count, note_count

def add_note(file_id, file_unique_id, file_name, title, subject, user_id, user_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO notes (file_id, file_unique_id, file_name, title, subject, user_id, user_name)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (file_id, file_unique_id, file_name, title, subject, user_id, user_name))
    conn.commit()
    conn.close()

def get_subjects():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT subject FROM notes ORDER BY subject')
    subjects = [row[0] for row in cursor.fetchall()]
    conn.close()
    return subjects

def get_notes_by_subject(subject):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, file_name, user_name, upload_date FROM notes WHERE subject = ? ORDER BY upload_date DESC', (subject,))
    notes = cursor.fetchall()
    conn.close()
    return notes

def get_note_by_id(note_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT file_id, file_name, title, subject, user_id FROM notes WHERE id = ?', (note_id,))
    note = cursor.fetchone()
    conn.close()
    return note

def search_notes(query):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Search in title or subject
    search_query = f"%{query}%"
    cursor.execute('''
        SELECT id, title, subject, file_name 
        FROM notes 
        WHERE title LIKE ? OR subject LIKE ? 
        ORDER BY upload_date DESC 
        LIMIT 10
    ''', (search_query, search_query))
    results = cursor.fetchall()
    conn.close()
    return results

def get_user_notes(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, subject, upload_date FROM notes WHERE user_id = ? ORDER BY upload_date DESC', (user_id,))
    notes = cursor.fetchall()
    conn.close()
    return notes

def delete_note(note_id, user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM notes WHERE id = ? AND user_id = ?', (note_id, user_id))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0

def force_delete_note(note_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0

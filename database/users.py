# database/users.py — управление пользователями
import sqlite3
import os
from typing import List, Optional

DB_PATH = "users.db"


def init_db():
    """Инициализация базы данных"""
    os.makedirs(os.path.dirname(DB_PATH) if os.path.dirname(DB_PATH) else '.', exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS allowed_users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            added_by INTEGER,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()


def add_user(user_id: int, username: str, first_name: str, last_name: str, added_by: int) -> bool:
    """Добавить пользователя в разрешенные"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO allowed_users 
            (user_id, username, first_name, last_name, added_by)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name, added_by))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding user: {e}")
        return False


def remove_user(user_id: int) -> bool:
    """Удалить пользователя из разрешенных"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('DELETE FROM allowed_users WHERE user_id = ?', (user_id,))

        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error removing user: {e}")
        return False


def is_user_allowed(user_id: int) -> bool:
    """Проверить, разрешен ли пользователь"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('SELECT 1 FROM allowed_users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone() is not None

        conn.close()
        return result
    except:
        return False


def get_all_users() -> List[dict]:
    """Получить список всех разрешенных пользователей"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT user_id, username, first_name, last_name, added_by, added_at
            FROM allowed_users 
            ORDER BY added_at DESC
        ''')

        users = []
        for row in cursor.fetchall():
            users.append({
                'user_id': row[0],
                'username': row[1],
                'first_name': row[2],
                'last_name': row[3],
                'added_by': row[4],
                'added_at': row[5]
            })

        conn.close()
        return users
    except Exception as e:
        print(f"Error getting users: {e}")
        return []
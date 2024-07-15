import sqlite3
from contextlib import contextmanager

DATABASE_NAME = 'bot_database.db'

@contextmanager
def get_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def create_tables():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                number TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mailings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT,
                image_id TEXT,
                video_id TEXT,
                button_text TEXT,
                button_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mailing_channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mailing_id INTEGER,
                channel_name TEXT,
                FOREIGN KEY (mailing_id) REFERENCES mailings(id)
            )
        ''')

def add_user(name, age, number):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (name, age, number)
            VALUES (?, ?, ?)
        ''', (name, age, number))

def add_mailing(content=None, image_id=None, video_id=None, button_text=None, button_url=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO mailings (content, image_id, video_id, button_text, button_url)
            VALUES (?, ?, ?, ?, ?)
        ''', (content, image_id, video_id, button_text, button_url))
        return cursor.lastrowid

def add_mailing_channel(mailing_id, channel_name):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO mailing_channels (mailing_id, channel_name)
            VALUES (?, ?)
        ''', (mailing_id, channel_name))
    
    # conn.commit()
    # conn.close()

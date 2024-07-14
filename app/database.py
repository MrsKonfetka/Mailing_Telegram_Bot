import sqlite3

DATABASE_NAME = 'bot_database.db'

def create_tables():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            number TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def add_user(name, age, number):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO users (name, age, number)
        VALUES (?, ?, ?)
    ''', (name, age, number))
    
    conn.commit()
    conn.close()

import sqlite3

def init_db():
    conn = sqlite3.connect('game.db')
    c = conn.cursor()

    # Buat tabel user
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id float PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        score float DEFAULT 0
    )
    ''')
    
    # Create game_scores table to track individual game sessions
    c.execute('''
    CREATE TABLE IF NOT EXISTS game_scores (
        id float PRIMARY KEY AUTOINCREMENT,
        user_id float NOT NULL,
        score float NOT NULL,
        date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')

    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect('game.db')

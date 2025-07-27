import sqlite3
from Db import get_connection

def register(username, password):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    result = c.fetchone()
    conn.close()
    return result

def update_username(user_id, new_username):
    conn = get_connection()
    c = conn.cursor()
    try:
        # Check if username already exists
        c.execute("SELECT * FROM users WHERE username=? AND id!=?", (new_username, user_id))
        if c.fetchone():
            conn.close()
            return False, "Username already exists"
        
        # Update username
        c.execute("UPDATE users SET username=? WHERE id=?", (new_username, user_id))
        conn.commit()
        conn.close()
        return True, "Username updated successfully"
    except Exception as e:
        conn.close()
        return False, str(e)

def delete_account(user_id):
    conn = get_connection()
    c = conn.cursor()
    try:
        # Delete user's game records
        c.execute("DELETE FROM game_scores WHERE user_id=?", (user_id,))
        
        # Delete user account
        c.execute("DELETE FROM users WHERE id=?", (user_id,))
        
        conn.commit()
        conn.close()
        return True, "Account deleted successfully"
    except Exception as e:
        conn.close()
        return False, str(e)

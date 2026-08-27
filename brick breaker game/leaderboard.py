from Db import get_connection
import datetime

def update_score(user_id, score):
    conn = get_connection()
    c = conn.cursor()
    
    # First, make sure the game_scores table exists
    c.execute('''
    CREATE TABLE IF NOT EXISTS game_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        score INTEGER NOT NULL,
        date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')
    
    # Update highest score in users table (for backwards compatibility)
    c.execute("UPDATE users SET score = MAX(score, ?) WHERE id = ?", (score, user_id))
    
    # Add this game session to game_scores table
    c.execute("INSERT INTO game_scores (user_id, score) VALUES (?, ?)", (user_id, score))
    
    conn.commit()
    conn.close()

def get_top_scores(limit=5):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT username, score FROM users ORDER BY score DESC LIMIT ?", (limit,))
    result = c.fetchall()
    conn.close()
    return result

def get_player_history(user_id, limit=10):
    """Get the recent game history for a specific player"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT score, date_time 
        FROM game_scores 
        WHERE user_id = ? 
        ORDER BY date_time DESC 
        LIMIT ?
    """, (user_id, limit))
    result = c.fetchall()
    conn.close()
    return result

def get_player_stats(user_id):
    """Get comprehensive statistics for a player"""
    conn = get_connection()
    c = conn.cursor()
    
    # Get username
    c.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    username = c.fetchone()[0]
    
    # Get highest score
    c.execute("SELECT MAX(score) FROM game_scores WHERE user_id = ?", (user_id,))
    highest_score = c.fetchone()[0] or 0
    
    # Get average score
    c.execute("SELECT AVG(score) FROM game_scores WHERE user_id = ?", (user_id,))
    avg_score = c.fetchone()[0] or 0
    
    # Get total games played
    c.execute("SELECT COUNT(*) FROM game_scores WHERE user_id = ?", (user_id,))
    games_played = c.fetchone()[0] or 0
    
    # Get score progression (last 5 games)
    c.execute("""
        SELECT score FROM game_scores 
        WHERE user_id = ? 
        ORDER BY date_time DESC 
        LIMIT 5
    """, (user_id,))
    recent_scores = [row[0] for row in c.fetchall()]
    
    conn.close()
    
    return {
        "username": username,
        "highest_score": highest_score,
        "average_score": round(avg_score, 1),
        "games_played": games_played,
        "recent_scores": recent_scores
    }

def get_global_stats():
    """Get global game statistics"""
    conn = get_connection()
    c = conn.cursor()
    
    # Get highest score ever
    c.execute("""
        SELECT u.username, MAX(g.score) as max_score
        FROM game_scores g
        JOIN users u ON g.user_id = u.id
        GROUP BY g.user_id
        ORDER BY max_score DESC
        LIMIT 1
    """)
    highest_result = c.fetchone()
    highest_player = highest_result[0] if highest_result else "None"
    highest_score = highest_result[1] if highest_result else 0
    
    # Get average score across all games
    c.execute("SELECT AVG(score) FROM game_scores")
    avg_score = c.fetchone()[0] or 0
    
    # Get total games played
    c.execute("SELECT COUNT(*) FROM game_scores")
    total_games = c.fetchone()[0] or 0
    
    conn.close()
    
    return {
        "highest_player": highest_player,
        "highest_score": highest_score,
        "average_score": round(avg_score, 1),
        "total_games": total_games
    }

import pygame
import sys
import sqlite3
import game
from login_register import handle_login_screen, handle_register_screen, LOGIN, REGISTER, MENU
from dashboard import show_dashboard

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Break-Breaker Pro")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
LIGHT_BLUE = (173, 216, 230)
GRAY = (100, 100, 100)

# Database setup
def init_db():
    conn = sqlite3.connect('breakbreaker.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE,
                  password TEXT)''')
    
    # Scores table
    c.execute('''CREATE TABLE IF NOT EXISTS scores
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  score INTEGER,
                  date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY(user_id) REFERENCES users(id))''')
    
    # Game scores table for tracking player progress
    c.execute('''CREATE TABLE IF NOT EXISTS game_scores
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  score INTEGER NOT NULL,
                  date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY(user_id) REFERENCES users(id))''')
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

def main():
    # Initialize variables
    current_state = LOGIN  # Start with login screen
    active_input = None
    input_text = ""
    login_data = {"username": "", "password": ""}
    register_data = {"username": "", "password": "", "confirm": ""}
    logged_in_user = None
    error_message = ""
    
    # Main game loop
    clock = pygame.time.Clock()
    running = True
    
    while running:
        # Limit frame rate
        clock.tick(60)
        
        # Get events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
        
        # Clear screen
        screen.fill(BLACK)
        
        # State machine
        if current_state == LOGIN:
            # Handle login screen
            next_state, active_input, input_text, login_data, error_message, user_id = handle_login_screen(
                screen, events, active_input, input_text, login_data, error_message
            )
            
            if user_id:
                logged_in_user = user_id
            
            current_state = next_state
        
        elif current_state == REGISTER:
            # Handle register screen
            next_state, active_input, input_text, register_data, error_message = handle_register_screen(
                screen, events, active_input, input_text, register_data, error_message
            )
            
            current_state = next_state
        
        elif current_state == MENU:
            # Show dashboard and get next action
            action = show_dashboard(screen, logged_in_user)
            
            if action == "PLAY":
                # Start the game
                game.start(logged_in_user)
            elif action == "LOGIN":
                current_state = LOGIN
                login_data = {"username": "", "password": ""}
                error_message = ""
            elif action == "REGISTER":
                current_state = REGISTER
                register_data = {"username": "", "password": "", "confirm": ""}
                error_message = ""
            elif action == "LOGOUT":
                logged_in_user = None
                current_state = LOGIN
                login_data = {"username": "", "password": ""}
                error_message = ""
            elif action == "QUIT":
                running = False
        
        # Update display
        pygame.display.flip()
    
    # Quit pygame
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
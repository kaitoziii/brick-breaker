import pygame
import hashlib
import sqlite3
import random
import math 

# Colors - Subtle, elegant color palette
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
BLUE = (50, 100, 180)
GREEN = (50, 170, 100)
GRAY = (120, 120, 120)
LIGHT_GRAY = (230, 230, 230)
DARK_BLUE = (20, 40, 80)
PURPLE = (100, 80, 150)
CYAN = (90, 160, 190)
ORANGE = (230, 150, 50)
BG_COLOR = (10, 20, 40)

# States
LOGIN = 1
REGISTER = 2
MENU = 0

# Initialize fonts
try:
    font_small = pygame.font.Font("freesansbold.ttf", 20)
    font_medium = pygame.font.Font("freesansbold.ttf", 28)
    font_large = pygame.font.Font("freesansbold.ttf", 36)
except:
    # Fallback to default font
    font_small = pygame.font.Font(None, 24)
    font_medium = pygame.font.Font(None, 32)
    font_large = pygame.font.Font(None, 40)

# Input boxes
WIDTH, HEIGHT = 800, 600
login_boxes = {
    "username": pygame.Rect(WIDTH//2-120, HEIGHT//2-40, 240, 35),
    "password": pygame.Rect(WIDTH//2-120, HEIGHT//2+20, 240, 35)
}

register_boxes = {
    "username": pygame.Rect(WIDTH//2-150, HEIGHT//2-70, 300, 35),
    "password": pygame.Rect(WIDTH//2-150, HEIGHT//2, 300, 35),
    "confirm": pygame.Rect(WIDTH//2-150, HEIGHT//2+70, 300, 35)
}

# Password visibility
show_password_login = False
show_password_register = False
show_confirm_register = False

# Particles for background
particles = []
for _ in range(50):
    particles.append({
        'x': random.randint(0, WIDTH),
        'y': random.randint(0, HEIGHT),
        'size': random.randint(1, 2),
        'brightness': random.randint(100, 200),
        'speed': random.uniform(0.2, 0.5)  # Very slow speed
    })

# Simple eye icon for password visibility toggle
def create_eye_icon(show_password=False):
    icon_size = 24  # Slightly larger icon
    icon = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
    
    # Choose color based on state
    color = BLUE if show_password else GRAY
    
    # Draw eye outline
    pygame.draw.ellipse(icon, color, (0, 5, icon_size, 12), 2)
    
    # Draw pupil
    pygame.draw.circle(icon, color, (icon_size//2, icon_size//2), 4)
    
    # Add a line through the eye if password is hidden
    if not show_password:
        pygame.draw.line(icon, color, (3, icon_size//2), (icon_size-3, icon_size//2), 2)
    
    return icon

def draw_text(screen, text, font, color, x, y, centered=True):
    text_surface = font.render(text, True, color)
    if centered:
        text_rect = text_surface.get_rect(center=(x, y))
    else:
        text_rect = text_surface.get_rect(topleft=(x, y))
    screen.blit(text_surface, text_rect)
    return text_rect

def draw_rounded_rect(surface, rect, color, radius=10, border_width=0, border_color=None):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border_width > 0 and border_color:
        pygame.draw.rect(surface, border_color, rect, border_width, border_radius=radius)
    return rect

def draw_button(screen, text, rect, color, hover_color=None, text_color=WHITE):
    mouse_pos = pygame.mouse.get_pos()
    current_color = hover_color if rect.collidepoint(mouse_pos) and hover_color else color
    
    draw_rounded_rect(screen, rect, current_color)
    draw_text(screen, text, font_small, text_color, rect.centerx, rect.centery)
    
    return rect

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    if not username or not password:
        return False, "Username and password cannot be empty"
    
    try:
        conn = sqlite3.connect('game.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                 (username, hash_password(password)))
        conn.commit()
        conn.close()
        return True, "Registration successful!"
    except sqlite3.IntegrityError:
        return False, "Username already exists"

def login_user(username, password):
    if not username or not password:
        return None, "Username and password cannot be empty"
    
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username=? AND password=?", 
             (username, hash_password(password)))
    user = c.fetchone()
    conn.close()
    
    if user:
        return user[0], "Login successful!"
    else:
        return None, "Invalid username or password"

def draw_background(screen):
    # Simple gradient background
    for y in range(HEIGHT):
        r = int(10 + (30 - 10) * (1 - y / HEIGHT))
        g = int(20 + (50 - 20) * (1 - y / HEIGHT))
        b = int(40 + (80 - 40) * (1 - y / HEIGHT))
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))
    
    # Draw and update existing particles
    for particle in particles:
        # Draw the particle
        pygame.draw.circle(
            screen, 
            (particle['brightness'], particle['brightness'], particle['brightness']), 
            (int(particle['x']), int(particle['y'])), 
            particle['size']
        )
        
        # Move the particle very slowly (10x slower)
        particle['y'] += particle['speed']
        
        # Reset particle if it goes off screen
        if particle['y'] > HEIGHT:
            particle['y'] = 0
            particle['x'] = random.randint(0, WIDTH)
            particle['brightness'] = random.randint(100, 200)

def draw_input_field(screen, rect, text, active, placeholder="", is_password=False, show_password=False):
    # Draw field background
    color = LIGHT_GRAY
    border_color = BLUE if active else GRAY
    draw_rounded_rect(screen, rect, color, border_width=2, border_color=border_color)
    
    # Prepare display text
    display_text = text
    if is_password and not show_password:
        display_text = "•" * len(text)
    
    # Draw text or placeholder
    if display_text:
        text_surface = font_small.render(display_text, True, BLACK)
        screen.blit(text_surface, (rect.x + 10, rect.y + (rect.height - text_surface.get_height()) // 2))
    elif not active:
        placeholder_surface = font_small.render(placeholder, True, GRAY)
        screen.blit(placeholder_surface, (rect.x + 10, rect.y + (rect.height - placeholder_surface.get_height()) // 2))
    
    # Draw cursor if field is active
    if active and pygame.time.get_ticks() % 1000 < 500:
        cursor_x = rect.x + 10
        if display_text:
            cursor_x += font_small.size(display_text)[0]
        pygame.draw.line(screen, BLACK, (cursor_x, rect.y + 8), (cursor_x, rect.y + rect.height - 8), 2)
    
    # If password field, add eye icon
    if is_password:
        # Create larger clickable area for the eye icon
        eye_rect = pygame.Rect(rect.right - 35, rect.y + (rect.height - 24) // 2, 24, 24)
        
        # Draw background for the eye icon for better visibility
        if show_password:
            # Draw light background behind the eye when active
            pygame.draw.rect(screen, (220, 240, 255), eye_rect, border_radius=5)
        
        # Get the appropriate eye icon based on password visibility
        icon = create_eye_icon(show_password)
        screen.blit(icon, eye_rect)
        
        return eye_rect
    
    return None

def handle_login_screen(screen, events, active_input, input_text, login_data, error_message):
    global show_password_login
    
    # Initialize return variables
    next_state = LOGIN
    new_active_input = active_input
    new_input_text = input_text
    new_login_data = login_data.copy()
    new_error_message = error_message
    user_id = None
    
    # Draw background
    draw_background(screen)
    
    # Draw login card
    card_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 120, 300, 300)
    draw_rounded_rect(screen, card_rect, (245, 245, 250, 230), radius=12)
    
    # Draw title
    draw_text(screen, "Login", font_large, DARK_BLUE, WIDTH//2, HEIGHT//2 - 90)
    
    # Draw input fields
    username_field = login_boxes["username"]
    password_field = login_boxes["password"]
    
    draw_input_field(screen, username_field, new_login_data["username"], 
                    new_active_input == "username", "Username")
    
    eye_rect = draw_input_field(screen, password_field, new_login_data["password"], 
                               new_active_input == "password", "Password", 
                               is_password=True, show_password=show_password_login)
    
    # Draw buttons
    login_button = draw_button(screen, "Login", pygame.Rect(WIDTH//2 - 60, HEIGHT//2 + 100, 120, 30), GREEN)
    
    # Draw register link
    register_text = "Create account"
    register_link = draw_text(screen, register_text, font_small, BLUE, WIDTH//2, HEIGHT//2 + 160)
    
    # Draw error message if any
    if new_error_message:
        draw_text(screen, new_error_message, font_small, RED, WIDTH//2, HEIGHT//2 - 160)
    
    # Handle events
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check eye icon FIRST - before checking the password field
            if eye_rect and eye_rect.collidepoint(event.pos):
                show_password_login = not show_password_login
                
                draw_input_field(screen, password_field, new_login_data["password"], 
                               new_active_input == "password", "Password", 
                               is_password=True, show_password=show_password_login)
                pygame.display.update(password_field.inflate(100, 50))  # Partial update for performance
            elif username_field.collidepoint(event.pos):
                new_active_input = "username"
                new_input_text = new_login_data["username"]
            elif password_field.collidepoint(event.pos):
                new_active_input = "password"
                new_input_text = new_login_data["password"]
            elif login_button.collidepoint(event.pos):
                user_id, message = login_user(new_login_data["username"], new_login_data["password"])
                if user_id:
                    next_state = MENU
                    new_active_input = None
                    new_input_text = ""
                    new_error_message = ""
                else:
                    new_error_message = message
            elif register_link.collidepoint(event.pos):
                next_state = REGISTER
                new_active_input = None
                new_input_text = ""
                new_error_message = ""
            else:
                new_active_input = None
        elif event.type == pygame.KEYDOWN:
            if new_active_input:
                if event.key == pygame.K_RETURN:
                    if new_active_input == "username":
                        new_active_input = "password"
                        new_input_text = new_login_data["password"]
                    elif new_active_input == "password":
                        user_id, message = login_user(new_login_data["username"], new_login_data["password"])
                        if user_id:
                            next_state = MENU
                            new_active_input = None
                            new_input_text = ""
                            new_error_message = ""
                        else:
                            new_error_message = message
                elif event.key == pygame.K_BACKSPACE:
                    new_input_text = new_input_text[:-1]
                    new_login_data[new_active_input] = new_input_text
                elif event.key == pygame.K_TAB:
                    if new_active_input == "username":
                        new_active_input = "password"
                        new_input_text = new_login_data["password"]
                    else:
                        new_active_input = "username"
                        new_input_text = new_login_data["username"]
                elif event.key == pygame.K_ESCAPE:
                    next_state = MENU
                else:
                    new_input_text += event.unicode
                    new_login_data[new_active_input] = new_input_text
    
    return next_state, new_active_input, new_input_text, new_login_data, new_error_message, user_id

def handle_register_screen(screen, events, active_input, input_text, register_data, error_message):
    global show_password_register, show_confirm_register
    
    # Initialize return variables
    next_state = REGISTER
    new_active_input = active_input
    new_input_text = input_text
    new_register_data = register_data.copy()
    new_error_message = error_message
    
    # Draw background
    draw_background(screen)
    
    # Draw register card
    card_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 150, 400, 340)
    draw_rounded_rect(screen, card_rect, (245, 245, 250, 230), radius=12)
    
    # Draw title
    draw_text(screen, "Register", font_large, DARK_BLUE, WIDTH//2, HEIGHT//2 - 120)
    
    # Draw input fields
    username_field = register_boxes["username"]
    password_field = register_boxes["password"]
    confirm_field = register_boxes["confirm"]
    
    draw_input_field(screen, username_field, new_register_data["username"], 
                    new_active_input == "username", "Username")
    
    password_eye_rect = draw_input_field(screen, password_field, new_register_data["password"], 
                                        new_active_input == "password", "Password", 
                                        is_password=True, show_password=show_password_register)
    
    confirm_eye_rect = draw_input_field(screen, confirm_field, new_register_data["confirm"], 
                                       new_active_input == "confirm", "Confirm Password", 
                                       is_password=True, show_password=show_confirm_register)
    
    # Draw buttons
    register_button = draw_button(screen, "Register", pygame.Rect(WIDTH//2 - 60, HEIGHT//2 + 120, 120, 30), GREEN)
    
    # Draw login link
    login_text = "Already have an account? Login"
    login_link = draw_text(screen, login_text, font_small, BLUE, WIDTH//2, HEIGHT//2 + 170)
    
    # Draw error message if any
    if new_error_message:
        draw_text(screen, new_error_message, font_small, RED, WIDTH//2, HEIGHT//2 - 160)
    
    # Handle events
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            # Check password eye icon FIRST - before checking the password field
            if password_eye_rect and password_eye_rect.collidepoint(mouse_pos):
                show_password_register = not show_password_register
                
                pygame.draw.rect(screen, (0, 0, 0), password_field.inflate(100, 70))  # Clear area
                draw_input_field(screen, password_field, new_register_data["password"], 
                               new_active_input == "password", "Password", 
                               is_password=True, show_password=show_password_register)
                pygame.display.flip()  # Update entire screen
            
            # Check confirm password eye icon NEXT
            elif confirm_eye_rect and confirm_eye_rect.collidepoint(mouse_pos):
                show_confirm_register = not show_confirm_register
                
                pygame.draw.rect(screen, (0, 0, 0), confirm_field.inflate(100, 70))  # Clear area
                draw_input_field(screen, confirm_field, new_register_data["confirm"], 
                               new_active_input == "confirm", "Confirm Password", 
                               is_password=True, show_password=show_confirm_register)
                pygame.display.flip()  # Update entire screen
            
            # Only check input fields AFTER checking eye icons
            elif username_field.collidepoint(mouse_pos):
                new_active_input = "username"
                new_input_text = new_register_data["username"]
            elif password_field.collidepoint(mouse_pos):
                new_active_input = "password"
                new_input_text = new_register_data["password"]
            elif confirm_field.collidepoint(mouse_pos):
                new_active_input = "confirm"
                new_input_text = new_register_data["confirm"]
            elif register_button.collidepoint(mouse_pos):
                if new_register_data["password"] != new_register_data["confirm"]:
                    new_error_message = "Passwords do not match"
                else:
                    success, message = register_user(new_register_data["username"], new_register_data["password"])
                    if success:
                        next_state = LOGIN
                        new_register_data = {"username": "", "password": "", "confirm": ""}
                        new_active_input = None
                        new_input_text = ""
                        new_error_message = ""
                    else:
                        new_error_message = message
            elif login_link.collidepoint(mouse_pos):
                next_state = LOGIN
                new_active_input = None
                new_input_text = ""
                new_error_message = ""
            else:
                new_active_input = None
        elif event.type == pygame.KEYDOWN:
            if new_active_input:
                if event.key == pygame.K_RETURN:
                    if new_active_input == "username":
                        new_active_input = "password"
                        new_input_text = new_register_data["password"]
                    elif new_active_input == "password":
                        new_active_input = "confirm"
                        new_input_text = new_register_data["confirm"]
                    elif new_active_input == "confirm":
                        if new_register_data["password"] != new_register_data["confirm"]:
                            new_error_message = "Passwords do not match"
                        else:
                            success, message = register_user(new_register_data["username"], new_register_data["password"])
                            if success:
                                next_state = LOGIN
                                new_register_data = {"username": "", "password": "", "confirm": ""}
                                new_active_input = None
                                new_input_text = ""
                                new_error_message = ""
                            else:
                                new_error_message = message
                elif event.key == pygame.K_BACKSPACE:
                    new_input_text = new_input_text[:-1]
                    new_register_data[new_active_input] = new_input_text
                elif event.key == pygame.K_TAB:
                    if new_active_input == "username":
                        new_active_input = "password"
                        new_input_text = new_register_data["password"]
                    elif new_active_input == "password":
                        new_active_input = "confirm"
                        new_input_text = new_register_data["confirm"]
                    else:
                        new_active_input = "username"
                        new_input_text = new_register_data["username"]
                elif event.key == pygame.K_ESCAPE:
                    next_state = LOGIN
                else:
                    new_input_text += event.unicode
                    new_register_data[new_active_input] = new_input_text
    
    return next_state, new_active_input, new_input_text, new_register_data, new_error_message
import pygame
import game
import sys
import math
import sqlite3
from datetime import datetime
from leaderboard import get_player_stats, get_global_stats
import random
import auth

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
BLUE = (50, 100, 255)
GREEN = (50, 200, 100)
PURPLE = (150, 50, 200)
CYAN = (0, 210, 210)
ORANGE = (255, 165, 0)
DARK_BLUE = (20, 30, 60)
LIGHT_BLUE = (173, 216, 230)
GRAY = (100, 100, 100)
TRANSPARENT_BLACK = (0, 0, 0, 180)

# Screen dimensions
WIDTH, HEIGHT = 800, 600

# Game states
MAIN_MENU = 0
LEADERBOARD = 1
STORE = 2
SETTINGS = 3
GAME_HISTORY = 4
PROFILE = 5
USERNAME_EDIT = 6

# Initialize fonts
try:
    font_small = pygame.font.Font("freesansbold.ttf", 24)
    font_medium = pygame.font.Font("freesansbold.ttf", 36)
    font_large = pygame.font.Font("freesansbold.ttf", 48)
    font_title = pygame.font.Font("freesansbold.ttf", 64)
except:
    # Fallback to default font if custom font not found
    font_small = pygame.font.Font(None, 28)
    font_medium = pygame.font.Font(None, 42)
    font_large = pygame.font.Font(None, 56)
    font_title = pygame.font.Font(None, 72)

# Animation variables
menu_animation = 0
particles = []

def get_username(user_id):
    """Get username from user ID"""
    if not user_id:
        return None
    
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE id=?", (user_id,))
    result = c.fetchone()
    conn.close()
    
    return result[0] if result else None

def draw_text(screen, text, font, color, x, y, shadow=False):
    if shadow:
        shadow_surface = font.render(text, True, (30, 30, 30))
        shadow_rect = shadow_surface.get_rect(center=(x+2, y+2))
        screen.blit(shadow_surface, shadow_rect)
    
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

def draw_rounded_rect(surface, rect, color, radius=15, alpha=255):
    """Draw a rounded rectangle with optional transparency"""
    if alpha < 255:
        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s, color + (alpha,), (0, 0, rect.width, rect.height), border_radius=radius)
        surface.blit(s, (rect.x, rect.y))
    else:
        pygame.draw.rect(surface, color, rect, border_radius=radius)
    
    return rect

def draw_button(screen, text, rect, color, hover_color=None, text_color=WHITE, shadow=True, icon=None):
    mouse_pos = pygame.mouse.get_pos()
    
    # Check if mouse is over button
    if rect.collidepoint(mouse_pos):
        if hover_color:
            color = hover_color
        else:
            # Lighten the color if no hover color specified
            color = (min(color[0] + 30, 255), min(color[1] + 30, 255), min(color[2] + 30, 255))
        
        # Add some particles when hovering
        if menu_animation % 10 == 0:
            particles.append({
                'x': rect.centerx + random.randint(-rect.width//2, rect.width//2),
                'y': rect.centery + random.randint(-rect.height//2, rect.height//2),
                'size': random.randint(2, 5),
                'color': color,
                'life': 20
            })
    
    # Draw button with rounded corners
    draw_rounded_rect(screen, rect, color)
    
    # Add subtle gradient to button
    gradient = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    for i in range(rect.height):
        alpha = 10 - (i / rect.height * 10)
        pygame.draw.line(gradient, (255, 255, 255, alpha), (0, i), (rect.width, i))
    
    gradient_rect = gradient.get_rect(topleft=(rect.x, rect.y))
    screen.blit(gradient, gradient_rect)
    
    # Draw icon if provided
    if icon:
        icon_rect = icon.get_rect(midright=(rect.centerx - 10, rect.centery))
        screen.blit(icon, icon_rect)
        # Draw text with shadow, shifted right to accommodate icon
        draw_text(screen, text, font_small, text_color, rect.centerx + 15, rect.centery, shadow)
    else:
        # Draw text with shadow
        draw_text(screen, text, font_small, text_color, rect.centerx, rect.centery, shadow)
    
    # Add a subtle border
    pygame.draw.rect(screen, (255, 255, 255, 30), rect, 2, border_radius=15)
    
    return rect

def draw_gradient_background(screen):
    # Create a more vibrant gradient background
    for y in range(HEIGHT):
        # Calculate colors for a more dynamic gradient
        progress = y / HEIGHT
        r = int(20 * (1 - progress))
        g = int(30 * (1 - progress))
        b = int(80 + 50 * (1 - progress))
        color = (r, g, b)
        pygame.draw.line(screen, color, (0, y), (WIDTH, y))
    
    # Add animated stars/particles with varying sizes and brightness
    global menu_animation, particles
    
    # Update existing particles
    updated_particles = []
    for p in particles:
        p['life'] -= 1
        if p['life'] > 0:
            alpha = min(255, p['life'] * 12)
            pygame.draw.circle(screen, p['color'] + (alpha,), (p['x'], p['y']), p['size'])
            updated_particles.append(p)
    particles = updated_particles
    
    # Add background stars
    for i in range(100):
        x = (i * 37 + menu_animation // 3) % WIDTH
        y = (i * 23 + menu_animation // 2) % HEIGHT
        
        # Vary star size based on position
        size_factor = (math.sin(menu_animation / 100 + i) + 1) / 2
        size = 1 + size_factor * 2
        
        # Twinkle effect
        brightness = 100 + (math.sin(menu_animation / 30 + i * 0.3) + 1) * 77
        pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), size)

def get_leaderboard():
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute('''SELECT users.username, users.score
                 FROM users
                 ORDER BY users.score DESC LIMIT 10''')
    leaderboard = c.fetchall()
    conn.close()
    return leaderboard

def draw_card(screen, title, content, rect, color=DARK_BLUE, title_color=WHITE, content_color=WHITE):
    """Draw a card with a title and content"""
    # Draw card background with slight transparency
    draw_rounded_rect(screen, rect, color, alpha=230)
    
    # Draw title area
    title_rect = pygame.Rect(rect.x, rect.y, rect.width, 50)
    draw_rounded_rect(screen, title_rect, (color[0]+20, color[1]+20, color[2]+40), radius=15)
    
    # Draw divider line
    pygame.draw.line(screen, WHITE, (rect.x+20, rect.y+50), (rect.x+rect.width-20, rect.y+50), 1)
    
    # Draw title
    draw_text(screen, title, font_small, title_color, rect.centerx, rect.y+25)
    
    # Draw content
    if isinstance(content, list):
        y_offset = 70
        for item in content:
            draw_text(screen, item, font_small, content_color, rect.centerx, rect.y+y_offset)
            y_offset += 30
    else:
        draw_text(screen, content, font_small, content_color, rect.centerx, rect.centery)
    
    # Add subtle border
    pygame.draw.rect(screen, (255, 255, 255, 30), rect, 1, border_radius=15)

def wrap_text(text, font, max_width):
    """Wrap text to fit within a certain width"""
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        # Create a test line with the new word
        test_line = ' '.join(current_line + [word])
        # Get the width of this test line
        width, _ = font.size(test_line)
        
        if width <= max_width:
            # Word fits, add it to the current line
            current_line.append(word)
        else:
            # Word doesn't fit, start a new line
            if current_line:  # Don't add empty lines
                lines.append(' '.join(current_line))
            current_line = [word]
    
    # Add the last line
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

def show_dashboard(screen, user_id):
    global menu_animation
    
    clock = pygame.time.Clock()
    current_state = MAIN_MENU
    running = True
    
    # Get username if user is logged in
    username = get_username(user_id) if user_id else None
    
    # Load user stats if logged in
    user_stats = None
    global_stats = None
    if user_id:
        try:
            user_stats = get_player_stats(user_id)
            global_stats = get_global_stats()
        except:
            pass  # Handle case where stats aren't available
    
    # Initialize variables needed for new functionality
    active_input = False
    input_text = ""
    input_rect = pygame.Rect(0, 0, 0, 0)
    confirmation_dialog = None
    message_box = None
    message_timeout = 0
    
    while running:
        # Limit frame rate
        clock.tick(60)
        
        # Handle events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return "QUIT"
        
        # Update animation
        menu_animation = (menu_animation + 1) % 10000
        
        # Clear screen
        screen.fill(BLACK)
        
        # Draw background
        draw_gradient_background(screen)
        
        # State machine
        if current_state == MAIN_MENU:
            # Draw animated title with glow effect
            title_glow = abs(math.sin(menu_animation / 60)) * 20
            title_color = (255, 255, 255)
            shadow_color = (50 + title_glow, 100 + title_glow, 255)
            
            # Draw shadow/glow first
            draw_text(screen, "BRICK BREAKER", font_title, shadow_color, WIDTH//2+2, 100+2, False)
            draw_text(screen, "BRICK BREAKER", font_title, title_color, WIDTH//2, 100, False)
            
            # Display welcome message if logged in
            if username:
                welcome_msg = f"Welcome, {username}!"
                draw_text(screen, welcome_msg, font_medium, CYAN, WIDTH//2, 160)
            
            # Draw menu container
            menu_rect = pygame.Rect(WIDTH//2 - 150, 190, 300, 300)
            draw_rounded_rect(screen, menu_rect, DARK_BLUE, alpha=180)
            
            # Draw buttons with improved styling
            button_spacing = 60
            button_y = 210
            
            play_button = draw_button(screen, "Play Game", pygame.Rect(WIDTH//2-120, button_y, 240, 50), GREEN)
            button_y += button_spacing
            
            leaderboard_button = draw_button(screen, "Leaderboard", pygame.Rect(WIDTH//2-120, button_y, 240, 50), BLUE)
            button_y += button_spacing
            
            if user_id:
                profile_button = draw_button(screen, "My Profile", pygame.Rect(WIDTH//2-120, button_y, 240, 50), PURPLE)
                button_y += button_spacing
                logout_button = draw_button(screen, "Logout", pygame.Rect(WIDTH//2-120, button_y, 240, 50), RED)
            else:
                login_button = draw_button(screen, "Login", pygame.Rect(WIDTH//2-120, button_y, 240, 50), LIGHT_BLUE)
                button_y += button_spacing
                register_button = draw_button(screen, "Register", pygame.Rect(WIDTH//2-120, button_y, 240, 50), PURPLE)
            
            # Quit button positioned at the bottom
            quit_button = draw_button(screen, "Quit", pygame.Rect(WIDTH//2-120, HEIGHT-60, 240, 50), RED)
            
            # Display stats cards if logged in
            if user_id and user_stats:
                # Left card - Player stats
                stats_card_rect = pygame.Rect(50, 200, 220, 180)
                stats_content = [
                    f"Highest: {user_stats['highest_score']}",
                    f"Average: {user_stats['average_score']}",
                    f"Games: {user_stats['games_played']}",
                ]
                draw_card(screen, "Your Stats", stats_content, stats_card_rect, DARK_BLUE)
                
                # Right card - Global stats
                if global_stats:
                    global_card_rect = pygame.Rect(WIDTH-270, 200, 220, 180)
                    global_content = [
                        f"Top Score: {global_stats['highest_score']}",
                        f"By: {global_stats['highest_player']}",
                        f"Games Played: {global_stats['total_games']}"
                    ]
                    draw_card(screen, "Global Stats", global_content, global_card_rect, DARK_BLUE)
            
            # Handle button clicks
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_button.collidepoint(event.pos):
                        if user_id:
                            return "PLAY"
                        else:
                            # Show message that login is required
                            draw_text(screen, "Please login first!", font_medium, RED, WIDTH//2, 550)
                            pygame.display.flip()
                            pygame.time.wait(1500)
                    
                    elif leaderboard_button.collidepoint(event.pos):
                        current_state = LEADERBOARD
                    
                    elif user_id and profile_button.collidepoint(event.pos):
                        current_state = PROFILE
                    
                    elif user_id and logout_button.collidepoint(event.pos):
                        return "LOGOUT"
                    
                    elif not user_id and login_button.collidepoint(event.pos):
                        return "LOGIN"
                    
                    elif not user_id and register_button.collidepoint(event.pos):
                        return "REGISTER"
                    
                    elif quit_button.collidepoint(event.pos):
                        return "QUIT"
        
        elif current_state == LEADERBOARD:
            # Draw leaderboard title with animation
            title_offset = math.sin(menu_animation / 30) * 5
            draw_text(screen, "LEADERBOARD", font_large, WHITE, WIDTH//2, 80 + title_offset, True)
            
            leaderboard_data = get_leaderboard()
            
            if leaderboard_data:
                # Create a card-style leaderboard
                table_width = 600
                table_height = 400
                table_left = (WIDTH - table_width) // 2
                
                # Draw a semi-transparent card for the table
                leaderboard_rect = pygame.Rect(table_left, 130, table_width, table_height)
                draw_rounded_rect(screen, leaderboard_rect, DARK_BLUE, radius=20, alpha=220)
                
                # Headers with better styling
                header_rect = pygame.Rect(table_left, 130, table_width, 50)
                draw_rounded_rect(screen, header_rect, (40, 60, 120), radius=20)
                
                # Header text
                draw_text(screen, "Rank", font_small, CYAN, table_left + 80, 155)
                draw_text(screen, "Player", font_small, CYAN, table_left + 270, 155)
                draw_text(screen, "Score", font_small, CYAN, table_left + 470, 155)
                
                # Horizontal line below headers
                pygame.draw.line(screen, CYAN, (table_left + 20, 180), (table_left + table_width - 20, 180), 2)
                
                # Entries with alternating row colors
                for i, (username, score) in enumerate(leaderboard_data):
                    y_pos = 200 + i * 35
                    row_rect = pygame.Rect(table_left + 20, y_pos - 17, table_width - 40, 34)
                    
                    # Alternating row colors
                    if i % 2 == 0:
                        draw_rounded_rect(screen, row_rect, (30, 50, 100, 100), radius=10)
                    
                    # Highlight top 3
                    rank_color = WHITE
                    if i == 0:
                        rank_color = (255, 215, 0)  # Gold
                    elif i == 1:
                        rank_color = (192, 192, 192)  # Silver
                    elif i == 2:
                        rank_color = (205, 127, 50)  # Bronze
                    
                    draw_text(screen, f"{i+1}", font_small, rank_color, table_left + 80, y_pos)
                    draw_text(screen, username, font_small, WHITE, table_left + 270, y_pos)
                    draw_text(screen, str(score), font_small, WHITE, table_left + 470, y_pos)
            else:
                draw_text(screen, "No scores yet!", font_medium, WHITE, WIDTH//2, HEIGHT//2)
            
            # Back button - centered at the bottom
            back_button = draw_button(screen, "Back", pygame.Rect(WIDTH//2-100, 540, 200, 50), RED)
            
            # Handle button clicks
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_button.collidepoint(event.pos):
                        current_state = MAIN_MENU
        
        elif current_state == PROFILE:
            # Only show if logged in and stats available
            if user_id and user_stats:
                # Profile title
                draw_text(screen, "Player Profile", font_large, WHITE, WIDTH//2, 80, True)
                
                # User info card
                profile_rect = pygame.Rect(WIDTH//2 - 300, 130, 600, 400)
                draw_rounded_rect(screen, profile_rect, DARK_BLUE, radius=20, alpha=220)
                
                # Add Edit Username button (now on the left of username)
                edit_username_button = draw_button(
                    screen, 
                    "Edit Username", 
                    pygame.Rect(WIDTH//2 - 290, 170, 180, 30), 
                    PURPLE,
                    text_color=WHITE,
                    shadow=False
                )
                
                # Username and join date
                draw_text(screen, username, font_medium, CYAN, WIDTH//2, 170)
                
                # Add Delete Account button (now on the right of username)
                delete_account_button = draw_button(
                    screen, 
                    "Delete Account", 
                    pygame.Rect(WIDTH//2 + 100, 170, 190, 30), 
                    RED,
                    text_color=WHITE,
                    shadow=False
                )
                
                # Stats in grid layout
                col1_x = WIDTH//2 - 200
                col2_x = WIDTH//2 + 200
                row1_y = 230
                row2_y = 300
                row3_y = 370
                
                # Stats with labels
                draw_text(screen, "Highest Score", font_small, LIGHT_BLUE, col1_x, row1_y)
                draw_text(screen, str(user_stats['highest_score']), font_medium, WHITE, col1_x, row1_y + 40)
                
                draw_text(screen, "Average Score", font_small, LIGHT_BLUE, col2_x, row1_y)
                draw_text(screen, str(user_stats['average_score']), font_medium, WHITE, col2_x, row1_y + 40)
                
                draw_text(screen, "Total Games", font_small, LIGHT_BLUE, col1_x, row2_y)
                draw_text(screen, str(user_stats['games_played']), font_medium, WHITE, col1_x, row2_y + 40)
                
                # Recent games heading
                draw_text(screen, "Recent Scores", font_small, LIGHT_BLUE, WIDTH//2, row3_y)
                
                # Draw recent scores as a chart if available
                if 'recent_scores' in user_stats and user_stats['recent_scores']:
                    scores = user_stats['recent_scores']
                    max_score = max(scores) if scores else 0
                    
                    if max_score > 0:
                        chart_width = 400
                        chart_height = 100
                        chart_left = WIDTH//2 - chart_width//2
                        chart_top = row3_y + 20
                        
                        # Draw chart background
                        chart_rect = pygame.Rect(chart_left, chart_top, chart_width, chart_height)
                        draw_rounded_rect(screen, chart_rect, (20, 30, 60), radius=10)
                        
                        # Draw score trend line
                        for i in range(len(scores)-1):
                            x1 = chart_left + (i * chart_width / (len(scores)-1))
                            y1 = chart_top + chart_height - (scores[i] / max_score * chart_height * 0.8)
                            x2 = chart_left + ((i+1) * chart_width / (len(scores)-1))
                            y2 = chart_top + chart_height - (scores[i+1] / max_score * chart_height * 0.8)
                            
                            pygame.draw.line(screen, CYAN, (x1, y1), (x2, y2), 2)
                            pygame.draw.circle(screen, WHITE, (int(x1), int(y1)), 4)
                        
                        # Draw final point
                        if scores:
                            final_x = chart_left + chart_width
                            final_y = chart_top + chart_height - (scores[-1] / max_score * chart_height * 0.8)
                            pygame.draw.circle(screen, WHITE, (int(final_x), int(final_y)), 4)
                
                # Back button
                back_button = draw_button(screen, "Back", pygame.Rect(WIDTH//2-100, 540, 200, 50), RED)
                
                # Handle button clicks
                for event in events:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if back_button.collidepoint(event.pos):
                            current_state = MAIN_MENU
                        
                        # Handle Edit Username button click
                        if user_id and 'edit_username_button' in locals() and edit_username_button.collidepoint(event.pos):
                            # Switch to username edit mode
                            current_state = USERNAME_EDIT
                            input_text = username
                            input_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 25, 300, 50)
                            active_input = True
                        
                        # Handle Delete Account button click
                        if user_id and 'delete_account_button' in locals() and delete_account_button.collidepoint(event.pos):
                            # Show confirmation dialog
                            confirmation_dialog = {
                                "title": "Confirm Delete",
                                "message": "Are you sure you want to delete your account? This cannot be undone.",
                                "yes_rect": pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 30, 100, 40),
                                "no_rect": pygame.Rect(WIDTH//2 + 10, HEIGHT//2 + 30, 100, 40)
                            }
        
        # Handle username edit state
        elif current_state == USERNAME_EDIT:
            # Draw background overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            # Draw input dialog
            dialog_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 100, 400, 200)
            draw_rounded_rect(screen, dialog_rect, DARK_BLUE, radius=20)
            
            # Dialog title
            draw_text(screen, "Edit Username", font_medium, WHITE, WIDTH//2, HEIGHT//2 - 70)
            
            # Input field
            pygame.draw.rect(screen, WHITE if active_input else LIGHT_BLUE, input_rect, 0, 5)
            draw_text(screen, input_text, font_small, BLACK, WIDTH//2, HEIGHT//2)
            
            # Save and Cancel buttons
            save_button = draw_button(screen, "Save", pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 50, 100, 40), GREEN)
            cancel_button = draw_button(screen, "Cancel", pygame.Rect(WIDTH//2 + 10, HEIGHT//2 + 50, 100, 40), RED)
            
            # Handle events for username edit
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if input_rect.collidepoint(event.pos):
                        active_input = True
                    else:
                        active_input = False
                        
                    if save_button.collidepoint(event.pos):
                        # Validate and save the new username
                        if len(input_text) >= 3:
                            success, message = auth.update_username(user_id, input_text)
                            if success:
                                username = input_text  # Update the username
                                current_state = PROFILE
                                message_box = {"text": message, "color": GREEN}
                                message_timeout = pygame.time.get_ticks() + 3000  # Show for 3 seconds
                            else:
                                message_box = {"text": message, "color": RED}
                                message_timeout = pygame.time.get_ticks() + 3000
                        else:
                            message_box = {"text": "Username must be at least 3 characters", "color": RED}
                            message_timeout = pygame.time.get_ticks() + 3000
                    
                    if cancel_button.collidepoint(event.pos):
                        current_state = PROFILE
                        active_input = False
                
                if event.type == pygame.KEYDOWN:
                    if active_input:
                        if event.key == pygame.K_RETURN:
                            # Validate and save the new username
                            if len(input_text) >= 3:
                                success, message = auth.update_username(user_id, input_text)
                                if success:
                                    username = input_text  # Update the username
                                    current_state = PROFILE
                                    message_box = {"text": message, "color": GREEN}
                                    message_timeout = pygame.time.get_ticks() + 3000
                                else:
                                    message_box = {"text": message, "color": RED}
                                    message_timeout = pygame.time.get_ticks() + 3000
                            else:
                                message_box = {"text": "Username must be at least 3 characters", "color": RED}
                                message_timeout = pygame.time.get_ticks() + 3000
                        elif event.key == pygame.K_BACKSPACE:
                            input_text = input_text[:-1]
                        elif event.key == pygame.K_ESCAPE:
                            current_state = PROFILE
                            active_input = False
                        else:
                            # Limit username length to 15 characters
                            if len(input_text) < 15:
                                input_text += event.unicode
        
        # Display confirmation dialog if active
        if confirmation_dialog:
            # Draw overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            # Draw dialog box
            dialog_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 100, 400, 200)
            draw_rounded_rect(screen, dialog_rect, DARK_BLUE, radius=20)
            
            # Dialog title and message
            draw_text(screen, confirmation_dialog["title"], font_medium, WHITE, WIDTH//2, HEIGHT//2 - 70)
            
            # Draw the wrapped confirmation message
            message_lines = wrap_text(confirmation_dialog["message"], font_small, 350)
            line_height = 25
            start_y = HEIGHT//2 - 40
            
            for i, line in enumerate(message_lines):
                draw_text(screen, line, font_small, WHITE, WIDTH//2, start_y + i * line_height)
            
            # Yes and No buttons
            yes_button = draw_button(screen, "Yes", confirmation_dialog["yes_rect"], RED)
            no_button = draw_button(screen, "No", confirmation_dialog["no_rect"], GREEN)
            
            # Handle confirmation dialog events
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if yes_button.collidepoint(event.pos):
                        # Delete account
                        success, message = auth.delete_account(user_id)
                        if success:
                            # Log out and return to login screen
                            return "LOGIN"
                        else:
                            message_box = {"text": message, "color": RED}
                            message_timeout = pygame.time.get_ticks() + 3000
                        confirmation_dialog = None
                    
                    if no_button.collidepoint(event.pos):
                        confirmation_dialog = None
        
        # Display message box if active
        if message_box and pygame.time.get_ticks() < message_timeout:
            msg_rect = pygame.Rect(WIDTH//2 - 200, 30, 400, 40)
            draw_rounded_rect(screen, msg_rect, message_box["color"], radius=10, alpha=200)
            draw_text(screen, message_box["text"], font_small, WHITE, WIDTH//2, 50)
        
        # Update display
        pygame.display.flip()
    
    return "QUIT"
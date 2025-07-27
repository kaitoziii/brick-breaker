import pygame
import random
import math

# Cheat mode flags and variables
CHEAT_ENABLED = False
CHEAT_KEYS = {
    'MULTIPLY_BALLS': pygame.K_m,  # Press 'M' to multiply balls
    'CLEAR_BRICKS': pygame.K_c,    # Press 'C' to clear all bricks
    'GOD_MODE': pygame.K_g,        # Press 'G' for infinite lives
    'LEVEL_UP': pygame.K_l,        # Press 'L' to force level up
    'TOGGLE_CHEAT': pygame.K_F12   # Press F12 to toggle cheat mode
}

# Notification variables
notification_text = ""
notification_start_time = 0
notification_duration = 2000  # 2 seconds

def toggle_cheat_mode():
    """Toggle the cheat mode on/off"""
    global CHEAT_ENABLED, notification_text, notification_start_time
    CHEAT_ENABLED = not CHEAT_ENABLED
    
    # Set notification text and start time
    notification_text = "CHEAT MODE ACTIVATED!" if CHEAT_ENABLED else "CHEAT MODE DEACTIVATED"
    notification_start_time = pygame.time.get_ticks()
    
    print(f"Cheat mode {'enabled' if CHEAT_ENABLED else 'disabled'}")
    return CHEAT_ENABLED

def is_cheat_enabled():
    """Check if cheat mode is enabled"""
    return CHEAT_ENABLED

def handle_cheat_keys(event, game_state):
    """
    Handle cheat key presses and modify game state accordingly
    
    Parameters:
    - event: pygame event
    - game_state: dict containing game state variables
    
    Returns:
    - Modified game_state
    """
    global notification_text, notification_start_time
    
    # Always handle F12 for toggling cheat mode
    if event.type == pygame.KEYDOWN and event.key == CHEAT_KEYS['TOGGLE_CHEAT']:
        toggle_cheat_mode()
        return game_state
    
    if not CHEAT_ENABLED or event.type != pygame.KEYDOWN:
        return game_state
    
    # Proceed only if cheat mode is enabled
    # Multiply balls
    if event.key == CHEAT_KEYS['MULTIPLY_BALLS']:
        for _ in range(5):  # Add 5 more balls
            if len(game_state['balls']) < 20:  # Limit to 20 balls to prevent performance issues
                new_ball = pygame.Rect(
                    game_state['paddle'].centerx, 
                    game_state['paddle'].top - 20, 
                    game_state['BALL_RADIUS']*2, 
                    game_state['BALL_RADIUS']*2
                )
                
                # Generate random velocity
                angle = random.uniform(0.5, 2.5)  # Random angle in radians
                speed = game_state['base_speed']
                dx = speed * math.cos(angle)
                dy = -speed * math.sin(angle)  # Negative because y increases downward in pygame
                
                game_state['balls'].append(new_ball)
                game_state['ball_velocities'].append((dx, dy))
        
        notification_text = f"ADDED BALLS! Total: {len(game_state['balls'])}"
        notification_start_time = pygame.time.get_ticks()
        print(f"Cheat: Added balls. Total: {len(game_state['balls'])}")
    
    # Clear all bricks
    elif event.key == CHEAT_KEYS['CLEAR_BRICKS']:
        # Leave just one brick to break
        if len(game_state['bricks']) > 1:
            game_state['bricks'] = [game_state['bricks'][0]]
            notification_text = "CLEARED BRICKS! Only one remains."
            notification_start_time = pygame.time.get_ticks()
        print("Cheat: Cleared bricks. Only one remains.")
    
    # God mode (infinite lives)
    elif event.key == CHEAT_KEYS['GOD_MODE']:
        game_state['lives'] = 999
        notification_text = "GOD MODE ENABLED! Lives set to 999."
        notification_start_time = pygame.time.get_ticks()
        print("Cheat: God mode enabled. Lives set to 999.")
    
    # Force level up
    elif event.key == CHEAT_KEYS['LEVEL_UP']:
        # Set up for level transition
        game_state['bricks'] = []  # Clear all bricks
        game_state['level_cleared'] = True
        game_state['level'] += 1
        game_state['level_transition_message_time'] = pygame.time.get_ticks() + 2000
        game_state['last_refill_time'] = pygame.time.get_ticks()
        
        # Set up new bricks for the next level
        rows = min(10, 3 + game_state['level'])
        cols = 10
        
        brick_width = (game_state['WIDTH'] - 100) // cols
        brick_height = 20
        
        # Generate new bricks with staggered appearance
        new_bricks = []
        for row in range(rows):
            for col in range(cols):
                brick = pygame.Rect(
                    50 + col * brick_width,
                    50 + row * (brick_height + 5),
                    brick_width - 5,
                    brick_height
                )
                new_bricks.append(brick)
        
        # Randomize the order for a more interesting refill animation
        random.shuffle(new_bricks)
        game_state['new_bricks'] = new_bricks
        
        notification_text = f"LEVEL UP! Now at level {game_state['level']}"
        notification_start_time = pygame.time.get_ticks()
        print(f"Cheat: Level up to level {game_state['level']}")
    
    return game_state

def draw_cheat_status(screen, font):
    """Draw cheat mode status indicator and notifications"""
    global notification_text, notification_start_time
    
    current_time = pygame.time.get_ticks()
    
    if CHEAT_ENABLED:
        # Draw a small indicator that cheat mode is active
        pygame.draw.rect(screen, (255, 0, 0), (screen.get_width() - 20, 10, 10, 10))
        
        # Draw cheat commands
        text = font.render("CHEAT MODE", True, (255, 100, 100))
        screen.blit(text, (screen.get_width() - 120, 10))
        
        # Display available commands (small text)
        small_font = pygame.font.SysFont(None, 18)
        commands = [
            "M: Multiply Balls",
            "C: Clear Bricks",
            "G: God Mode",
            "L: Level Up",
            "F12: Toggle Cheat"
        ]
        
        for i, cmd in enumerate(commands):
            cmd_text = small_font.render(cmd, True, (200, 200, 200))
            screen.blit(cmd_text, (screen.get_width() - 120, 30 + i * 15))
    
    # Display notification if it's active
    if notification_text and current_time - notification_start_time < notification_duration:
        # Calculate alpha for fade-out effect
        alpha = 255
        time_passed = current_time - notification_start_time
        if time_passed > notification_duration * 0.7:  # Start fading out after 70% of the duration
            fade_period = notification_duration * 0.3
            alpha = 255 * (1 - (time_passed - notification_duration * 0.7) / fade_period)
            alpha = max(0, min(255, alpha))  # Clamp between 0 and 255
        
        # Create semi-transparent notification box
        notification_font = pygame.font.SysFont(None, 36)
        notification_surface = notification_font.render(notification_text, True, (255, 255, 0))
        text_width, text_height = notification_surface.get_size()
        
        # Position in center top of screen
        x = screen.get_width() // 2 - text_width // 2
        y = 50
        
        # Draw background box
        padding = 10
        box_rect = pygame.Rect(x - padding, y - padding, text_width + padding*2, text_height + padding*2)
        box_surface = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
        box_surface.fill((0, 0, 0, int(180 * alpha / 255)))
        screen.blit(box_surface, box_rect)
        
        # Draw border
        pygame.draw.rect(screen, (255, 255, 0, int(alpha)), box_rect, 2, border_radius=5)
        
        # Apply alpha to text
        notification_surface.set_alpha(int(alpha))
        screen.blit(notification_surface, (x, y))

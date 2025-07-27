import pygame
import random
import math
import time
import sys
from leaderboard import update_score
from events import trigger_special_event

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
FPS = 60

# Enhanced color palette
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BG = (15, 20, 35)
BRICK_COLORS = [
    (220, 50, 50),   # Red
    (220, 120, 50),  # Orange
    (220, 180, 50),  # Yellow
    (50, 180, 80),   # Green
    (50, 120, 180),  # Blue
]
PADDLE_COLOR = (80, 200, 230)
PADDLE_GLOW = (120, 220, 255)
BALL_COLOR = (240, 240, 240)
BALL_GLOW = (200, 200, 255)
RED = (220, 60, 60)
GREEN = (60, 200, 100)
BLUE = (60, 130, 200)
PURPLE = (150, 70, 200)
GRAY = (150, 150, 150)

# Game objects
PADDLE_WIDTH, PADDLE_HEIGHT = 100, 15
BALL_RADIUS = 8
BRICK_WIDTH, BRICK_HEIGHT = 70, 25

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Brick Breaker")

# Better fonts
try:
    font = pygame.font.Font("freesansbold.ttf", 36)
    small_font = pygame.font.Font("freesansbold.ttf", 24)
except:
    font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 24)

# Particle system
particles = []
brick_particles = []
special_effect_particles = []

def draw_text(text, x, y, color=WHITE, font_size=None):
    text_font = font if font_size is None else pygame.font.SysFont(None, font_size)
    text_surface = text_font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

def create_button(rect, text, text_color=WHITE, button_color=BLUE, hover_color=GREEN):
    mouse_pos = pygame.mouse.get_pos()
    color = hover_color if rect.collidepoint(mouse_pos) else button_color
    
    # Draw button with rounded corners
    pygame.draw.rect(screen, color, rect, border_radius=8)
    
    # Button border
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=8)
    
    # Center text on button
    font_size = 28
    text_surface = pygame.font.SysFont(None, font_size).render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)
    
    return rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]

def draw_background():
    # Create a gradient background
    for y in range(HEIGHT):
        # Calculate colors for a more dynamic gradient
        progress = y / HEIGHT
        r = int(15 * (1 - progress*0.7))
        g = int(20 * (1 - progress*0.7))
        b = int(35 + 20 * (1 - progress*0.7))
        color = (r, g, b)
        pygame.draw.line(screen, color, (0, y), (WIDTH, y))
    
    # Add some subtle stars in the background
    for i in range(50):
        x = (i * 37 + pygame.time.get_ticks() // 50) % WIDTH
        y = (i * 23 + pygame.time.get_ticks() // 100) % HEIGHT
        size = random.random() * 2
        brightness = 50 + int((math.sin(pygame.time.get_ticks() / 1000 + i) + 1) * 25)
        pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), size)

def create_particle(x, y, color, speed=1, size=3, life=30):
    angle = random.uniform(0, math.pi * 2)
    speed_x = math.cos(angle) * speed
    speed_y = math.sin(angle) * speed
    return {
        'x': x, 
        'y': y,
        'speed_x': speed_x,
        'speed_y': speed_y,
        'size': size,
        'color': color,
        'life': life
    }

def update_particles():
    # Update ball trail particles
    for i, p in enumerate(particles[:]):
        p['life'] -= 1
        if p['life'] <= 0:
            particles.remove(p)
            continue
        
        p['x'] += p['speed_x']
        p['y'] += p['speed_y']
        p['size'] *= 0.95
        
        # Draw particle
        alpha = min(255, p['life'] * 8)
        pygame.draw.circle(screen, p['color'] + (alpha,), (int(p['x']), int(p['y'])), p['size'])
    
    # Update brick explosion particles
    for i, p in enumerate(brick_particles[:]):
        p['life'] -= 1
        if p['life'] <= 0:
            brick_particles.remove(p)
            continue
        
        p['x'] += p['speed_x']
        p['y'] += p['speed_y']
        p['speed_y'] += 0.1  # Add gravity
        
        # Draw particle
        alpha = min(255, p['life'] * 8)
        pygame.draw.circle(screen, p['color'] + (alpha,), (int(p['x']), int(p['y'])), p['size'])
    
    # Update special effect particles
    for i, p in enumerate(special_effect_particles[:]):
        p['life'] -= 1
        if p['life'] <= 0:
            special_effect_particles.remove(p)
            continue
        
        p['x'] += p['speed_x']
        p['y'] += p['speed_y']
        
        # Draw particle
        alpha = min(255, p['life'] * 8)
        size = p['size'] * (1 + math.sin(pygame.time.get_ticks() / 200 + i) * 0.2)
        pygame.draw.circle(screen, p['color'] + (alpha,), (int(p['x']), int(p['y'])), size)

def draw_paddle(paddle, special_active):
    # Create a glow effect for the paddle
    glow_rect = pygame.Rect(paddle.x - 5, paddle.y - 5, paddle.width + 10, paddle.height + 10)
    
    # Different glow for special powers
    glow_color = PADDLE_GLOW
    if special_active == "big_paddle":
        glow_color = (180, 220, 120)  # Green glow for big paddle
    elif special_active:
        glow_color = (220, 180, 120)  # Orange glow for other specials
    
    # Draw multiple layers for glow effect
    for i in range(3):
        g_rect = pygame.Rect(glow_rect.x + i, glow_rect.y + i, glow_rect.width - i*2, glow_rect.height - i*2)
        pygame.draw.rect(screen, glow_color + (100 - i*30,), g_rect, border_radius=8)
    
    # Draw the main paddle
    pygame.draw.rect(screen, PADDLE_COLOR, paddle, border_radius=7)
    
    # Add a shine effect
    shine_height = paddle.height // 2
    shine_rect = pygame.Rect(paddle.x, paddle.y, paddle.width, shine_height)
    
    for i in range(shine_height):
        progress = i / shine_height
        alpha = int(80 * (1 - progress))
        pygame.draw.line(screen, (255, 255, 255, alpha), 
                         (paddle.x, paddle.y + i), 
                         (paddle.x + paddle.width, paddle.y + i))

def draw_ball(ball, ball_dx, ball_dy):
    # Ball glow
    glow_radius = BALL_RADIUS * 1.5
    for i in range(3):
        size = glow_radius - i
        alpha = 150 - i*40
        pygame.draw.circle(screen, BALL_GLOW + (alpha,), ball.center, size)
    
    # Main ball
    pygame.draw.circle(screen, BALL_COLOR, ball.center, BALL_RADIUS)
    
    # Ball shine
    shine_pos = (ball.centerx - BALL_RADIUS//3, ball.centery - BALL_RADIUS//3)
    pygame.draw.circle(screen, (255, 255, 255), shine_pos, BALL_RADIUS//3)
    
    # Add particle trail
    if random.random() < 0.3:
        particles.append(create_particle(
            ball.centerx, ball.centery,
            BALL_COLOR, 
            speed=0.5,
            size=BALL_RADIUS * 0.7,
            life=15
        ))

def draw_bricks(bricks):
    for i, brick in enumerate(bricks):
        # Vary brick colors by row
        row = i // 10
        color = BRICK_COLORS[row % len(BRICK_COLORS)]
        
        # Draw brick with gradient
        pygame.draw.rect(screen, color, brick, border_radius=4)
        
        # Add highlight to top edge
        highlight_rect = pygame.Rect(brick.x, brick.y, brick.width, 5)
        pygame.draw.rect(screen, (255, 255, 255, 100), highlight_rect, border_radius=4)
        
        # Add shadow to bottom edge
        shadow_rect = pygame.Rect(brick.x, brick.y + brick.height - 5, brick.width, 5)
        pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=4)

def create_brick_particles(brick):
    color = BRICK_COLORS[(brick.y // BRICK_HEIGHT) % len(BRICK_COLORS)]
    for _ in range(10):
        brick_particles.append(create_particle(
            brick.centerx, brick.centery,
            color, 
            speed=random.uniform(1, 3),
            size=random.uniform(2, 5),
            life=random.randint(20, 40)
        ))

def create_special_effect(x, y, special_type):
    color = (220, 220, 120)  # Default yellow
    if special_type == "big_paddle":
        color = (100, 220, 100)  # Green
    elif special_type == "score_boost":
        color = (220, 180, 100)  # Orange
    elif special_type == "multi_ball":
        color = (100, 180, 220)  # Blue
    
    for _ in range(20):
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(0.5, 2)
        speed_x = math.cos(angle) * speed
        speed_y = math.sin(angle) * speed
        
        special_effect_particles.append({
            'x': x,
            'y': y,
            'speed_x': speed_x,
            'speed_y': speed_y,
            'size': random.uniform(3, 7),
            'color': color,
            'life': random.randint(30, 60)
        })

def draw_special_indicator(special_active, special_timer):
    if not special_active:
        return
    
    # Calculate remaining time
    elapsed = pygame.time.get_ticks() - special_timer
    remaining = max(0, 5000 - elapsed)
    progress = remaining / 5000
    
    # Draw indicator in top-right corner
    indicator_width = 150
    indicator_height = 25
    x = WIDTH - indicator_width - 10
    y = 50
    
    # Draw background
    pygame.draw.rect(screen, (50, 50, 70, 200), 
                     pygame.Rect(x, y, indicator_width, indicator_height), 
                     border_radius=5)
    
    # Draw progress bar
    progress_width = int(indicator_width * progress)
    
    # Choose color based on special type
    bar_color = (220, 220, 120)  # Default yellow
    if special_active == "big_paddle":
        bar_color = (100, 220, 100)  # Green
    elif special_active == "score_boost":
        bar_color = (220, 180, 100)  # Orange
    elif special_active == "multi_ball":
        bar_color = (100, 180, 220)  # Blue
    
    pygame.draw.rect(screen, bar_color, 
                     pygame.Rect(x, y, progress_width, indicator_height), 
                     border_radius=5)
    
    # Draw border
    pygame.draw.rect(screen, WHITE, 
                     pygame.Rect(x, y, indicator_width, indicator_height), 
                     width=1, border_radius=5)
    
    # Draw text
    special_name = special_active.replace("_", " ").title()
    draw_text(special_name, x + indicator_width//2, y + indicator_height//2, WHITE, 20)

def apply_bounce_randomness(dx, dy, randomness=0.2):
    # Add a small random variation to the angle while preserving speed
    speed = math.sqrt(dx**2 + dy**2)
    angle = math.atan2(dy, dx)
    
    # Add random angle variation (within limits)
    angle_variation = random.uniform(-randomness, randomness)
    new_angle = angle + angle_variation
    
    # Convert back to velocity components
    new_dx = math.cos(new_angle) * speed
    new_dy = math.sin(new_angle) * speed
    
    return new_dx, new_dy

def start(user_id):
    clock = pygame.time.Clock()

    # Paddle
    paddle = pygame.Rect(WIDTH // 2 - PADDLE_WIDTH // 2, HEIGHT - 40, PADDLE_WIDTH, PADDLE_HEIGHT)
    
    # Main ball and multiple balls support
    main_ball = pygame.Rect(WIDTH // 2, HEIGHT // 2, BALL_RADIUS*2, BALL_RADIUS*2)
    balls = [main_ball]  # List to store all active balls
    ball_velocities = [(5, -5)]  # List of (dx, dy) for each ball
    
    # Bricks
    bricks = []
    for i in range(5):
        for j in range(10):
            bricks.append(pygame.Rect(j * (BRICK_WIDTH + 5) + 35, i * (BRICK_HEIGHT + 5) + 35, BRICK_WIDTH, BRICK_HEIGHT))

    running = True
    game_over = False
    paused = False
    score = 0
    special_active = None
    special_timer = 0
    return_to_menu = False
    collision_cooldown = 0  # Add collision cooldown counter
    
    # New variables for level transition
    level = 1
    level_cleared = False
    refill_timer = 0
    refill_delay = 100  # Time between adding each brick (ms)
    last_refill_time = 0
    new_bricks = []
    level_transition_message_time = 0
    starting_ball_pos = (WIDTH // 2, HEIGHT // 2)
    starting_paddle_pos = WIDTH // 2 - PADDLE_WIDTH // 2
    
    # Multi-ball variables
    multi_ball_spawned = False
    multi_ball_spawn_time = 0
    
    # Function to reset game state
    def reset_game_state():
        nonlocal balls, ball_velocities, paddle, bricks, score, special_active, special_timer, collision_cooldown, multi_ball_spawned
        score = 0
        
        # Reset to single ball
        balls = [pygame.Rect(WIDTH // 2, HEIGHT // 2, BALL_RADIUS*2, BALL_RADIUS*2)]
        ball_velocities = [(5, -5)]
        
        paddle.x = WIDTH // 2 - PADDLE_WIDTH // 2
        paddle.width = PADDLE_WIDTH  # Reset paddle size
        # Reset bricks
        bricks.clear()
        for i in range(5):
            for j in range(10):
                bricks.append(pygame.Rect(j * (BRICK_WIDTH + 5) + 35, i * (BRICK_HEIGHT + 5) + 35, BRICK_WIDTH, BRICK_HEIGHT))
        special_active = None
        special_timer = 0
        collision_cooldown = 0  # Reset collision cooldown when game resets
        multi_ball_spawned = False  # Reset multi-ball state
        # Clear particles
        particles.clear()
        brick_particles.clear()
        special_effect_particles.clear()
        
    # Function to create new bricks for the next level
    def create_new_bricks():
        new_bricks = []
        for i in range(5):
            for j in range(10):
                new_bricks.append(pygame.Rect(j * (BRICK_WIDTH + 5) + 35, i * (BRICK_HEIGHT + 5) + 35, BRICK_WIDTH, BRICK_HEIGHT))
        return new_bricks

    # Pause button
    pause_button = pygame.Rect(WIDTH - 120, 10, 110, 30)
    
    # Menu buttons
    play_again_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 30, 200, 40)
    restart_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 80, 200, 40)
    back_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 130, 200, 40)
    
    # Track button clicks for better detection
    button_pressed = False
    
    # Helper function to spawn additional balls for multi-ball power-up
    def spawn_multi_balls(ball, count=2):
        nonlocal balls, ball_velocities, multi_ball_spawned
        
        # Only spawn new balls if we haven't already for this power-up
        if not multi_ball_spawned:
            multi_ball_spawned = True
            
            # Create the additional balls
            for i in range(count):
                # Create a new ball at the same position as the current ball
                new_ball = pygame.Rect(ball.x, ball.y, BALL_RADIUS*2, BALL_RADIUS*2)
                
                # Give the new ball a different velocity direction
                angle = math.pi/4 + i * math.pi/2  # Spread the balls at different angles
                speed = 6  # Slightly faster than normal
                dx = math.cos(angle) * speed
                dy = -math.sin(angle) * speed  # Negative to go up
                
                # Add the new ball and its velocity
                balls.append(new_ball)
                ball_velocities.append((dx, dy))
                
                # Create particle effect for the new ball
                for _ in range(10):
                    particles.append(create_particle(
                        new_ball.centerx, 
                        new_ball.centery, 
                        BALL_COLOR, 
                        speed=random.uniform(1, 2.5),
                        life=30
                    ))
    
    while running:
        clock.tick(FPS)
        
        # Draw the background
        draw_background()
        
        # Reset button_pressed state on new frame
        if not pygame.mouse.get_pressed()[0]:
            button_pressed = False

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                # Spacebar or P key to pause/unpause
                if (event.key == pygame.K_SPACE or event.key == pygame.K_p) and not game_over:
                    paused = not paused
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Check if pause button was clicked
                    if pause_button.collidepoint(mouse_pos) and not game_over:
                        paused = not paused
                    
                    # Handle restart button click
                    if restart_button.collidepoint(mouse_pos) and not button_pressed:
                        button_pressed = True
                        print("Restart button clicked!")  # Debugging
                        reset_game_state()
                        game_over = False  # Always set game_over to false to restart
                        paused = False     # Always unpause when restarting

        # Draw pause button (only if game is not over)
        if not game_over:
            # Draw a nicer pause button
            pygame.draw.rect(screen, GREEN if not paused else RED, pause_button, border_radius=7)
            # Add border
            pygame.draw.rect(screen, WHITE, pause_button, 1, border_radius=7)
            # Center text in pause button
            draw_text("PAUSE" if not paused else "RESUME", pause_button.centerx, pause_button.centery, WHITE, 24)

        # Draw score
        score_bg = pygame.Rect(60, 10, 120, 30)
        pygame.draw.rect(screen, (30, 30, 60, 180), score_bg, border_radius=7)
        pygame.draw.rect(screen, WHITE, score_bg, 1, border_radius=7)
        draw_text(f"Score: {score}", 120, 25, WHITE, 24)

        if game_over:
            # Game over screen with improved visuals
            # Semi-transparent overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            # Game over card
            card_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 200, 400, 400)
            pygame.draw.rect(screen, (30, 30, 60, 230), card_rect, border_radius=15)
            pygame.draw.rect(screen, (200, 60, 60), card_rect, 2, border_radius=15)
            
            # Game over text with glow
            draw_text("GAME OVER", WIDTH // 2, HEIGHT // 2 - 150, RED, 48)
            draw_text(f"Final Score: {score}", WIDTH // 2, HEIGHT // 2 - 100, WHITE)
            
            # Draw buttons for Game Over screen
            if create_button(play_again_button, "Play Again"):
                game_over = False
                reset_game_state()
            
            if create_button(restart_button, "Restart"):
                reset_game_state()
                game_over = False
                paused = False
            
            if create_button(back_button, "Back to Menu"):
                return_to_menu = True
                running = False
            
            pygame.display.flip()
            continue

        if paused:
            # Pause screen with improved visuals
            # Semi-transparent overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            # Pause card
            card_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 200, 400, 400)
            pygame.draw.rect(screen, (30, 30, 60, 230), card_rect, border_radius=15)
            pygame.draw.rect(screen, (60, 100, 200), card_rect, 2, border_radius=15)
            
            # Pause text
            draw_text("GAME PAUSED", WIDTH // 2, HEIGHT // 2 - 150, WHITE, 48)
            
            # Draw buttons for Pause screen
            if create_button(play_again_button, "Continue"):
                paused = False
            
            if create_button(restart_button, "Restart"):
                reset_game_state()
                game_over = False
                paused = False
            
            if create_button(back_button, "Back to Menu"):
                return_to_menu = True
                running = False
            
            pygame.display.flip()
            continue

        # Handle level transition and block refill animation
        if level_cleared:
            current_time = pygame.time.get_ticks()
            
            # Check if power-up expires during level transition
            if special_active and current_time - special_timer > 5000:
                special_active = None
                paddle.width = PADDLE_WIDTH
                multi_ball_spawned = False
            
            # Show level completion message
            if current_time < level_transition_message_time:
                # Semi-transparent message box
                msg_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 50, 400, 100)
                pygame.draw.rect(screen, (30, 30, 60, 200), msg_rect, border_radius=15)
                pygame.draw.rect(screen, (60, 200, 100), msg_rect, 2, border_radius=15)
                
                # Level completion text
                draw_text(f"LEVEL {level-1} COMPLETED!", WIDTH // 2, HEIGHT // 2 - 20, GREEN, 36)
                draw_text(f"Level {level} starting...", WIDTH // 2, HEIGHT // 2 + 20, WHITE, 28)
            
            # No paddle movement during transition - paddle stays centered
            
            # Gradually add new bricks with animation
            if new_bricks and current_time - last_refill_time > refill_delay:
                # Add a new brick from the prepared list
                brick = new_bricks.pop(0)
                bricks.append(brick)
                last_refill_time = current_time
                
                # Create special appearance effect for the new brick
                for _ in range(5):
                    particles.append(create_particle(
                        brick.centerx, 
                        brick.centery, 
                        BRICK_COLORS[min(4, level-1) % len(BRICK_COLORS)], 
                        speed=random.uniform(0.5, 1.5), 
                        size=random.uniform(2, 4), 
                        life=30
                    ))
            
            # When all bricks are refilled, resume normal gameplay
            if not new_bricks:
                level_cleared = False
                
                # Reset ball and paddle to starting positions
                # For multi-ball, keep only the first ball
                balls = [pygame.Rect(starting_ball_pos[0], starting_ball_pos[1], BALL_RADIUS*2, BALL_RADIUS*2)]
                ball_velocities = [(5, -5)]
                
                paddle.x = starting_paddle_pos
                
                # Reset ball velocity (with slightly increased speed for higher levels)
                base_speed = 5 + (level - 1) * 0.5  # Increase speed with each level
                ball_velocities[0] = (base_speed, -base_speed)
                
                # Add bonus points for completing a level
                score += level * 50
                
                # Shrink paddle slightly for added difficulty (but not too much)
                if paddle.width > PADDLE_WIDTH * 0.7 and not special_active:
                    paddle.width = max(PADDLE_WIDTH * 0.9, paddle.width - 5)
                elif special_active == "big_paddle":
                    # Ensure the paddle remains big if power-up is active
                    paddle.width = 150
            
            # Draw the current state of bricks being filled
            draw_paddle(paddle, special_active)
            # Draw all balls
            for ball in balls:
                draw_ball(ball, 0, 0)  # Show ball but don't indicate movement
            draw_bricks(bricks)
            update_particles()
            
            # Always show power-up indicator during level transition if active
            if special_active:
                draw_special_indicator(special_active, special_timer)
            
            # Continue to next frame, skipping normal ball movement
            pygame.display.flip()
            continue
            
        # Move paddle - ONLY if not in level transition
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and paddle.left > 0:
            paddle.move_ip(-10, 0)
        if keys[pygame.K_RIGHT] and paddle.right < WIDTH:
            paddle.move_ip(10, 0)

        # Move and handle collision for all balls
        balls_to_remove = []
        for i, ball in enumerate(balls):
            ball_dx, ball_dy = ball_velocities[i]
            
            # Move ball
            ball.x += ball_dx
            ball.y += ball_dy

            # Collision with walls
            if ball.left <= 0 or ball.right >= WIDTH:
                # Reverse x direction with slight randomization
                new_dx, new_dy = apply_bounce_randomness(-ball_dx, ball_dy)
                ball_velocities[i] = (new_dx, new_dy)
                
                # Add collision particles
                for _ in range(5):
                    particles.append(create_particle(ball.centerx, ball.centery, BALL_COLOR, 
                                                   speed=random.uniform(1, 2), life=15))
                    
            if ball.top <= 0:
                # Reverse y direction with slight randomization
                new_dx, new_dy = apply_bounce_randomness(ball_dx, -ball_dy)
                ball_velocities[i] = (new_dx, new_dy)
                
                # Add collision particles
                for _ in range(5):
                    particles.append(create_particle(ball.centerx, ball.centery, BALL_COLOR, 
                                                   speed=random.uniform(1, 2), life=15))
                    
            if ball.bottom >= HEIGHT:
                # Ball missed the paddle - remove this ball
                balls_to_remove.append(i)
                # Add explosion effect
                for _ in range(10):
                    particles.append(create_particle(ball.centerx, ball.centery, RED, 
                                                   speed=random.uniform(2, 3), life=20))
                continue  # Skip rest of processing for this ball

            # Collision with paddle
            if ball.colliderect(paddle) and collision_cooldown == 0:
                # Ensure the ball is above the paddle to prevent getting stuck inside
                if ball.centery < paddle.top:
                    ball.bottom = paddle.top - 1  # Position ball just above paddle
                    
                    # Angle the bounce based on where it hit the paddle
                    hit_pos = (ball.centerx - paddle.left) / paddle.width
                    angle = math.pi * (0.25 + 0.5 * hit_pos)  # Between pi/4 and 3pi/4
                    speed = math.sqrt(ball_dx**2 + ball_dy**2)
                    ball_velocities[i] = (math.cos(angle) * speed, -math.sin(angle) * speed)
                    
                    collision_cooldown = 5  # Set cooldown to prevent multiple collisions
                    
                    # Add collision particles
                    for _ in range(8):
                        particles.append(create_particle(ball.centerx, ball.centery, PADDLE_COLOR, 
                                                      speed=random.uniform(1, 2), life=15))
                        
                # If ball hits from below or sides (rare case), just reverse direction
                elif ball.centery > paddle.bottom:
                    ball.top = paddle.bottom + 1  # Position ball just below paddle
                    ball_velocities[i] = (ball_dx, abs(ball_dy))  # Ensure ball goes downward
                    collision_cooldown = 5
                    
                # Side collision
                else:
                    ball_velocities[i] = (-ball_dx, ball_dy)  # Reverse horizontal direction for side hits
                    collision_cooldown = 5

            # Collision with bricks
            hit_index = ball.collidelist(bricks)
            if hit_index != -1 and collision_cooldown == 0:
                # Get the brick that was hit
                hit_brick = bricks[hit_index]
                
                # Create particle effect for brick breaking
                create_brick_particles(hit_brick)
                
                # Determine collision direction and respond accordingly
                # Top or bottom collision
                if abs(ball.bottom - hit_brick.top) < 10 or abs(ball.top - hit_brick.bottom) < 10:
                    # Reverse y direction with randomization
                    new_dx, new_dy = apply_bounce_randomness(ball_dx, -ball_dy)
                    ball_velocities[i] = (new_dx, new_dy)
                # Side collision
                elif abs(ball.right - hit_brick.left) < 10 or abs(ball.left - hit_brick.right) < 10:
                    # Reverse x direction with randomization
                    new_dx, new_dy = apply_bounce_randomness(-ball_dx, ball_dy)
                    ball_velocities[i] = (new_dx, new_dy)
                # Corner collision or other cases
                else:
                    # Default to vertical bounce with randomization
                    new_dx, new_dy = apply_bounce_randomness(ball_dx, -ball_dy)
                    ball_velocities[i] = (new_dx, new_dy)
                
                # Remove brick and add score
                del bricks[hit_index]
                score += 10
                collision_cooldown = 3  # Add cooldown after brick collision too
                
                # Special event trigger - ONLY if no power-up is currently active
                if not special_active:
                    new_special = trigger_special_event()
                    if new_special:
                        special_active = new_special
                        special_timer = pygame.time.get_ticks()
                        multi_ball_spawned = False  # Reset so we can spawn more balls if we get multi-ball again
                        # Create special effect particles
                        create_special_effect(hit_brick.centerx, hit_brick.centery, special_active)

        # Remove any balls that went out of bounds (bottom of screen)
        for i in sorted(balls_to_remove, reverse=True):
            if i < len(balls):
                balls.pop(i)
                ball_velocities.pop(i)
        
        # Game over if all balls are lost
        if not balls:
            game_over = True
            # Save score to database
            update_score(user_id, score)
            
        # Update collision cooldown
        if collision_cooldown > 0:
            collision_cooldown -= 1

        # Apply special events
        if special_active:
            if special_active == "big_paddle":
                paddle.width = 150
            elif special_active == "score_boost":
                score += 5
            elif special_active == "multi_ball":
                # Spawn additional balls if not already spawned for this power-up
                if not multi_ball_spawned:
                    spawn_multi_balls(balls[0])
                    multi_ball_spawn_time = pygame.time.get_ticks()

            # Check if power-up has expired
            current_time = pygame.time.get_ticks()
            if current_time - special_timer > 5000:
                special_active = None
                paddle.width = PADDLE_WIDTH
                # We don't remove the extra balls when the power-up expires
                # Just reset the flag so a new multi-ball power-up can spawn more balls
                multi_ball_spawned = False

        # Win condition
        if not bricks and not level_cleared:
            level_cleared = True
            level += 1
            refill_timer = pygame.time.get_ticks()
            new_bricks = create_new_bricks()
            last_refill_time = pygame.time.get_ticks()
            
            # Store original positions to restore later
            starting_ball_pos = (WIDTH // 2, HEIGHT - 100)
            starting_paddle_pos = WIDTH // 2 - PADDLE_WIDTH // 2
            
            # Freeze ball and paddle position (no movement during transition)
            balls = [pygame.Rect(starting_ball_pos[0], starting_ball_pos[1], BALL_RADIUS*2, BALL_RADIUS*2)]
            ball_velocities = [(5, -5)]
            
            paddle.x = starting_paddle_pos
            
            # Keep track of current power-up state before transition
            # (Don't reset power-ups just because level is cleared)
            
            # Set the level transition message time
            level_transition_message_time = pygame.time.get_ticks() + 3000  # Show for 3 seconds
            
            # Create celebratory particles
            for _ in range(30):
                x = random.randint(0, WIDTH)
                y = random.randint(0, HEIGHT//2)
                color = random.choice(BRICK_COLORS)
                speed = random.uniform(1, 3)
                special_effect_particles.append(create_particle(x, y, color, speed, size=random.uniform(3, 6), life=60))
            
        # Draw game elements
        draw_paddle(paddle, special_active)
        # Draw all balls
        for i, ball in enumerate(balls):
            ball_dx, ball_dy = ball_velocities[i]
            draw_ball(ball, ball_dx, ball_dy)
        draw_bricks(bricks)
        update_particles()

        # Draw power-up indicator
        if special_active:
            draw_special_indicator(special_active, special_timer)
        
        pygame.display.flip()

    if not game_over:  # If game ended normally (quit, not game over)
        update_score(user_id, score)
        
    return return_to_menu

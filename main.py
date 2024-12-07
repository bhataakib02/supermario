import pygame
import random
import sys
import wave
import numpy as np
import os

# Initialize Pygame and Pygame Mixer
pygame.init()
pygame.mixer.init()

# Function to generate sound waves
def generate_sine_wave(frequency, duration, amplitude=0.5, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave_data = amplitude * np.sin(2 * np.pi * frequency * t)
    wave_data = (wave_data * 32767).astype(np.int16)  # convert to 16-bit PCM format
    return wave_data.tobytes()

# Sound effects configurations
sounds = {
    "jump": (880, 0.1),
    "coin": (1200, 0.2),
    "collision": (200, 0.3),
    "game_over": (400, 0.5),
    "start": (600, 0.3)
}

# Create a sound directory if it doesn't exist
sound_dir = os.path.join(os.path.dirname(__file__), 'sounds')
os.makedirs(sound_dir, exist_ok=True)

# Save sound files to the permanent sound directory
file_paths = {}
for name, (frequency, duration) in sounds.items():
    sound_path = os.path.join(sound_dir, f"{name}.wav")
    with wave.open(sound_path, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(44100)
        wav_file.writeframes(generate_sine_wave(frequency, duration))
    file_paths[name] = sound_path

# Load the generated sounds into Pygame
sound_effects = {name: pygame.mixer.Sound(path) for name, path in file_paths.items()}

# Set volume to max for each sound effect (1.0 is the max volume)
for sound in sound_effects.values():
    sound.set_volume(1.0)

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Super Mario-like Game")

# Load images and scale them down
mario_image = pygame.image.load('assets/images/mario.png').convert_alpha()
mario_image = pygame.transform.scale(mario_image, (40, 40))

enemy_image = pygame.image.load('assets/images/enemy.png').convert_alpha()
enemy_image = pygame.transform.scale(enemy_image, (30, 30))

obstacle_image = pygame.image.load('assets/images/obstacle.png').convert_alpha()
obstacle_image = pygame.transform.scale(obstacle_image, (40, 20))

background_image = pygame.image.load('assets/images/background.png').convert_alpha()
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

ground_image = pygame.image.load('assets/images/ground.png').convert_alpha()
ground_image = pygame.transform.scale(ground_image, (WIDTH, 100))

coin_image = pygame.image.load('assets/images/coin.png').convert_alpha()
coin_image = pygame.transform.scale(coin_image, (20, 20))

# Colors
WHITE = (255, 255, 255)

# Game variables
mario_x, mario_y = 50, 450
enemy_x, enemy_y = random.randint(100, WIDTH - 100), 450
score = 0
font = pygame.font.Font(None, 36)
game_over = False
game_started = False

# Speeds
mario_speed = 5
enemy_speed = 2

# Jumping variables
jumping = False
jump_velocity = 20
gravity = 1
on_ground = True
high_jump = False  # To indicate if Mario is making a high jump

# Initialize obstacles and coins
obstacles = []
coins = []

def create_obstacles(num_obstacles):
    """Create obstacles at random positions."""
    global obstacles
    obstacles.clear()
    for _ in range(num_obstacles):
        x_position = random.randint(WIDTH + 100, WIDTH + 300)
        y_position = random.choice([HEIGHT - 120, HEIGHT - 160, HEIGHT - 200])
        obstacles.append([x_position, y_position])

def create_coins(num_coins):
    """Create coins at random positions."""
    global coins
    coins.clear()
    for _ in range(num_coins):
        x_position = random.randint(WIDTH + 100, WIDTH + 300)
        y_position = random.choice([HEIGHT - 140, HEIGHT - 200])
        coins.append([x_position, y_position])

def reset_game():
    """Reset game variables and create initial obstacles and coins."""
    global mario_x, mario_y, enemy_x, enemy_y, score, game_over, game_started
    mario_x, mario_y = 50, 450
    enemy_x, enemy_y = random.randint(100, WIDTH - 100), 450
    score = 0
    game_over = False
    game_started = True
    create_obstacles(5)
    create_coins(3)

def draw_text(text, font, surface, x, y):
    """Draw text on the screen."""
    textobj = font.render(text, True, WHITE)
    surface.blit(textobj, (x, y))

def main():
    """Main game loop."""
    global mario_x, mario_y, jumping, jump_velocity, game_over, score, game_started
    global enemy_x, enemy_y, on_ground, high_score

    clock = pygame.time.Clock()
    high_score = 0
    reset_game()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if game_over:
                        reset_game()
                    else:
                        game_started = True
                        game_over = False
                if event.key in [pygame.K_UP, pygame.K_SPACE]:  # Jump or high jump
                    if on_ground:
                        jumping = True
                        jump_velocity = 20
                        on_ground = False
                    elif not on_ground and not high_jump:  # Allow high jump in the air
                        high_jump = True
                        jump_velocity = 30  # Higher jump velocity for a high jump

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            mario_x -= mario_speed
        if keys[pygame.K_RIGHT]:
            mario_x += mario_speed
        if keys[pygame.K_DOWN] and on_ground:  # Allow crouching only when on the ground
            mario_y += 5  # Crouch down (you can adjust this value)
        
        # Prevent Mario from going out of bounds
        mario_x = max(0, min(mario_x, WIDTH - 40))

        # Reset Mario's vertical position if he falls below the ground
        if mario_y > 450:
            mario_y = 450
            on_ground = True
            high_jump = False  # Reset high jump when landing

        # Game background
        screen.blit(background_image, (0, 0))
        screen.blit(ground_image, (0, HEIGHT - 100))

        if not game_started:
            draw_text('Press ENTER to Start', font, screen, 250, 250)
        else:
            if game_over:
                draw_text('Game Over', font, screen, 300, 250)
                draw_text('Press ENTER to Restart', font, screen, 250, 300)
                draw_text(f'High Score: {high_score}', font, screen, 250, 350)
            else:
                # Jumping logic
                if jumping:
                    mario_y -= jump_velocity
                    jump_velocity -= gravity
                    if jump_velocity <= 0:  # When the jump reaches the peak
                        jumping = False
                else:
                    if not on_ground:  # Only apply gravity if not on ground
                        mario_y += gravity
                        if high_jump:  # If high jumping, apply a faster downward velocity
                            mario_y += 2  # Adjust this value to control how fast he falls

                # Check for ground collision
                if mario_y >= 450:
                    mario_y = 450
                    on_ground = True
                    high_jump = False  # Reset high jump when landing
                else:
                    on_ground = False

                # Move and check collisions for obstacles
                for obstacle in obstacles:
                    obstacle[0] -= 3
                    if obstacle[0] < -40:
                        obstacle[0] = random.randint(WIDTH, WIDTH + 200)
                        obstacle[1] = random.choice([HEIGHT - 120, HEIGHT - 160, HEIGHT - 200])
                    # Collision detection with obstacles
                    if mario_x + 40 > obstacle[0] and mario_x < obstacle[0] + 40:
                        if mario_y + 40 >= obstacle[1] and mario_y + 40 <= obstacle[1] + 10:
                            mario_y = obstacle[1] - 40
                            on_ground = True
                            high_jump = False  # Reset high jump if colliding with an obstacle

                # Move and check collisions for coins
                for coin in coins:
                    coin[0] -= 3
                    if coin[0] < -20:
                        coin[0] = random.randint(WIDTH, WIDTH + 200)
                        coin[1] = random.choice([HEIGHT - 140, HEIGHT - 200])
                    # Collision detection with coins
                    if mario_x + 40 > coin[0] and mario_x < coin[0] + 20:
                        if mario_y + 40 >= coin[1] and mario_y + 40 <= coin[1] + 20:
                            coins.remove(coin)
                            score += 1
                            sound_effects["coin"].play()  # Play coin collection sound

                # Move enemy
                enemy_x -= enemy_speed
                if enemy_x < -30:
                    enemy_x = random.randint(WIDTH + 100, WIDTH + 300)
                # Collision detection with enemy
                if mario_x + 40 > enemy_x and mario_x < enemy_x + 30:
                    if mario_y + 40 >= enemy_y:
                        game_over = True
                        sound_effects["collision"].play()  # Play collision sound

                # Draw Mario, enemy, obstacles, and coins
                screen.blit(mario_image, (mario_x, mario_y))
                screen.blit(enemy_image, (enemy_x, enemy_y))
                for obstacle in obstacles:
                    screen.blit(obstacle_image, (obstacle[0], obstacle[1]))
                for coin in coins:
                    screen.blit(coin_image, (coin[0], coin[1]))
                
                draw_text(f'Score: {score}', font, screen, 10, 10)
                high_score = max(high_score, score)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()

import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Super Mario Bros. Clone")

# Colors
SKY_BLUE = (107, 140, 255)
BROWN = (139, 69, 19)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Game constants
GRAVITY = 0.5
SCROLL_THRESH = 200
TILE_SIZE = 40

# Player class
class Player:
    def __init__(self, x, y):
        self.image = pygame.Surface((30, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True
        self.flip = False
        self.speed = 4
        self.score = 0
        self.lives = 3
        self.level_complete = False

    def update(self, platforms, enemies, coins, pipes, flag):
        dx = 0
        dy = 0

        # Process keypresses
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if key[pygame.K_RIGHT]:
            dx = self.speed
            self.flip = False
            self.direction = 1
        if key[pygame.K_SPACE] and not self.jumped and not self.in_air:
            self.vel_y = -12
            self.jumped = True
            self.in_air = True
        if not key[pygame.K_SPACE]:
            self.jumped = False

        # Add gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # Check for collisions with platforms
        self.in_air = True
        for platform in platforms:
            # Check for collision in x direction
            if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            # Check for collision in y direction
            if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # Check if below the platform (jumping)
                if self.vel_y < 0:
                    dy = platform.rect.bottom - self.rect.top
                    self.vel_y = 0
                # Check if above the platform (falling)
                elif self.vel_y >= 0:
                    dy = platform.rect.top - self.rect.bottom
                    self.vel_y = 0
                    self.in_air = False

        # Check for collisions with pipes
        for pipe in pipes:
            if pipe.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            if pipe.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.vel_y < 0:
                    dy = pipe.rect.bottom - self.rect.top
                    self.vel_y = 0
                elif self.vel_y >= 0:
                    dy = pipe.rect.top - self.rect.bottom
                    self.vel_y = 0
                    self.in_air = False

        # Check for collisions with enemies
        for enemy in enemies:
            if enemy.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                if self.vel_y > 0 and self.rect.bottom < enemy.rect.centery:
                    enemies.remove(enemy)
                    self.vel_y = -6
                    self.score += 100
                else:
                    self.lives -= 1
                    self.rect.x = 100
                    self.rect.y = 300
                    if self.lives <= 0:
                        return "game_over"

        # Check for collisions with coins
        for coin in coins[:]:
            if coin.rect.colliderect(self.rect):
                coins.remove(coin)
                self.score += 50

        # Check for collision with flag
        if flag.rect.colliderect(self.rect):
            self.level_complete = True
            return "level_complete"

        # Update player position
        self.rect.x += dx
        self.rect.y += dy

        # Ensure player doesn't go off the left side of the screen
        if self.rect.left < 0:
            self.rect.left = 0

        return "playing"

    def draw(self, screen, scroll):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), 
                   (self.rect.x - scroll, self.rect.y))

# Platform class
class Platform:
    def __init__(self, x, y, width, height, color=BROWN):
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self, screen, scroll):
        screen.blit(self.image, (self.rect.x - scroll, self.rect.y))

# Enemy class (Goomba)
class Enemy:
    def __init__(self, x, y):
        self.image = pygame.Surface((30, 30))
        self.image.fill((139, 69, 19))  # Brown color
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self, scroll):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if self.move_counter > 50:
            self.move_direction *= -1
            self.move_counter = 0

    def draw(self, screen, scroll):
        screen.blit(self.image, (self.rect.x - scroll, self.rect.y))

# Coin class
class Coin:
    def __init__(self, x, y):
        self.image = pygame.Surface((15, 15), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (7, 7), 7)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.animation_counter = 0

    def update(self):
        self.animation_counter += 0.1
        if self.animation_counter >= 2:
            self.animation_counter = 0

    def draw(self, screen, scroll):
        screen.blit(self.image, (self.rect.x - scroll, self.rect.y))

# Pipe class
class Pipe:
    def __init__(self, x, y, height):
        self.image = pygame.Surface((50, height))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self, screen, scroll):
        screen.blit(self.image, (self.rect.x - scroll, self.rect.y))

# Flag class
class Flag:
    def __init__(self, x, y):
        self.image = pygame.Surface((10, 50))
        self.image.fill(WHITE)
        pygame.draw.rect(self.image, RED, (0, 0, 10, 30))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self, screen, scroll):
        screen.blit(self.image, (self.rect.x - scroll, self.rect.y))

# Create game objects
def create_level():
    platforms = []
    enemies = []
    coins = []
    pipes = []
    
    # Ground platform
    for i in range(30):
        platforms.append(Platform(i * TILE_SIZE, SCREEN_HEIGHT - 40, TILE_SIZE, TILE_SIZE))
    
    # Platforms in the air
    platforms.append(Platform(200, 300, 100, 20))
    platforms.append(Platform(400, 250, 100, 20))
    platforms.append(Platform(600, 200, 100, 20))
    platforms.append(Platform(800, 250, 100, 20))
    platforms.append(Platform(1000, 300, 100, 20))
    
    # Pipes
    pipes.append(Pipe(350, SCREEN_HEIGHT - 100, 60))
    pipes.append(Pipe(750, SCREEN_HEIGHT - 120, 80))
    
    # Enemies
    enemies.append(Enemy(300, SCREEN_HEIGHT - 70))
    enemies.append(Enemy(500, SCREEN_HEIGHT - 70))
    enemies.append(Enemy(700, SCREEN_HEIGHT - 70))
    enemies.append(Enemy(900, SCREEN_HEIGHT - 70))
    
    # Coins
    for i in range(10):
        coins.append(Coin(250 + i * 50, 250))
    
    # Flag (end of level)
    flag = Flag(1200, SCREEN_HEIGHT - 90)
    
    return platforms, enemies, coins, pipes, flag

# Draw text on screen
def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

# Main game loop
def main():
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)
    
    # Create player
    player = Player(100, 300)
    
    # Create level
    platforms, enemies, coins, pipes, flag = create_level()
    
    # Game variables
    scroll = 0
    game_state = "playing"
    level = 1
    max_levels = 32
    
    running = True
    while running:
        clock.tick(60)
        
        # Fill background
        screen.fill(SKY_BLUE)
        
        # Draw clouds in background
        for i in range(5):
            pygame.draw.ellipse(screen, WHITE, (i * 200 - scroll // 2, 50, 100, 50))
            pygame.draw.ellipse(screen, WHITE, (i * 200 + 50 - scroll // 2, 30, 80, 60))
        
        # Draw platforms
        for platform in platforms:
            platform.draw(screen, scroll)
        
        # Draw pipes
        for pipe in pipes:
            pipe.draw(screen, scroll)
        
        # Draw coins
        for coin in coins:
            coin.update()
            coin.draw(screen, scroll)
        
        # Draw enemies
        for enemy in enemies:
            enemy.update(scroll)
            enemy.draw(screen, scroll)
        
        # Draw flag
        flag.draw(screen, scroll)
        
        # Draw player
        player.draw(screen, scroll)
        
        # Draw UI
        draw_text(f"SCORE: {player.score}", font, WHITE, 10, 10)
        draw_text(f"LIVES: {player.lives}", font, WHITE, 10, 40)
        draw_text(f"LEVEL: {level}/{max_levels}", font, WHITE, 500, 10)
        
        # Handle game states
        if game_state == "playing":
            # Update player and get game state
            game_state = player.update(platforms, enemies, coins, pipes, flag)
            
            # Update scroll based on player position
            if (player.rect.right > SCREEN_WIDTH - SCROLL_THRESH and scroll < (len(platforms) * TILE_SIZE) - SCREEN_WIDTH) or \
               (player.rect.left < SCROLL_THRESH and scroll > 0):
                scroll += player.direction * player.speed
            
        elif game_state == "level_complete":
            draw_text("LEVEL COMPLETE!", font, WHITE, 200, 150)
            draw_text("Press SPACE to continue", font, WHITE, 180, 200)
            
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE]:
                level += 1
                if level > max_levels:
                    game_state = "game_complete"
                else:
                    # Reset level with increased difficulty
                    platforms, enemies, coins, pipes, flag = create_level()
                    player.rect.x = 100
                    player.rect.y = 300
                    scroll = 0
                    game_state = "playing"
                    
        elif game_state == "game_over":
            draw_text("GAME OVER", font, WHITE, 230, 150)
            draw_text("Press SPACE to restart", font, WHITE, 190, 200)
            
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE]:
                # Reset game
                player = Player(100, 300)
                platforms, enemies, coins, pipes, flag = create_level()
                scroll = 0
                game_state = "playing"
                
        elif game_state == "game_complete":
            draw_text("CONGRATULATIONS!", font, WHITE, 200, 150)
            draw_text("YOU BEAT ALL 32 LEVELS!", font, WHITE, 170, 200)
            draw_text("Press SPACE to play again", font, WHITE, 170, 250)
            
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE]:
                # Reset game
                player = Player(100, 300)
                platforms, enemies, coins, pipes, flag = create_level()
                scroll = 0
                level = 1
                game_state = "playing"
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
        
        pygame.display.update()

if __name__ == "__main__":
    main()

import pygame
import random
import sys

# ----------------------------
# Config
# ----------------------------
WIDTH = 500
HEIGHT = 700
FPS = 60
GRAVITY = 0.5
JUMP_STRENGTH = -9
PIPE_SPEED = 4
PIPE_WIDTH = 80
PIPE_GAP = 180
PIPE_FREQUENCY = 1500  # ms
GROUND_HEIGHT = 100

# Colors
SKY_BLUE = (135, 206, 235)
GREEN = (34, 177, 76)
DARK_GREEN = (0, 120, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird Clone")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 36)


class Bird:
    def __init__(self):
        self.x = 100
        self.y = HEIGHT // 2
        self.radius = 20
        self.velocity = 0

    def jump(self):
        self.velocity = JUMP_STRENGTH

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity

    def draw(self):
        pygame.draw.circle(screen, YELLOW, (self.x, int(self.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (self.x + 8, int(self.y) - 5), 3)

    def get_rect(self):
        return pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )


class Pipe:
    def __init__(self):
        self.x = WIDTH
        self.height = random.randint(150, HEIGHT - GROUND_HEIGHT - PIPE_GAP - 150)
        self.passed = False

    def update(self):
        self.x -= PIPE_SPEED

    def draw(self):
        # Top pipe
        pygame.draw.rect(screen, GREEN, (self.x, 0, PIPE_WIDTH, self.height))
        pygame.draw.rect(screen, DARK_GREEN, (self.x - 5, self.height - 20, PIPE_WIDTH + 10, 20))

        # Bottom pipe
        bottom_y = self.height + PIPE_GAP
        bottom_height = HEIGHT - GROUND_HEIGHT - bottom_y
        pygame.draw.rect(screen, GREEN, (self.x, bottom_y, PIPE_WIDTH, bottom_height))
        pygame.draw.rect(screen, DARK_GREEN, (self.x - 5, bottom_y, PIPE_WIDTH + 10, 20))

    def collide(self, bird):
        bird_rect = bird.get_rect()

        top_pipe = pygame.Rect(self.x, 0, PIPE_WIDTH, self.height)
        bottom_pipe = pygame.Rect(
            self.x,
            self.height + PIPE_GAP,
            PIPE_WIDTH,
            HEIGHT - GROUND_HEIGHT - (self.height + PIPE_GAP)
        )

        return bird_rect.colliderect(top_pipe) or bird_rect.colliderect(bottom_pipe)


def draw_ground():
    pygame.draw.rect(screen, GREEN, (0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT))


def draw_text(text, x, y):
    label = font.render(text, True, WHITE)
    screen.blit(label, (x, y))


def reset_game():
    return Bird(), [], 0, pygame.time.get_ticks()


def main():
    bird, pipes, score, last_pipe_time = reset_game()
    game_over = False

    running = True
    while running:
        clock.tick(FPS)
        screen.fill(SKY_BLUE)
   
    ## Action code to be altered
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_over:
                        bird, pipes, score, last_pipe_time = reset_game()
                        game_over = False
                    else:
                        bird.jump()

        if not game_over:
            # Spawn pipes
            current_time = pygame.time.get_ticks()
            if current_time - last_pipe_time > PIPE_FREQUENCY:
                pipes.append(Pipe())
                last_pipe_time = current_time

            bird.update()

            for pipe in pipes:
                pipe.update()

                if pipe.collide(bird):
                    game_over = True

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    score += 1

            pipes = [p for p in pipes if p.x + PIPE_WIDTH > 0]

            # Ground / ceiling collision
            if bird.y + bird.radius >= HEIGHT - GROUND_HEIGHT:
                game_over = True
            if bird.y - bird.radius <= 0:
                game_over = True

        # Draw everything
        bird.draw()

        for pipe in pipes:
            pipe.draw()
        
        
        

        draw_ground()
        draw_text(f"Score: {score}", 20, 20)

        if game_over:
            draw_text("GAME OVER", WIDTH//2 - 110, HEIGHT//2 - 40)
            draw_text("Press SPACE to restart", WIDTH//2 - 180, HEIGHT//2 + 10)

        pygame.display.update()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()



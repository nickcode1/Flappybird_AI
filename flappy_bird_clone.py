import pygame
import random
import sys
from itertools import product

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
PIPE_GAP = 150
PIPE_FREQUENCY = 1500  # ms
GROUND_HEIGHT = 100

# Colors
SKY_BLUE = (135, 206, 235)
GREEN = (34, 177, 76)
DARK_GREEN = (0, 120, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

#SIM Specs
N = 10 


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

def seq_eval(seq, current_y, current_v, pipeheight, pipex):
    y = current_y
    v = current_v
    px = pipex
    
    bird_x = 100
    radius = 25

    # 1. ADD THIS: A separate X coordinate strictly for drawing the red line
    draw_x = bird_x 
    
    # 2. Start the line EXACTLY at the bird's center
    coords = [(bird_x, current_y)] 

    total_cost = 0
    Qy = 100
    Qv = 10
    R  = 1000000

    for i in seq:
        px -= PIPE_SPEED        # The pipe moves LEFT (for collision math)
        draw_x += PIPE_SPEED    # The visual path moves RIGHT (for the red line)

        # update physics
        if i == 1:
            v = JUMP_STRENGTH + GRAVITY
        else:
            v += GRAVITY
        
        y += v
        
        # 3. Append the DRAWING coordinate, not the pipe coordinate
        coords.append((draw_x, y))

        # position error (distance from center of gap)
        error = y - (pipeheight + PIPE_GAP / 2)

        # stage cost
        total_cost += (Qy * error**2 + Qv * v**2 + R * i)

        # FIXED HITBOX COLLISION
        if px < (bird_x + radius) and (px + PIPE_WIDTH) > (bird_x - radius):
            if (y - radius) < pipeheight or (y + radius) > (pipeheight + PIPE_GAP):
                total_cost = float('inf') 

        # FIXED BOUNDARY COLLISION (Floor and Ceiling)
        if (y + radius) >= (HEIGHT - GROUND_HEIGHT) or (y - radius) <= 0:
            total_cost = float('inf')

    return total_cost, coords


def simulate(birdy,birdvelo,pipeheight,pipex):

  ypos = birdy
  velo = birdvelo
  seqs = list(product([0,1], repeat=N))
  optimalcost = float("inf")
  optimal_seq = []
  
  for seq in seqs:
    cost = seq_eval(seq,birdy,birdvelo,pipeheight,pipex)

        
    if cost[0] < optimalcost:
        optimalcost = cost[0]
        optimal_seq = seq
        optimal_coords = cost[1]
    # else:
    #     optimal_seq = [0]*N
    
  return optimal_seq[0],optimal_coords


    
def main():
    bird, pipes, score, last_pipe_time = reset_game()
    game_over = False
    coords = []
    running = True
    while running:
        clock.tick(FPS)
        screen.fill(SKY_BLUE)

      #  Find the nearest pipe ahead of the bird
        next_pipe = next((p for p in pipes if p.x + PIPE_WIDTH > bird.x - bird.radius), None)

        if next_pipe:
            move = simulate(bird.y, bird.velocity, next_pipe.height, next_pipe.x)
            coords = move[1]

            if move[0] == 1:

                bird.jump()
        
        elif bird.y > 300:
            
            bird.jump()
            
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            ## Action code to be altered
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
        
        draw_predicted_path(coords)
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


def draw_predicted_path(coords):
    if len(coords) < 2:
        return

    # Use a distinct color (e.g., Red) so it stands out
    LINE_COLOR = (255, 0, 0)
    
    # Draw dotted line (iterate by 2 to create gaps)
    for i in range(0, len(coords) - 1, 2):
        start_pos = (int(coords[i][0]), int(coords[i][1]))
        end_pos = (int(coords[i+1][0]), int(coords[i+1][1]))
        
        pygame.draw.line(screen, LINE_COLOR, start_pos, end_pos, 3)

if __name__ == "__main__":
    main()



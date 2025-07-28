import pygame
import random
import os

pygame.init()

WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird Mini")
clock = pygame.time.Clock()

ASSETS = "assets"
bg = pygame.image.load(os.path.join(ASSETS, "bg.png"))
bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))

bird = pygame.image.load(os.path.join(ASSETS, "bird.png"))
bird = pygame.transform.scale(bird, (40, 30))

pipe_img = pygame.image.load(os.path.join(ASSETS, "pipe.png"))
pipe_img = pygame.transform.scale(pipe_img, (70, 400))

flap_sound = pygame.mixer.Sound(os.path.join(ASSETS, "flap.wav"))
point_sound = pygame.mixer.Sound(os.path.join(ASSETS, "point.wav"))
hit_sound = pygame.mixer.Sound(os.path.join(ASSETS, "hit.wav"))

font = pygame.font.SysFont("Arial", 28)
big_font = pygame.font.SysFont("Arial", 40)

gravity = 0.4
bird_x = 100
bird_y = HEIGHT // 2
bird_velocity = 0
score = 0
game_over = False
pipes = []
jump_cooldown = 0
game_started = False

HIGH_SCORE_FILE = os.path.join(ASSETS, "highscore.txt")
if os.path.exists(HIGH_SCORE_FILE):
    with open(HIGH_SCORE_FILE, "r") as f:
        try:
            high_score = int(f.read())
        except:
            high_score = 0
else:
    high_score = 0


def save_high_score():
    with open(HIGH_SCORE_FILE, "w") as f:
        f.write(str(high_score))


def reset_game():
    global bird_y, bird_velocity, pipes, score, game_over, jump_cooldown
    bird_y = HEIGHT // 2
    bird_velocity = 0
    pipes.clear()
    score = 0
    game_over = False
    jump_cooldown = 0


def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    rect = img.get_rect(center=(x, y))
    screen.blit(img, rect)


def create_pipe():
    gap = 150
    pipe_height = random.randint(100, 400)
    top_rect = pipe_img.get_rect(midbottom=(WIDTH + 50, pipe_height - gap // 2))
    bottom_rect = pipe_img.get_rect(midtop=(WIDTH + 50, pipe_height + gap // 2))
    return {"top": top_rect, "bottom": bottom_rect, "passed": False}


def draw_pipes():
    for pipe in pipes:
        screen.blit(pygame.transform.flip(pipe_img, False, True), pipe["top"])
        screen.blit(pipe_img, pipe["bottom"])


def move_pipes():
    for pipe in pipes:
        pipe["top"].x -= 3
        pipe["bottom"].x -= 3


def check_collision():
    bird_rect = bird.get_rect(center=(bird_x, bird_y))
    for pipe in pipes:
        if bird_rect.colliderect(pipe["top"]) or bird_rect.colliderect(pipe["bottom"]):
            return True
    if bird_y <= 0 or bird_y >= HEIGHT:
        return True
    return False


running = True
while running:
    clock.tick(60)
    screen.blit(bg, (0, 0))
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_started:
        draw_text("Flappy Bird Mini", big_font, (255, 255, 255), WIDTH // 2, HEIGHT // 2 - 60)
        draw_text("Click SPACE Start Game", font, (255, 255, 0), WIDTH // 2, HEIGHT // 2)
        pygame.display.update()
        if keys[pygame.K_SPACE]:
            game_started = True
            reset_game()
        continue

    if not game_over:
        if keys[pygame.K_SPACE] and jump_cooldown == 0:
            bird_velocity = -5.5  # Giảm lực bay lên
            flap_sound.play()
            jump_cooldown = 10

        if jump_cooldown > 0:
            jump_cooldown -= 1

        bird_velocity += gravity
        bird_y += bird_velocity
        screen.blit(bird, (bird_x, bird_y))

        if len(pipes) == 0 or pipes[-1]["top"].x < WIDTH - 200:
            pipes.append(create_pipe())

        move_pipes()
        draw_pipes()

        if check_collision():
            game_over = True
            hit_sound.play()

        for pipe in pipes:
            if pipe["top"].right < bird_x and not pipe["passed"]:
                score += 1
                pipe["passed"] = True
                point_sound.play()

        pipes = [p for p in pipes if p["top"].x > -70]
        draw_text(f"Score: {score}", font, (255, 255, 255), WIDTH // 2, 30)

    else:
        if score > high_score:
            high_score = score
            save_high_score()

        draw_text("Game Over!", big_font, (255, 0, 0), WIDTH // 2, HEIGHT // 2 - 80)
        draw_text(f"Score: {score}", font, (255, 255, 255), WIDTH // 2, HEIGHT // 2 - 30)
        draw_text(f"High Score: {high_score}", font, (255, 255, 0), WIDTH // 2, HEIGHT // 2 + 10)
        draw_text("Click SPACE play the game again", font, (255, 255, 255), WIDTH // 2, HEIGHT // 2 + 50)

        if keys[pygame.K_SPACE]:
            reset_game()

    pygame.display.update()

pygame.quit()

import pygame
import random
import os

pygame.init()

WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

ASSETS = "assets"
FONT_PATH = os.path.join(ASSETS, "Roboto-Regular.ttf")

if not os.path.exists(FONT_PATH):
    print(" Font 'Roboto-Regular.ttf' chưa tồn tại trong thư mục assets!")
    pygame.quit()
    exit()

bg = pygame.image.load(os.path.join(ASSETS, "bg.png"))
bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))

bird = pygame.image.load(os.path.join(ASSETS, "bird.png"))
bird = pygame.transform.scale(bird, (40, 30))

pipe_img = pygame.image.load(os.path.join(ASSETS, "pipe.png"))
pipe_img = pygame.transform.scale(pipe_img, (70, 400))

flap_sound = pygame.mixer.Sound(os.path.join(ASSETS, "flap.wav"))
point_sound = pygame.mixer.Sound(os.path.join(ASSETS, "point.wav"))
hit_sound = pygame.mixer.Sound(os.path.join(ASSETS, "hit.wav"))

font = pygame.font.Font(FONT_PATH, 28)
big_font = pygame.font.Font(FONT_PATH, 40)
title_font = pygame.font.Font(FONT_PATH, 48)
option_font = pygame.font.Font(FONT_PATH, 28)

gravity = 0.4
bird_x = 100
bird_y = HEIGHT // 2
bird_velocity = 0
score = 0
game_over = False
pipes = []
jump_cooldown = 0
game_started = False
show_menu = True

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

def draw_main_menu():
    screen.blit(bg, (0, 0))
    panel_surface = pygame.Surface((320, 280), pygame.SRCALPHA)
    panel_surface.fill((0, 0, 0, 160))
    screen.blit(panel_surface, (WIDTH // 2 - 160, HEIGHT // 2 - 140))

    draw_text("Flappy Bird", title_font, (255, 255, 0), WIDTH // 2, HEIGHT // 2 - 90)
    draw_text("[SPACE] Bắt đầu chơi", option_font, (255, 255, 255), WIDTH // 2, HEIGHT // 2 - 30)
    draw_text("[H] Hướng dẫn", option_font, (200, 200, 255), WIDTH // 2, HEIGHT // 2 + 10)
    draw_text("[L] Bảng xếp hạng", option_font, (200, 255, 200), WIDTH // 2, HEIGHT // 2 + 50)
    draw_text("[ESC] Thoát", option_font, (255, 100, 100), WIDTH // 2, HEIGHT // 2 + 90)

def show_instruction():
    while True:
        screen.fill((200, 255, 255))
        instructs = [
            "Cách chơi:",
            "- Nhấn SPACE để chim bay lên",
            "- Tránh va vào ống hoặc bị rơi ",
            "- Ghi điểm càng cao càng tốt!",
            "",
            "Nhấn M để quay lại menu chính"
        ]
        for i, line in enumerate(instructs):
            text = font.render(line, True, (0, 0, 0))
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 100 + i * 40))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                return
        pygame.display.update()

def show_leaderboard():
    screen.fill((255, 255, 200))
    draw_text("Bảng xếp hạng", title_font, (0, 0, 0), WIDTH // 2, 100)
    draw_text(f"Điểm cao nhất: {high_score}", font, (0, 0, 255), WIDTH // 2, 180)
    draw_text("Nhấn M để quay lại", font, (0, 0, 0), WIDTH // 2, 240)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                return
        pygame.display.update()

running = True
while running:
    clock.tick(60)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if show_menu:
        draw_main_menu()
        if keys[pygame.K_SPACE]:
            show_menu = False
            game_started = True
            reset_game()
        elif keys[pygame.K_h]:
            show_instruction()
        elif keys[pygame.K_l]:
            show_leaderboard()
        elif keys[pygame.K_ESCAPE]:
            running = False
        pygame.display.update()
        continue

    if not game_over:
        screen.blit(bg, (0, 0))

        if keys[pygame.K_SPACE] and jump_cooldown == 0:
            bird_velocity = -5.5
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

                if score > high_score:
                    high_score = score
                    save_high_score()

        pipes = [p for p in pipes if p["top"].x > -70]

        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        high_score_text = font.render(f"High Score: {high_score}", True, (255, 215, 0))
        screen.blit(high_score_text, (WIDTH - high_score_text.get_width() - 10, 10))

    else:
        screen.blit(bg, (0, 0))
        draw_pipes()
        screen.blit(bird, (bird_x, bird_y))

        panel_surface = pygame.Surface((320, 260), pygame.SRCALPHA)
        panel_surface.fill((0, 0, 0, 150))
        screen.blit(panel_surface, (WIDTH // 2 - 160, HEIGHT // 2 - 130))

        draw_text("Game Over!", big_font, (255, 0, 0), WIDTH // 2, HEIGHT // 2 - 90)
        draw_text(f"Score: {score}", font, (255, 255, 255), WIDTH // 2, HEIGHT // 2 - 40)
        draw_text(f"High Score: {high_score}", font, (255, 215, 0), WIDTH // 2, HEIGHT // 2)
        draw_text("SPACE: Chơi lại", font, (255, 255, 255), WIDTH // 2, HEIGHT // 2 + 50)
        draw_text("M: Menu chính", font, (200, 200, 200), WIDTH // 2, HEIGHT // 2 + 90)

        if keys[pygame.K_SPACE]:
            reset_game()
            game_over = False
            game_started = True
        elif keys[pygame.K_m]:
            show_menu = True
            game_over = False

    pygame.display.update()

pygame.quit()

import pygame
import sys
import random

# scales the window to account for smaller (laptop) screens
if sys.platform == 'win32':
    import ctypes
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except AttributeError:
        pass


def draw_floor():
    screen.blit(floor_surface, (floor_x_pos, 836))
    screen.blit(floor_surface, (floor_x_pos + 540, 836))


def create_pipe():
    random_pipe_position = random.randrange(380, 640, 20)
    bottom_pipe = pipe_surface.get_rect(midtop=(640, random_pipe_position))
    top_pipe = pipe_surface.get_rect(midbottom=(640, random_pipe_position-240))
    return bottom_pipe, top_pipe


def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= 4
    return pipes


def draw_pipes(pipes):
    for pipe in pipes:
        if pipe.bottom >= 880:
            screen.blit(pipe_surface, pipe)
        else:
            flipped_pipe = pygame.transform.flip(pipe_surface, False, True)
            screen.blit(flipped_pipe, pipe)


def delete_obsolete_pipes(pipes, pipe_scores):
    to_remove = 0
    i = 0
    for pipe in pipes:
        if pipe.centerx < -10:
            if pipe.bottom >= 880:
                pipe_scores.pop(0)
            to_remove += 1
        i += 1
    for i in range(to_remove):
        pipes.pop(0)


def check_collision(pipes):
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            return False
    if bird_rect.top <= -30 or bird_rect.bottom >= 836:
        return False
    return True


def rotate_bird(bird):
    new_bird = pygame.transform.rotozoom(bird, -bird_movement * 3, 1)
    return new_bird


def bird_animation():
    new_bird = bird_frames[bird_index]
    new_bird_rect = new_bird.get_rect(center=(100, bird_rect.centery))
    return new_bird, new_bird_rect


def score_display(game_state):
    if game_state == "main_game":
        score_surface = game_font.render(str(score), True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(270, 65))
        screen.blit(score_surface, score_rect)
    if game_state == "game_over":
        score_surface = game_font.render("Score: " + str(score), True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(270, 65))
        screen.blit(score_surface, score_rect)
        high_score_surface = game_font.render("High score: " + str(high_score), True, (255, 255, 255))
        high_score_rect = high_score_surface.get_rect(center=(270, 800))
        screen.blit(high_score_surface, high_score_rect)


def update_score(scr, pipes, pipe_scores):
    for i in range(0, len(pipe_scores)):
        if pipes[i*2].bottom >= 880 and pipes[i*2].centerx < 100 and pipe_scores[i] == 0:
            scr += 1
            pipe_scores[i] = 1
    return scr


# GAME VARIABLES
gravity = 0.25
bird_movement = 0
game_active = True
score = 0
high_score = 0

pygame.init()
pygame.display.set_caption("Flappy Bird")
pygame.display.set_icon(pygame.image.load("assets/redbird-midflap.png"))
screen = pygame.display.set_mode((540, 960))
clock = pygame.time.Clock()
game_font = pygame.font.Font("04B_19.ttf", 50)


bg_surface = pygame.image.load("assets/background-day-ns.png").convert()
bg_surface = pygame.transform.scale(bg_surface, (540, 960))

floor_surface = pygame.image.load("assets/base.png").convert()
floor_surface = pygame.transform.scale(floor_surface, (540, 180))

floor_x_pos = 0

bird_downflap = pygame.transform.scale(pygame.image.load('assets/bluebird-downflap.png').convert_alpha(), (58, 39))
bird_midflap = pygame.transform.scale(pygame.image.load('assets/bluebird-midflap.png').convert_alpha(), (58, 39))
bird_upflap = pygame.transform.scale(pygame.image.load('assets/bluebird-upflap.png').convert_alpha(), (58, 39))
bird_frames = [bird_downflap, bird_midflap, bird_upflap]
bird_index = 1
bird_surface = bird_frames[bird_index]
bird_rect = bird_surface.get_rect(center=(100, 480))

BIRDFLAP = pygame.USEREVENT + 1
pygame.time.set_timer(BIRDFLAP, 200)

pipe_surface = pygame.image.load("assets/pipe-green.png").convert()
pipe_surface = pygame.transform.scale(pipe_surface, (84, 514))

pipe_list = []
pipe_scores_list = []
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 1000)

game_over_surface = pygame.transform.scale(pygame.image.load("assets/gameover.png").convert_alpha(), (309, 68))
game_over_rect = game_over_surface.get_rect(center=(270, 480))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bird_movement = 0
                bird_movement -= 9
            if event.key == pygame.K_SPACE and not game_active:
                game_active = True
                pipe_list.clear()
                pipe_scores_list.clear()
                score = 0
                bird_rect.center = (100, 480)
                bird_movement = -8
        if event.type == SPAWNPIPE:
            delete_obsolete_pipes(pipe_list, pipe_scores_list)
            pipe_list.extend(create_pipe())
            pipe_scores_list.append(0)
        if event.type == BIRDFLAP:
            bird_index = (bird_index + 1) % 3
            bird_surface, bird_rect = bird_animation()

    screen.blit(bg_surface, (0, 0))

    if game_active:
        # Bird
        bird_movement += gravity
        rotated_bird = rotate_bird(bird_surface)
        bird_rect.centery += int(bird_movement)
        screen.blit(rotated_bird, bird_rect)
        game_active = check_collision(pipe_list)

        # Pipes
        pipe_list = move_pipes(pipe_list)
        draw_pipes(pipe_list)

        # Score update
        score = update_score(score, pipe_list, pipe_scores_list)
        score_display("main_game")
    else:
        if high_score < score:
            high_score = score
        score_display("game_over")
        screen.blit(game_over_surface, game_over_rect)

    # Floor
    floor_x_pos -= 1
    draw_floor()
    if floor_x_pos <= -540:
        floor_x_pos = 0

    pygame.display.update()
    clock.tick(120)

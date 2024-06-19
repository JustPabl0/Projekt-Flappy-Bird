import pygame
import shelve
from pygame.locals import *
from random import randint

highscore_save = shelve.open("highscore")

# inicjacja pygame
pygame.init()
clock = pygame.time.Clock()
fps = 75

# wielkości okna
screen_width = 500
screen_height = 700

# okno i tytuł okna
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')

# tekstowe sprawy (czcionka, kolor)
font = pygame.font.SysFont('smallee', 60)
font_smaller = pygame.font.SysFont('smallee', 20)

color = (0, 0, 0)

# definiowanie zmiennych gry
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 150
pipe_frequency = 1500  # milisekundy
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
highscore = highscore_save["highscore"]
playsound = True
pass_pipe = False

# wczytywanie obrazów
bg = pygame.image.load('sprites/bg.png')
ground_img = pygame.image.load('sprites/ground.png')
restart_img = pygame.image.load('sprites/restart.png')
play_img = pygame.image.load('sprites/play.png')
main_menu_img = pygame.image.load('sprites/main_menu_background.png')

# wczytywanie dźwięków
jump_sound = pygame.mixer.Sound('sounds/jump.wav')
death_sound = pygame.mixer.Sound('sounds/explosion.wav')
click_sound = pygame.mixer.Sound('sounds/pickupCoin.wav')

# resetowanie gry
def reset_game():
    global game_over
    global score
    global flying
    global playsound
    game_over = False
    flying = False
    playsound = True
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    score = 0

# rysowanie tekstu
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# klasa Ptaka (gracz)
class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f'sprites/bird{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def update(self):
        # grawitacja
        if flying == True:
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 555:
                self.rect.y += int(self.vel)

        # podskok
        if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False and game_over == False:
            self.clicked = True
            self.vel = -9.9
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # handle the animation
        if game_over == False:
            self.counter += 1
            flap_cooldown = 5

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            # obracanie
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)

# klasa rury
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('sprites/pipe.png')
        self.rect = self.image.get_rect()
        # pozycja 1 jest od góry, a -1 od dołu
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - pipe_gap // 2]
        if position == -1:
            self.rect.topleft = [x, y + pipe_gap // 2]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        action = False
        # rejestrowanie gdzie jest myszka
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                jump_sound.play()
                action = True

        # rysowanie przycisku
        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action

# grupa na wszystkie ptaki
bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()
flappy = Bird(100, int(screen_height / 2))
bird_group.add(flappy)

# dodanie przycików
restart_button = Button(250-60, 300-21, restart_img)
play_button = Button(int(screen_width / 2) - 60, int(screen_height / 2) - 21, play_img)

# główna pętla gry
run = True
while run:
    # ograniczenie klate na sekunde
    clock.tick(fps)

    # rysowanie tła
    screen.blit(bg, (0, 0))

    # rysowanie ptaka
    bird_group.draw(screen)
    bird_group.update()

    # rysowanie rury
    pipe_group.draw(screen)

    # rysowanie podłogi
    screen.blit(ground_img, (ground_scroll, 555))

    # sprawdzanie punktów
    if game_over == False and flying == True:
        if len(pipe_group) > 0:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right and pass_pipe == False:
                pass_pipe = True
            if pass_pipe == True and bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                click_sound.play()
                if score > highscore:
                    highscore_save["highscore"] = score
                    highscore = highscore_save["highscore"]
                pass_pipe = 0

    # rysowanie punktów
    draw_text(str(score), font, (0, 0, 0), screen_width // 2, 50)

    # sprawdzanie kolizji
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True
        if playsound:
            death_sound.play()
            playsound = False

    # sprawdzanie czy ptak uderzył ziemie
    if flappy.rect.bottom > 555:
        game_over = True
        flying = False
        if playsound:
            death_sound.play()
            playsound = False

    # rysowanie main menu
    if game_over == False and flying == False:
        screen.blit(main_menu_img, (0, 0))
        draw_text("Lewy przycisk myszy odpowiada za skok i interakcje z przyciskami", font_smaller, (0, 0, 0), 35, 450)
        draw_text(f"HIGHSCORE:{str(highscore)}", font, (0, 0, 0), (screen_width // 2) - 155, 550)
        if play_button.draw():
            flying = True

    if game_over == False and flying == True:
        # generowanie nowych rur
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_height = randint(-30, 200)
            btm_pipe = Pipe(screen_width, int(pipe_gap) + pipe_height, -1)
            top_pipe = Pipe(screen_width, int(pipe_gap) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now
        pipe_group.update()

        # przesuwanie podłogi
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 110:
            ground_scroll = 0

    # sprawdzanie czy trzeba zresetować gre
    if game_over == True:
        if restart_button.draw():
            reset_game()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()

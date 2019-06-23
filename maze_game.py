import pygame
from pygame.locals import *
import sys
import time
from random import randrange
import random

SCREEN_SIZE = (1280, 720) 
global HORIZ_MOV_INCR
HORIZ_MOV_INCR = 5 
global FPS
global clock
global time_spent

WHITE = ((255,255,255))
BLACK = ((0,0,0))
BLUE = pygame.Color('dodgerblue4')

global difficulty
m_width = 16
m_height = 8

def text_objects(text, font):
    textSurface = font.render(text, True, BLACK)
    return textSurface, textSurface.get_rect()

def game_intro():
    intro = True
    while intro:
        for event in pygame.event.get():
            if event.type == KEYDOWN and event.key == K_1:
                intro = False
                return 1
            if event.type == KEYDOWN and event.key == K_2:
                intro = False
                return 2
            if event.type == KEYDOWN and event.key == K_3:
                intro = False
                return 3
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                
        screen.fill(WHITE)
        largeText = pygame.font.Font('freesansbold.ttf',115)
        TextSurf, TextRect = text_objects("The Maze Game", largeText)
        TextRect.center = (640,360)
        screen.blit(TextSurf, TextRect)
        smallText = pygame.font.Font('freesansbold.ttf',75)
        TextSurf, TextRect = text_objects("Press [1,2,3] for difficulty.", smallText)
        TextRect.center = (640,460)
        screen.blit(TextSurf, TextRect)
        pygame.display.update()

def game_win():
    win = True
    while win:
        for event in pygame.event.get():
            if event.type == KEYDOWN and event.key == K_SPACE:
                win = False
                pygame.quit()
                quit()
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                
        screen.fill(WHITE)
        largeText = pygame.font.Font('freesansbold.ttf',115)
        TextSurf, TextRect = text_objects("You Won!", largeText)
        TextRect.center = (640,360)
        screen.blit(TextSurf, TextRect)
        smallText = pygame.font.Font('freesansbold.ttf',75)
        TextSurf, TextRect = text_objects("Press space to exit.", smallText)
        TextRect.center = (640,460)
        screen.blit(TextSurf, TextRect)
        pygame.display.update()
        

def RelRect(actor, camera):
    return pygame.Rect(actor.rect.x-camera.rect.x, actor.rect.y-camera.rect.y, actor.rect.w, actor.rect.h)

def flip_image(image):
    return pygame.transform.flip(image, True, False)

class Camera(object):
    def __init__(self, screen, player, level_width, level_height):
        self.player = player
        self.rect = screen.get_rect()
        self.rect.center = self.player.center
        self.world_rect = Rect(0, 0, level_width, level_height)

    def update(self):
      if self.player.centerx > self.rect.centerx + 25:
          self.rect.centerx = self.player.centerx - 25
      if self.player.centerx < self.rect.centerx - 25:
          self.rect.centerx = self.player.centerx + 25
      if self.player.centery > self.rect.centery + 25:
          self.rect.centery = self.player.centery - 25
      if self.player.centery < self.rect.centery - 25:
          self.rect.centery = self.player.centery + 25
      self.rect.clamp_ip(self.world_rect)

    def draw_sprites(self, surf, sprites):
        for s in sprites:
            if s.rect.colliderect(self.rect):
                surf.blit(s.image, RelRect(s, self))

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("world/obstacle.png").convert()
        self.rect = self.image.get_rect()
        self.rect.topleft = [self.x, self.y]

class Door(pygame.sprite.Sprite):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("world/door.png").convert()
        self.rect = self.image.get_rect()
        self.rect.topleft = [self.x, self.y]


class Teleport(pygame.sprite.Sprite):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("world/teleport.png").convert()
        self.rect = self.image.get_rect()
        self.rect.topleft = [self.x, self.y]
        
class Shroom(pygame.sprite.Sprite):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("world/shroom.png").convert()
        self.rect = self.image.get_rect()
        self.rect.topleft = [self.x, self.y]

class Hero(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.health = 5

        self.movy = 0
        self.movx = 0
        self.x = x
        self.y = y

        self.contact = False
        self.jump = False
        self.attacking = False

        self.image = flip_image(pygame.image.load('actions/Player_Idle_Special_0.png').convert())

        self.rect = self.image.get_rect()
        self.run_action = ["actions/Player_Walk_Special_0.png","actions/Player_Walk_Special_1.png",
                         "actions/Player_Walk_Special_2.png", "actions/Player_Walk_Special_3.png"]
        self.attack_action = ["actions/Player_Attack_Special_0.png","actions/Player_Attack_Special_1.png",
                         "actions/Player_Attack_Special_2.png", "actions/Player_Attack_Special_3.png"]
        self.idle_action = ["actions/Player_Idle_Special_0.png","actions/Player_Idle_Special_1.png",
                         "actions/Player_Idle_Special_2.png", "actions/Player_Idle_Special_3.png"]
        self.death_action = ["actions/Player_Death_Special_0.png","actions/Player_Death_Special_1.png",
                         "actions/Player_Death_Special_2.png", "actions/Player_Death_Special_3.png"]
        self.direction = "right"
        self.rect.topleft = [x, y]
        self.frame = 0

        self.tunnel = False
        self.hint = False
        self.time_counter = 0
        self.start_time = 0

    def update(self, up, down, left, right, space, jetpack):        
        

        if jetpack:
                up = False
                self.contact = True
                self.jump = False
                self.movy -= 2
        	
        if up:
            if self.contact:
                if self.direction == "right" and not jetpack:
                    self.image = pygame.image.load("actions/Player_Walk_Special_0.png")
                elif self.direction == "left" and not jetpack:
                    self.image = flip_image(pygame.image.load("actions/Player_Walk_Special_0.png"))
                    
                self.jump = True
                self.movy -= 10

        if not down and self.direction == "right":
            if self.contact:
                self.frame += 1
                self.image = pygame.image.load(self.idle_action[self.frame]).convert_alpha()
                if self.frame == 3: self.frame = 0
            else:
                self.image = pygame.image.load("actions/Player_Idle_Special_0.png").convert_alpha()

        if not down and self.direction == "left":
            if self.contact:
                self.frame += 1
                self.image = flip_image(pygame.image.load(self.idle_action[self.frame]).convert_alpha())
                if self.frame == 3: self.frame = 0
            else:
                self.image = flip_image(pygame.image.load("actions/Player_Idle_Special_0.png").convert_alpha())

        if left:
            self.direction = "left"
            self.movx = -HORIZ_MOV_INCR
            if self.contact:
                self.frame += 1
                self.image = flip_image(pygame.image.load(self.run_action[self.frame]).convert_alpha())
                if self.frame == 3: self.frame = 0
            else:
                self.image = flip_image(pygame.image.load("actions/Player_Walk_Special_0.png").convert_alpha())

        if right:
            self.direction = "right"
            self.movx = +HORIZ_MOV_INCR
            if self.contact:
                self.frame += 1
                self.image = pygame.image.load(self.run_action[self.frame]).convert_alpha()
                if self.frame == 3: self.frame = 0
            else:
                self.image = pygame.image.load("actions/Player_Walk_Special_0.png").convert_alpha()

        if space:
            space = False
            self.attacking = True

        if not (left or right):
            self.movx = 0
        self.rect.right += self.movx

        self.collide(self.movx, 0, world)

        if self.attacking:
            if self.direction == "right":
                self.frame += 1
                print(self.frame)
                self.image = pygame.image.load(self.attack_action[self.frame]).convert_alpha()
                if self.frame == 3: 
                    self.frame = 0
                    self.attacking = False
            if self.direction == "left":
                self.frame += 1
                self.image = flip_image(pygame.image.load(self.attack_action[self.frame]).convert_alpha())
                if self.frame == 3: 
                    self.frame = 0
                    self.attacking = False

        if not self.contact:
            
            self.movy += 0.3
            if self.movy > 10:
                self.movy = 10
            self.rect.top += self.movy

        if self.jump:
            self.movy += 2
            self.rect.top += self.movy
            if self.contact == True:
                self.jump = False

        if self.tunnel:
            s = pygame.surface.Surface(screen.get_size())
            s.fill(pygame.color.Color('Grey'))
            if(difficulty == 1):
                pygame.draw.circle(s, (0,0,0,0), self.rect.topleft, 90)
            if(difficulty == 2):
                pygame.draw.circle(s, (0,0,0,0), pygame.mouse.get_pos(), 90)
            screen.blit(s, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
            pygame.display.flip()

            if (self.time_counter == self.start_time + 150):
                self.tunnel = False

        self.contact = False
        self.collide(0, self.movy, world)
        self.time_counter += 1

    def collide(self, movx, movy, world):
        self.contact = False
        time_counter = 0
        for o in world:
            if self.rect.colliderect(o):
                if isinstance(o, Door):
                    game_win()
                if isinstance(o, Teleport):
                    found = True
                    while found:
                        x_c = randrange(0,75*m_width-10)
                        y_c = randrange(0,75*m_height-10)
                        for obj in world:
                            if (not((x_c > obj.rect.left and x_c < obj.rect.right) and (y_c < obj.rect.bottom and y_c > obj.rect.top))):
                                self.rect.topleft = [x_c,y_c]
                                self.movx = 0
                                self.movy = 0
                                found = False
                                break
                if isinstance(o, Shroom):
                    self.tunnel = True
                    o.rect.topleft = (999999,999999)
                    o.kill()
                    self.start_time = self.time_counter
                    
                if movx > 0 and not isinstance(o, Shroom):
                    self.rect.right = o.rect.left
                if movx < 0 and not isinstance(o, Shroom):
                    self.rect.left = o.rect.right
                if movy > 0 and not isinstance(o, Shroom):
                    self.rect.bottom = o.rect.top
                    self.movy = 0
                    self.contact = True
                if movy < 0 and not isinstance(o, Shroom):
                    self.rect.top = o.rect.bottom
                    self.movy = 0
        time_counter += 1
        
class Level(object):
    def __init__(self, open_level):
        self.level1 = []
        self.world = []
        self.enemies = []
        self.all_sprite = pygame.sprite.Group()
        self.level = open(open_level, "r")

    def create_level(self, x, y):
        for l in self.level:
            self.level1.append(l)

        for row in self.level1:
            for col in row:
                if col == "#":
                    wall = Wall(x, y)
                    self.world.append(wall)
                    self.all_sprite.add(self.world)
                if col == "T":
                    teleport = Teleport(x, y)
                    self.world.append(teleport)
                    self.all_sprite.add(self.world)
                if col == "D":
                    door = Door(x, y)
                    self.world.append(door)
                    self.all_sprite.add(self.world)
                if col == "P":
                    self.hero = Hero(x,y)
                    self.all_sprite.add(self.hero)
                if col == "S":
                    self.shroom = Shroom(x,y)
                    self.world.append(self.shroom)
                    self.all_sprite.add(self.world)
                x += 25
            y += 25
            x = 0

    def get_size(self):
        lines = self.level1
        #line = lines[0]
        line = max(lines, key=len)
        self.width = (len(line))*25
        self.height = (len(lines))*25
        return (self.width, self.height)



def tps(orologio,fps):
    temp = orologio.tick(fps)
    tps = temp / 1000.
    return tps

import maze_gen
pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE, FULLSCREEN, 32)
screen_rect = screen.get_rect()
difficulty = game_intro()
background = pygame.image.load("world/background.png").convert_alpha()
background_rect = background.get_rect()
maze_gen.make_maze(m_width * difficulty,m_height * difficulty)

level = Level('level/maze_lvl')
level.create_level(0,0)
world = level.world
hero = level.hero
pygame.mouse.set_visible(0)


camera = Camera(screen, hero.rect, level.get_size()[0], level.get_size()[1])
all_sprite = level.all_sprite

FPS = 30
clock = pygame.time.Clock()

up = down = left = right = space = jetpack = False
x, y = 0, 0
while True:

    for event in pygame.event.get():
        if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
            pygame.quit()
            sys.exit()

        if event.type == KEYDOWN and (event.key == K_UP or event.key == K_w):
            up = True
        if event.type == KEYDOWN and (event.key == K_DOWN or event.key == K_s):
            down = True
        if event.type == KEYDOWN and (event.key == K_LEFT or event.key == K_a):
            left = True
        if event.type == KEYDOWN and (event.key == K_RIGHT or event.key == K_d):
            right = True
        if event.type == KEYDOWN and (event.key == K_o or event.key == K_LSHIFT):
            jetpack = True
        if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_p):
            space = True

        if event.type == KEYUP and (event.key == K_UP or event.key == K_w):
            up = False
        if event.type == KEYUP and (event.key == K_DOWN or event.key == K_s):
            down = False
        if event.type == KEYUP and (event.key == K_LEFT or event.key == K_a):
            left = False
        if event.type == KEYUP and (event.key == K_RIGHT or event.key == K_d):
            right = False
        if event.type == KEYUP and (event.key == K_o or event.key == K_LSHIFT):
            jetpack = False

    asize = ((screen_rect.w // background_rect.w + 1) * background_rect.w, (screen_rect.h // background_rect.h + 1) * background_rect.h)
    bg = pygame.Surface(asize)

    for x in range(0, asize[0], background_rect.w):
        for y in range(0, asize[1], background_rect.h):
            screen.blit(background, (x, y))

    time_spent = tps(clock, FPS)
    camera.draw_sprites(screen, all_sprite)

    hero.update(up, down, left, right, space, jetpack)
    for enemy in level.enemies:
    	enemy.update()


    space = False
    camera.update()
    pygame.display.flip()

#!/usr/bin/env python3
# draw a world
# add a player and player control
# add player movement
# add enemy and basic collision
# add platform
# add gravity
# add jumping
# add scrolling
# add loot
# add score

# GNU All-Permissive License
# Copying and distribution of this file, with or without modification,
# are permitted in any medium without royalty provided the copyright
# notice and this notice are preserved.  This file is offered as-is,
# without any warranty.

import pygame
import sys
import os
import pygame.freetype
from pygame.locals import *


'''
Objects
'''
       
class Platform(pygame.sprite.Sprite):
    # x location, y location, img width, img height, img file    
    def __init__(self,xloc,yloc,imgw,imgh,img):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join('images',img)).convert()
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.y = yloc
        self.rect.x = xloc

class Player(pygame.sprite.Sprite):
    '''
    Spawn a player
    '''
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.movex = 0
        self.movey = 0
        self.frame = 0
        self.health = 10
        self.damage = 0
        self.collide_delta = 0
        self.jump_delta = 6
        self.score = 1
        self.images = []
        for i in range(1,9):
            img = pygame.image.load(os.path.join('images','child' + str(i) + '.png')).convert()
            img.convert_alpha()
            img.set_colorkey(ALPHA)
            self.images.append(img)
            self.image = self.images[0]
            self.rect  = self.image.get_rect()

    def jump(self,platform_list):
        self.jump_delta = 0
  
    def gravity(self):
        self.movey += 3.2 # how fast player falls
       
        if self.rect.y > worldy and self.movey >= 0:
            self.movey = 0
            self.rect.y = worldy-ty-ty
   
    def control(self,x,y):
        '''
        control player movement
        '''
        self.movex += x
        self.movey += y
       
    def update(self):
        '''
        Update sprite position
        '''
       
        self.rect.x = self.rect.x + self.movex
        self.rect.y = self.rect.y + self.movey

        # moving left
        if self.movex < 0:
            self.frame += 1
            if self.frame > ani*3:
                self.frame = 0
            self.image = self.images[self.frame//ani]

        # moving right
        if self.movex > 0:
            self.frame += 1
            if self.frame > ani*3:
                self.frame = 0
            self.image = self.images[(self.frame//ani)+4]
        # moving up
        if self.movey < 0:
            self.frame += 1
            if self.frame > ani*3:
                self.frame = 0
            self.image = self.images[self.frame//ani]

        # collisions
        enemy_hit_list = pygame.sprite.spritecollide(self, enemy_list, False)
        if self.damage == 0:
            for enemy in enemy_hit_list:
                if not self.rect.contains(enemy):
                    self.damage = self.rect.colliderect(enemy)

        if self.damage == 1:
            idx = self.rect.collidelist(enemy_hit_list)
            if idx == -1:
                self.damage = 0   # set damage back to 0
                self.health -= 1  # subtract 1 hp

        loot_hit_list = pygame.sprite.spritecollide(self, loot_list, False)
        for loot in loot_hit_list:
            loot_list.remove(loot)
            self.score += 1
            print(self.score)
       
        plat_hit_list = pygame.sprite.spritecollide(self, plat_list, False)
        for p in plat_hit_list:
            self.collide_delta = 0 # stop jumping
            self.movey = 0
            if self.rect.y > p.rect.y:
                self.rect.y = p.rect.y+ty
            else:
                self.rect.y = p.rect.y-ty
           
        ground_hit_list = pygame.sprite.spritecollide(self, ground_list, False)
        for g in ground_hit_list:
            self.movey = 0
            self.rect.y = worldy-ty-ty
            self.collide_delta = 0 # stop jumping
            if self.rect.y > g.rect.y:
                self.health -=1
                print(self.health)
               
        if self.collide_delta < 0 and self.jump_delta < 0:
            self.jump_delta = 6*2
            self.movey -= 50  # how high to jump
            self.collide_delta += 6
            self.jump_delta    += 6

                  
class Enemy(pygame.sprite.Sprite):
    '''
    Spawn an enemy
    '''
    def __init__(self,x,y,img):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join('images',img))
        self.movey = 0
        self.image.convert_alpha()
        self.image.set_colorkey(ALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.counter = 0

               
    def move(self):
        '''
        enemy movement
        '''
        distance = 40
        speed = 4

        self.movey += 1.2
       
        if self.counter >= 0 and self.counter <= distance:
            self.rect.x += speed
        elif self.counter >= distance and self.counter <= distance*2:
            self.rect.x -= speed
        else:
            self.counter = 0
       
        self.counter += 1

        if not self.rect.y >= worldy-ty-ty:
            self.rect.y += self.movey

        plat_hit_list = pygame.sprite.spritecollide(self, plat_list, False)
        for p in plat_hit_list:
            self.movey = 0
            if self.rect.y > p.rect.y:
                self.rect.y = p.rect.y+ty
            else:
                self.rect.y = p.rect.y-ty

        ground_hit_list = pygame.sprite.spritecollide(self, ground_list, False)
        for g in ground_hit_list:
            self.rect.y = worldy-ty

       
class Level():
    def bad(lvl,eloc):
        if lvl == 1:
            enemy = Enemy(eloc[0],eloc[1],'crab.png') # spawn enemy
            enemy1 =  Enemy(eloc[2],eloc[3],'crab.png')
            enemy2= Enemy(eloc[4],eloc[5],'krill.png')
            enemy_list = pygame.sprite.Group() # create enemy group
            enemy_list.add(enemy)  
            enemy_list.add(enemy1)   
            enemy_list.add(enemy2)         # add enemies to group
           
        if lvl == 2:
            print("Level " + str(lvl) )

        return enemy_list

    def loot(lvl,tx,ty):
        if lvl == 1:
            loot_list = pygame.sprite.Group()
            loot = Platform   (lloc[0],lloc[1],tx,ty, 'candle.png')
            loot1 = Platform  (lloc[2],lloc[3],tx,ty, 'candle.png')
            loot2 = Platform  (lloc[4],lloc[5],tx,ty, 'candle.png')
            loot3 = Platform  (lloc[6],lloc[7],tx,ty, 'candle.png')

            loot_list.add(loot)
            loot_list.add(loot1)
            loot_list.add(loot2)
            loot_list.add(loot3)

        if lvl == 2:
            print(lvl)

        return loot_list

    def ground(lvl,gloc,tx,ty):
        ground_list = pygame.sprite.Group()
        i=0
        if lvl == 1:
            while i < len(gloc):
                ground = Platform(gloc[i],worldy-ty,tx,ty,'ground.png')
                ground_list.add(ground)
                i=i+1

        if lvl == 2:
            print("Level " + str(lvl) )

        return ground_list

    def platform(lvl,tx,ty):
        plat_list = pygame.sprite.Group()
        ploc = []
        i=0
        if lvl == 1:
            ploc.append((20,worldy-ty-192,4))
            ploc.append((300,worldy-ty-256,3))
            ploc.append((500,worldy-ty-128,4))

            while i < len(ploc):
                j=0
                while j <= ploc[i][2]:
                    plat = Platform((ploc[i][0]+(j*tx)),ploc[i][1],tx,ty,'cloud.png')
                    plat_list.add(plat)
                    j=j+1
                print('run' + str(i) + str(ploc[i]))
                i=i+1

        if lvl == 2:
            print("Level " + str(lvl) )

        return plat_list

def stats(score,health):
    myfont.render_to(world, (4, 4), "Score:"+str(score), WHITE, None, size=64)
    myfont.render_to(world, (4, 72), "Health:"+str(health), WHITE, None, size=64)

def showendscreen():
        myfont.render_to(endsurf, (worldx/2-40, worldy/2), "You are reborn", WHITE, None, size=64)

def terminate() :          
    pygame.quit()
    sys.exit()
    main = False


   
       

'''
Setup
'''
worldx = 960
worldy = 720

fps = 30 # frame rate
ani = 3  # animation cycles
clock = pygame.time.Clock()
pygame.init()
main = True

BLUE  = (25,25,200)
BLACK = (23,23,23 )
WHITE = (254,254,254)
SNOWGRAY = (137,164,166)
ALPHA = (0,0,0)
   
world = pygame.display.set_mode([worldx,worldy])

backdrop = pygame.image.load(os.path.join('images','stage.png')).convert()
backdropbox = world.get_rect()
player = Player() # spawn player
player.rect.x = 0
player.rect.y = 0
player_list = pygame.sprite.Group()
player_list.add(player)
steps = 10
forwardx = 600
backwardx = 230

eloc = []
eloc = [60,200,280,300,460,50]
gloc = []
lloc= []
lloc=[60,360,140,240,0,0,0,0,0]
tx = 64 #tile size
ty = 64 #tile size

font_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"fonts","ani.ttf")
font_size = tx
myfont = pygame.freetype.Font(font_path, font_size)
   
i=0
while i <= (worldx/tx)+tx:
    gloc.append(i*tx)
    i=i+1
    print('Game Time'+str(i))

enemy_list = Level.bad( 1, eloc )
ground_list = Level.ground( 1,gloc,tx,ty )
plat_list = Level.platform( 1,tx,ty )
loot_list = Level.loot(1,tx,ty)

'''
Game over and Thanks for Playing Rectangles

# create the surfaces to hold game text - to be implemented 
gameOverSurf = myfont.render('You are reborn', WHITE, None, size=16)
gameOverRect = gameOverSurf.get_rect()
gameOverRect.center = (worldx/2, worldy/2)

winSurf = myfont.render('Thanks for Playing MyPySky Alpha', WHITE,None, size=10 )
winRect = winSurf.get_rect()
winRect.center = (worldx/2, worldy/2)

winSurf2 = myfont.render('(Press "q" to quit.)', WHITE,None, size=10)
winRect2 = winSurf2.get_rect()
winRect2.center = (worldx/2, worldy/2 + 30)
'''

'''
Main loop
'''
while main == True:
    pygame.display.set_caption('MyPySky!- python based Sky Fan art game')

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == ord('a'):
               player.control(-steps,0)
            if event.key == pygame.K_RIGHT or event.key == ord('d'):
                player.control(steps,0)
            if event.key == pygame.K_UP or event.key == ord('w'):
                player.control(0,-steps)
            if event.key == pygame.K_DOWN or event.key == ord('s'):
                player.control(0,steps)                
            if event.key == pygame.K_SPACE or event.key == ord('x'):
                print('jump')

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == ord('a'):
                player.control(steps,0)
            if event.key == pygame.K_RIGHT or event.key == ord('d'):
                player.control(-steps,0)
            if event.key == pygame.K_UP or event.key == ord('w'):
                player.control(0,-steps*4)
            if event.key == pygame.K_DOWN or event.key == ord('s'):
                player.control(0,steps)                
            if event.key == pygame.K_SPACE or event.key == ord('x'):
                player.jump(plat_list)
            if event.key == pygame.K_ESCAPE or event.key == ord('q'):
                terminate()
            

   

    # scroll the world forward
    if player.rect.x >= forwardx:
        scroll = player.rect.x - forwardx
        player.rect.x = forwardx
        for p in plat_list:
            p.rect.x -= scroll
        for e in enemy_list:
            e.rect.x -= scroll
        for l in loot_list:

            l.rect.x -= scroll
               
    # scroll the world backward
    if player.rect.x <= backwardx:
        scroll = backwardx - player.rect.x
        player.rect.x = backwardx
        for p in plat_list:
            p.rect.x += scroll
        for e in enemy_list:
            e.rect.x += scroll
        for l in loot_list:
            l.rect.x += scroll
    
    world.blit(backdrop, backdropbox)
    player.gravity() # check gravity
    player.update()
    player_list.draw(world) #refresh player position
    enemy_list.draw(world)  # refresh enemies
    ground_list.draw(world)  # refresh grounds
    plat_list.draw(world)   # refresh platforms
    loot_list.draw(world)   # refresh loot
    for e in enemy_list:
        e.move()
    if player.score > 5: 
        showwinscreen()
    
    if player.health < 1:
        showendscreen()
    
    stats(player.score,player.health) # draw text
    pygame.display.flip()
    clock.tick(fps)

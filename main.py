"""
MyPySky

created by mitradranirban

Pygame based platform scroller with sky fan art

distributed under GNU All-Permissive licence

Copying and distribution of this file, with or without modification,
are permitted in any medium without royalty provided the copyright
notice and this notice are preserved.  This file is offered as-is,
without any warranty.
"""

import pygame
import pygame.freetype
from pygame.locals import *
import os
import random

# Initiate pygame modules
pygame.init()
pygame.mixer.init()

# Colors
BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)
BLUE     = (   0,   0, 255)
GRAY     = ( 230, 230, 230)
GREY     = ( 127, 127, 127)

# Screen and tiles dimensions
SCREEN_WIDTH  = 1054
SCREEN_HEIGHT = 594
TILEX = 100
TILEY = 50

# pictures used for tiles
GRASS = 'grass.png'
STONE = 'stone.png'
ICE = 'ice.png'
SAND = 'sand.png'
CLOUD = 'cloud.png'
MANTA = 'manta.png'
JELLYFISH = 'jellyfish.png'
CANDLE = 'candle.png'
STAR = 'star.png'
KRILL = 'krill.png'
ROCK = 'rock.png'
ARC = 'arc.png'
STATUE = 'boy.png'
PLANT = 'plant.png'

# create the pygame font object
font_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"fonts","ani.ttf")
font_size = TILEY
myfont = pygame.freetype.Font(font_path, font_size)

# sounds used for effect
s = 'sounds'
tada = pygame.mixer.Sound(os.path.join(s, 'tada.OGG'))
wow = pygame.mixer.Sound(os.path.join(s, 'wow.OGG'))
tung = pygame.mixer.Sound(os.path.join(s, 'tung.OGG'))

"""
Create objects required
for the game
"""

class Player(pygame.sprite.Sprite):

    """ This class represents the player at the bottom that the player
    controls. """

    # -- Attributes
    # Set speed vector of player
    change_x = 0
    change_y = 0



    # This holds all the images for the animated walk left/right
    # of our player
    walking_frames_l = []
    walking_frames_r = []

    # What direction is the player facing?
    direction = "R"

    # List of sprites we can bump against
    level = None

    # -- Methods
    def __init__(self):
        """ Constructor function """
        # Call the parent's constructor
        pygame.sprite.Sprite.__init__(self)

        # Load all the right facing images into a list
        for i in range(1,9):
            image = pygame.image.load(os.path.join('images','child'+str(i)+'.png'))
            self.walking_frames_r.append(image)


        # Load all the right facing images, then flip them
        # to face left.
        for i in range(1,9):
            image = pygame.image.load(os.path.join('images','child'+str(i)+'.png'))
            image = pygame.transform.flip(image, True, False)
            self.walking_frames_l.append(image)


        # Set the image the player starts with
        self.image = self.walking_frames_r[0]

        # Set a referance to the image rect.
        self.rect = self.image.get_rect()
        # Set Baseline score, health and collide delta

        self.health = 1
        self.damage = 0
        self.collide_delta = 0
        self.jump_delta = 6
        self.score = 1

    def update(self):
        """ Move the player. """
        # Gravity
        self.calc_grav()
        # Move left/right
        self.rect.x += self.change_x
        pos = self.rect.x + self.level.world_shift
        if self.direction == "R":
            frame = (pos // 30) % len(self.walking_frames_r)
            self.image = self.walking_frames_r[frame]
        else:
            frame = (pos // 30) % len(self.walking_frames_l)
            self.image = self.walking_frames_l[frame]

        # See if we hit anything
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            # If we are moving right,
            # set our right side to the left side of the item we hit
            if self.change_x > 0:
                self.rect.right = block.rect.left
            elif self.change_x < 0:
                # Otherwise if we are moving left, do the opposite.
                self.rect.left = block.rect.right

        # increase score  by collecting candles
        loot_hit_list = pygame.sprite.spritecollide(self, self.level.loot_list, False)
        for loot in loot_hit_list:
            self.level.loot_list.remove(loot)
            pygame.mixer.Sound.play(tada)
            self.score += 1

        # increase health by collecting stars
        star_hit_list = pygame.sprite.spritecollide(self, self.level.star_list, False)
        for star in star_hit_list:
            self.level.star_list.remove(star)
            pygame.mixer.Sound.play(tung)
            self.health += 1

        # contact with enemy

        enemy_hit_list = pygame.sprite.spritecollide(self, self.level.enemy_list, False)
        if self.damage == 0:
            for enemy in enemy_hit_list:
                if not self.rect.contains(enemy):
                    self.damage = self.rect.colliderect(enemy)
        if self.damage == 1:
            idx = self.rect.collidelist(enemy_hit_list)
            if idx == -1:
                self.damage = 0   # set damage back to 0
                pygame.mixer.Sound.play(wow)
                self.health -= 1  # subtract 1 hp

        # Move up/down

        self.rect.y += self.change_y


        # Move up/down
        self.rect.y += self.change_y

        # Check and see if we hit anything
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:

            # Reset our position based on the top/bottom of the object.
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
            elif self.change_y < 0:
                self.rect.top = block.rect.bottom

            # Stop our vertical movement
            self.change_y = 0

            if isinstance(block, MovingPlatform):
                self.rect.x += block.change_x

    def calc_grav(self):
        """ Calculate effect of gravity. """
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += .35

        # See if we are on the ground.
        if self.rect.y >= SCREEN_HEIGHT - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = SCREEN_HEIGHT - self.rect.height

    def jump(self):
        """ Called when user hits 'jump' button. """

        # move down a bit and see if there is a platform below us.
        # Move down 2 pixels because it doesn't work well if we only move down 1
        # when working with a platform moving down.
        self.rect.y += 2
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        self.rect.y -= 2

        # If it is ok to jump, set our speed upwards
        if len(platform_hit_list) > 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.change_y = -7

    # Player-controlled movement:
    def go_left(self):
        """ Called when the user hits the left arrow. """
        self.change_x = -6
        self.direction = "L"

    def go_right(self):
        """ Called when the user hits the right arrow. """
        self.change_x = 6
        self.direction = "R"

    def stop(self):
        """ Called when the user lets off the keyboard. """
        self.change_x = 0

class Enemy(pygame.sprite.Sprite):

    ''' Spawn an enemy '''
    def __init__(self,x,y,img):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join('images',img))
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.counter = 0
        self.change_x = 0
        self.change_y = 0
        self.boundary_top = 0
        self.boundary_bottom = 0
        self.boundary_left = 0
        self.boundary_right = 0

    def update(self):
        ''' enemy movement '''
        # Move left/right
        self.rect.x += self.change_x

        # See if we hit the player
        hit = pygame.sprite.collide_rect(self, self.player)
        if hit:
            # We did hit the player. Shove the player around and
            # assume he/she won't hit anything else.

            # If we are moving right, set our right side
            # to the left side of the item we hit
            if self.change_x < 0:
                self.player.rect.right = self.rect.left
            else:
                # Otherwise if we are moving left, do the opposite.
                self.player.rect.left = self.rect.right

        # Move up/down
        self.rect.y += self.change_y

        # Check and see if we hit the player
        hit = pygame.sprite.collide_rect(self, self.player)
        if hit:
            # We did hit the player. Shove the player around and
            # assume he/she won't hit anything else.

            # Reset our position based on the top/bottom of the object.
            if self.change_y < 0:
                self.player.rect.bottom = self.rect.top
            else:
                self.player.rect.top = self.rect.bottom

        # Check the boundaries and see if we need to reverse
        # direction.
        if self.rect.bottom > self.boundary_bottom or self.rect.top < self.boundary_top:
            self.change_y *= -1

        cur_pos = self.rect.x - self.level.world_shift
        if cur_pos < self.boundary_left or cur_pos > self.boundary_right:
            self.change_x *= -1


def load_image(self, width, height):
    """ load a single image from image folder and make a pygame sprite. """
    # Create a new blank image
    image = pygame.Surface([width, height]).convert()

    # Load the sprite from images folder
    pygame.image.load(os.path.join('images',image)).convert()

    # Assuming black works as the transparent color
    image.set_colorkey(BLACK)

    # Return the image
    return image

class Platform(pygame.sprite.Sprite):

    """ Platform the user can jump on """

    def __init__(self, xlocation, ylocation, imagewidth, imageheight, image):
        """ Platform constructorfrom individual images. """
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load(os.path.join('images',image)).convert()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.y = ylocation
        self.rect.x = xlocation

class MovingPlatform(Platform):

    """ This is a fancier platform that can actually move. """
    change_x = 0
    change_y = 0

    boundary_top = 0
    boundary_bottom = 0
    boundary_left = 0
    boundary_right = 0

    level = None
    player = None

    def update(self):
        """ Move the platform.
            If the player is in the way, it will shove the player
            out of the way. This does NOT handle what happens if a
            platform shoves a player into another object. Make sure
            moving platforms have clearance to push the player around
            or add code to handle what happens if they don't. """

        # Move left/right
        self.rect.x += self.change_x

        # See if we hit the player
        hit = pygame.sprite.collide_rect(self, self.player)
        if hit:
            # We did hit the player. Shove the player around and
            # assume he/she won't hit anything else.

            # If we are moving right, set our right side
            # to the left side of the item we hit
            if self.change_x < 0:
                self.player.rect.right = self.rect.left
            else:
                # Otherwise if we are moving left, do the opposite.
                self.player.rect.left = self.rect.right

        # Move up/down
        self.rect.y += self.change_y

        # Check and see if we the player
        hit = pygame.sprite.collide_rect(self, self.player)
        if hit:
            # We did hit the player. Shove the player around and
            # assume he/she won't hit anything else.

            # Reset our position based on the top/bottom of the object.
            if self.change_y < 0:
                self.player.rect.bottom = self.rect.top
            else:
                self.player.rect.top = self.rect.bottom

        # Check the boundaries and see if we need to reverse
        # direction.
        if self.rect.bottom > self.boundary_bottom or self.rect.top < self.boundary_top:
            self.change_y *= -1

        cur_pos = self.rect.x - self.level.world_shift
        if cur_pos < self.boundary_left or cur_pos > self.boundary_right:
            self.change_x *= -1

class loot(Platform):

    """ A special platform player will collect to increase score. """
    level = None
    player = None

class star(Platform):

    """ A special platform player wil collect to increase health. """
    level = None
    player = None

class Level():

    """ This is a generic super-class used to define a level.
        Create a child class for each level with level-specific
        info. """
    # Lists of sprites used in all levels. Add or remove
    # lists as needed for your game. """
    platform_list = None
    enemy_list = None
    loot_list = None
    star_list = None

    # Background image
    background = None

    # How far this world has been scrolled left/right
    world_shift = 0
    level_limit = -1000

    def __init__(self, player):
        """ Constructor. Pass in a handle to player. Needed for when moving platforms collide with the player. """
        self.platform_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()
        self.loot_list = pygame.sprite.Group()
        self.star_list = pygame.sprite.Group()
        self.player = player

    # Update everything on this level
    def update(self):
        """ Update everything in this level."""
        self.platform_list.update()
        self.enemy_list.update()
        self.loot_list.update()
        self.star_list.update()

    def draw(self, screen):
        """ Draw everything on this level. """
        # Draw the background
        # We don't shift the background as much as the sprites are shifted
        # to give a feeling of depth.
        screen.fill(WHITE)
        screen.blit(self.background,(self.world_shift // 3,0))

        # Draw all the sprite lists that we have
        self.platform_list.draw(screen)
        self.enemy_list.draw(screen)
        self.loot_list.draw(screen)
        self.star_list.draw(screen)

    def shift_world(self, shift_x):
        """ When the user moves left/right and we need to scroll everything: """

        # Keep track of the shift amount
        self.world_shift += shift_x

        # Go through all the sprite lists and shift
        for platform in self.platform_list:
            platform.rect.x += shift_x

        for enemy in self.enemy_list:
            enemy.rect.x += shift_x

        for loot in self.loot_list:
            loot.rect.x += shift_x

        for star in self.star_list:
            star.rect.x += shift_x

# Create platforms for the level
class Level_01(Level):

    """ Definition for level 1. """

    def __init__(self, player):
        """ Create level 1. """
        # Call the parent constructor
        Level.__init__(self, player)
        self.background = pygame.image.load(os.path.join('images',"home.png")).convert()
        self.background.set_colorkey(BLACK)
        self.level_limit = -2500

        # Array with type of platform, and x, y location of the platform.
        level = [ [GRASS, 400, 500],
                  [SAND, 700, 500],
                  [ICE, 1800, 500],
                  [ICE, 1900, 500],
                  [STONE, 2200,500],
                  [STONE, 2800,500],
                  [STONE, 3200,500],
                  [STONE, 4000,500]
                   ]


        # Go through the array above and add platforms
        for platform in level:
            block = Platform(platform[1],platform[2], TILEX, TILEY,platform[0])
            block.rect.x = platform[1]
            block.rect.y = platform[2]
            block.player = self.player
            self.platform_list.add(block)

        # Add loot
        level = [ [  CANDLE, 100, 400],
                  [  CANDLE, 1700, 500]
                 ]
        for platform in level:
            block =   Platform(platform[1],platform[2], TILEX, TILEY,platform[0])
            block.rect.x = platform[1]
            block.rect.y = platform[2]
            block.player = self.player
            self.loot_list.add(block)
# Create platforms for the level 2
class Level_02(Level):

    """ Definition for level 2. """

    def __init__(self, player):
        """ Create level 2. """
        # Call the parent constructor
        Level.__init__(self, player)
        self.background = pygame.image.load(os.path.join('images',"isle.png")).convert()
        self.background.set_colorkey( BLUE)
        self.level_limit = -2600

        # Array with type of platform, and x, y location of the platform.
        level = [ [  SAND, 500, 550 ],
                  [  SAND, 600, 450],
                  [  SAND, 700, 350],
                  [  SAND, 900, 350],
                  [  STONE, 1100, 300],
                  [  GRASS, 2200, 400],
                  [  GRASS, 2400, 450]
                  ]

        # Go through the array above and add platforms
        for platform in level:
            block =   Platform(platform[1],platform[2], TILEX, TILEY,platform[0])
            block.rect.x = platform[1]
            block.rect.y = platform[2]
            block.player = self.player
            self.platform_list.add(block)

        # Add a custom moving platform
        block =   MovingPlatform(1350,280, TILEX, TILEY,  CLOUD)
        block.rect.x = 2150
        block.rect.y = 280
        block.boundary_left = 1150
        block.boundary_right = 2150
        block.change_x = 1
        block.player = self.player
        block.level = self
        self.platform_list.add(block)

        # Add candles
        level = [ [  CANDLE, 1700, 100],
                  [  CANDLE, 2400, 300]
                 ]
        for platform in level:
            block =   Platform(platform[1],platform[2], TILEX, TILEY,platform[0])
            block.rect.x = platform[1]
            block.rect.y = platform[2]
            block.player = self.player
            self.loot_list.add(block)

        # Add star
        level = [ [  STAR, 700, 300],
                  [  STAR, 2200, 300]
                 ]
        for platform in level:
            block =   Platform(platform[1],platform[2], TILEX, TILEY,platform[0])
            block.rect.x = platform[1]
            block.rect.y = platform[2]
            block.player = self.player
            self.star_list.add(block)
# Create platforms for the level 3
class Level_03(Level):

    """ Definition for level 3. """

    def __init__(self, player):
        """ Create level 3. """
        # Call the parent constructor
        Level.__init__(self, player)
        self.background = pygame.image.load(os.path.join('images',"prairie.png")).convert()
        self.background.set_colorkey( WHITE)
        self.level_limit = -2500

         # Array with type of platform, and x, y location of the platform.
        level = [ [  STONE, 500, 500, ],
                  [  STONE, 700, 450],
                  [  STONE, 900, 450],
                  [  GRASS, 1100, 400],
                  [  GRASS, 1300, 350],
                  [  GRASS, 1500, 300],
                  [  GRASS, 2500, 300],
                  [  GRASS, 2700, 350],
                  [  STONE, 3000, 280],
                  [  STONE, 3200, 400],
                  [  STONE, 3400, 500],
                  ]

        # Go through the array above and add platforms
        for platform in level:
            block =   Platform(platform[1],platform[2], TILEX, TILEY,platform[0])
            block.rect.x = platform[1]
            block.rect.y = platform[2]
            block.player = self.player
            self.platform_list.add(block)

          # Add a custom moving platform
        block =   MovingPlatform(1950,280, TILEX, TILEY,  MANTA)
        block.rect.x = 1950
        block.rect.y = 280
        block.boundary_left = 1650
        block.boundary_right = 2400
        block.change_x = 1
        block.player = self.player
        block.level = self
        self.platform_list.add(block)

        # Add enemy
        enemy = Enemy(600,400,"crab.png")
        enemy.rect.x = 600
        enemy.rect.y = 400
        enemy.boundary_left = 500
        enemy.boundary_right = 700
        enemy.change_x = random.randint(3,5)
        enemy.player = self.player
        enemy.level = self
        self.enemy_list.add(enemy)
   # Add candles
        level = [
                [ CANDLE, 1200, 300],
                [ PLANT, 2200, 200],
                [ CANDLE, 2700, 300]
                 ]
        for platform in level:
            block =   Platform(platform[1],platform[2], TILEX, TILEY,platform[0])
            block.rect.x = platform[1]
            block.rect.y = platform[2]
            block.player = self.player
            self.loot_list.add(block)

        # Add star
        level = [ [  STAR, 500, 400],
                  [  STAR, 3200, 350]
                 ]
        for platform in level:
            block =   Platform(platform[1],platform[2], TILEX, TILEY,platform[0])
            block.rect.x = platform[1]
            block.rect.y = platform[2]
            block.player = self.player
            self.star_list.add(block)
# Create platforms for the level 4
class Level_04(Level):
   
    """ Definition for level 4. """

    def __init__(self, player):
        """ Create level 4. """
        # Call the parent constructor
        Level.__init__(self, player)

        self.background = pygame.image.load(os.path.join('images',"forest.png")).convert()
        self.background.set_colorkey(WHITE)
        self.level_limit = -2500

        # Array with type of platform, and x, y location of the platform.
        level = [ [  STONE, 500, 500, ],
                  [  STONE, 700, 400],
                  [  GRASS, 900, 350],
                  [  GRASS, 1100, 300],
                  [  GRASS, 1300, 400],
                  [  STONE, 1600, 100],
                  [  STONE, 1700, 200],
                  [  STONE, 1800, 500],
                  [ GRASS, 2000,450],
                  [ GRASS, 2200,450],
                  [ GRASS, 2400,450],
                  [ GRASS, 2600,450],
                  ]


        # Go through the array above and add platforms
        for platform in level:
            block =   Platform(platform[1],platform[2], TILEX, TILEY,platform[0])
            block.rect.x = platform[1]
            block.rect.y = platform[2]
            block.player = self.player
            self.platform_list.add(block)

        # Add a custom moving platform
        block =   MovingPlatform(1500,300,TILEX,TILEY,  JELLYFISH)
        block.rect.x = 1500
        block.rect.y = 300
        block.boundary_top = 100
        block.boundary_bottom = 550
        block.change_y = -1
        block.player = self.player
        block.level = self
        self.platform_list.add(block)

        # Add enemies
        enemy = Enemy(1300,500,"rain.png")
        enemy.rect.x = 800
        enemy.rect.y = 500
        enemy.boundary_top = 300
        enemy.boundary_bottom = 550
        enemy.change_y = random.randint(1,5)
        enemy.player = self.player
        enemy.level = self
        self.enemy_list.add(enemy)

        enemy = Enemy(1900,500,"crab.png")
        enemy.rect.x = 1900
        enemy.rect.y = 500
        enemy.boundary_left = random.randint(1700,1850)
        enemy.boundary_right = random.randint(1950,2000)
        enemy.change_x = random.randint(1,5)
        enemy.player = self.player
        enemy.level = self
        self.enemy_list.add(enemy)
  # Add candles
        level = [
                [ PLANT, 800, 300],
                [ CANDLE, 1200, 300],
                [ PLANT, 2000, 400]
                 ]
        for platform in level:
            block =   Platform(platform[1],platform[2], TILEX, TILEY,platform[0])
            block.rect.x = platform[1]
            block.rect.y = platform[2]
            block.player = self.player
            self.loot_list.add(block)

        # Add star
        level = [ [  STAR, 1900, 450],
                  [  STAR, 1600, 50]
                 ]
        for platform in level:
            block =   Platform(platform[1],platform[2], TILEX, TILEY,platform[0])
            block.rect.x = platform[1]
            block.rect.y = platform[2]
            block.player = self.player
            self.star_list.add(block)
# Create platforms for the level 5
class Level_05(Level):

    """ Definition for level 5. """
    def __init__(self, player):
        """ Create level 5. """
        # Call the parent constructor
        Level.__init__(self, player)

        self.background = pygame.image.load(os.path.join('images',"valley.png")).convert()
        self.level_limit = -2000
        level = [ [  SAND, 500, 550 ],
                  [  SAND, 600, 450],
                  [  SAND, 700, 350],
                  [  ICE, 900, 450],
                  [  ICE, 1100, 300],
                  [  ICE, 1300, 280],
                  [  STONE, 1650, 280],
                  [  STONE, 1750, 400],
                  [  STONE, 1850, 400],
                  [ SAND, 2000,450],
                  [ GRASS, 2200,400],
                  [ STONE, 2400,350],
                  [ STONE, 2600,350],
                  [ STONE, 2900,350],
                  ]
 

        # Go through the array above and add platforms
        for platform in level:
            block =   Platform(platform[1],platform[2], TILEX, TILEY,platform[0])
            block.rect.x = platform[1]
            block.rect.y = platform[2]
            block.player = self.player
            self.platform_list.add(block)

 # Add candles
        level = [ 
                [ CANDLE, 1100, 200],
                [ CANDLE, 1900, 300],
                [ CANDLE, 2700, 300]
                 ]
        for platform in level:
            block =   Platform(platform[1],platform[2], TILEX, TILEY,platform[0])
            block.rect.x = platform[1]
            block.rect.y = platform[2]
            block.player = self.player
            self.loot_list.add(block)

        # Add star
        level = [ [  STAR, 700, 300],
                  [  STAR, 1700, 300]
                 ]
        for platform in level:
            block =   Platform(platform[1],platform[2], TILEX, TILEY,platform[0])
            block.rect.x = platform[1]
            block.rect.y = platform[2]
            block.player = self.player
            self.star_list.add(block)
# Create platforms for the level 6
class Level_06(Level):
   
    """ Definition for level 6. """

    def __init__(self, player):
        """ Create level 6. """
        # Call the parent constructor
        Level.__init__(self, player)

        self.background = pygame.image.load(os.path.join('images',"wasteland.png")).convert()
        self.background.set_colorkey( WHITE)
        self.level_limit = -2500
    


        # Array with type of platform, and x, y location of the platform.
        level = [ [  STONE, 500, 550],
                  [  STONE, 900, 500],
                  [  GRASS, 1100, 450],
                  [  GRASS, 1400, 450],
                  [  GRASS, 1600, 450],
                  [  GRASS, 1900, 400],
                  [  GRASS, 2200, 300],
                  [  GRASS, 2400, 200],
                  [  STONE, 2600, 100],
                  [  STONE, 2800, 500],
                  [  STONE, 3000, 400],
                  [  STONE, 3300, 350],
                  [  STONE, 3600, 300],
                  ]

        # Go through the array above and add platforms
        for platform in level:
            block =   Platform(platform[1],platform[2], TILEX, TILEY,platform[0])
            block.rect.x = platform[1]
            block.rect.y = platform[2]
            block.player = self.player
            self.platform_list.add(block)

        # Add a custom moving platform
        block =   MovingPlatform(700,300,TILEX,TILEY, ARC)
        block.rect.x = 700
        block.rect.y = 300
        block.boundary_top = 200
        block.boundary_bottom = 550
        block.change_y = -1
        block.player = self.player
        block.level = self
        self.platform_list.add(block)

        # Add enemies
        enemy = Enemy(2700,500,"krill.png")
        enemy.rect.x = 2700
        enemy.rect.y = 300
        enemy.boundary_top = 100
        enemy.boundary_bottom = 550
        enemy.boundary_left = 2000
        enemy.boundary_right = 2900
        enemy.change_x = random.randint(3,5)
        enemy.change_y = random.randint(3,5)
        enemy.player = self.player
        enemy.level = self
        self.enemy_list.add(enemy)

        enemy = Enemy(1900,500,"crab.png")
        enemy.rect.x = 1400
        enemy.rect.y = 500
        enemy.boundary_left = random.randint(1300,1350)
        enemy.boundary_right = random.randint(1450,1500)
        enemy.change_x = random.randint(1,5)
        enemy.player = self.player
        enemy.level = self
        self.enemy_list.add(enemy)

        # Add candles
        level = [ 
                [ CANDLE, 1500, 300],
                [ PLANT, 3000, 300],
                [ PLANT, 2200, 350],
                [ PLANT, 3700, 350],
                 ]
        for platform in level:
            block =   Platform(platform[1],platform[2], TILEX, TILEY,platform[0])
            block.rect.x = platform[1]
            block.rect.y = platform[2]
            block.player = self.player
            self.loot_list.add(block)

        # Add star
        level = [ [ STAR, 700, 100],
                  [ STAR, 1300, 450],
                  [ STAR, 2600, 50],
                 ]
        for platform in level:
            block =   Platform(platform[1],platform[2], TILEX, TILEY,platform[0])
            block.rect.x = platform[1]
            block.rect.y = platform[2]
            block.player = self.player
            self.star_list.add(block)
# Create platforms for the level 7
class Level_07(Level):
   
    """ Definition for level 7. """

    def __init__(self, player):
        """ Create level 7. """
        # Call the parent constructor
        Level.__init__(self, player)

        self.background = pygame.image.load(os.path.join('images',"vault.png")).convert()
        self.background.set_colorkey( WHITE)
        self.level_limit = -2500
 # Array with type of platform, and x, y location of the platform.
        level = [ [  STONE, 600, 450],
                  [  STONE, 1800, 300],
                  [  STONE, 1500, 350],
                  [ STONE, 1900, 400],
                  [  STONE, 1700, 200],
                  [  STONE, 1400, 250],
                  [  STONE, 1200, 300],
                  [  STONE, 1900, 100],
                  [  STONE, 2300, 200],
                  [  STONE, 2600, 100],
                  [ STONE, 2800,100],
                  [ STONE, 3000, 100]
                  ]


        # Go through the array above and add platforms
        for platform in level:
            block =   Platform(platform[1],platform[2], TILEX, TILEY,platform[0])
            block.rect.x = platform[1]
            block.rect.y = platform[2]
            block.player = self.player
            self.platform_list.add(block)

        # Add a custom moving platform
        block =   MovingPlatform(1600,300,TILEX,TILEY, STONE)
        block.rect.x = 1600
        block.rect.y = 300
        block.boundary_top = 100
        block.boundary_bottom = 550
        block.change_y = -1
        block.player = self.player
        block.level = self
        self.platform_list.add(block)
        
        # Add candles
        level = [ 
                [ CANDLE, 600, 350],
                [ CANDLE, 1200, 200],
                [ CANDLE, 2700, 20]
                 ]
        for platform in level:
            block =   Platform(platform[1],platform[2], TILEX, TILEY,platform[0])
            block.rect.x = platform[1]
            block.rect.y = platform[2]
            block.player = self.player
            self.loot_list.add(block)

        # Add star
        level = [ [  STAR, 1900, 50],
                  [  STAR, 3200, 100]
                 ]
        for platform in level:
            block =   Platform(platform[1],platform[2], TILEX, TILEY,platform[0])
            block.rect.x = platform[1]
            block.rect.y = platform[2]
            block.player = self.player
            self.star_list.add(block)
# Create platforms for the level 8
class Level_08(Level):
    
    """ Definition for level 8. """

    def __init__(self, player):
        """ Create level 8. """
        # Call the parent constructor
        Level.__init__(self, player)

        self.background = pygame.image.load(os.path.join('images',"eden.png")).convert()
        self.level_limit = -2500
        level = [ [ STONE, 600, 450],
                  [ STONE, 800, 350],
                  [ STONE, 1000, 300],
                  [ STONE, 1200, 330],
                  [ ICE, 1200, 550],
                  [ ICE, 1200, 400],
                  [ STONE, 1500, 250],
                  [ STONE, 1800, 200],
                  [ STONE, 2000, 300],
                  [ STONE, 2300, 400],
                  [ STONE, 2600, 550]
                  ]


        # Go through the array above and add platforms
        for platform in level:
            block =   Platform(platform[1],platform[2], TILEX, TILEY,platform[0])
            block.rect.x = platform[1]
            block.rect.y = platform[2]
            block.player = self.player
            self.platform_list.add(block)

       # Add enemies
        enemy = Enemy(700,300,"rock.png")
        enemy.rect.x = 700
        enemy.rect.y = 300
        enemy.boundary_top = 100
        enemy.boundary_bottom = 550
        enemy.change_y = 5
        enemy.player = self.player
        enemy.level = self
        self.enemy_list.add(enemy)

        enemy = Enemy(1200,300,"krill.png")
        enemy.rect.x = 1200
        enemy.rect.y = 300
        enemy.boundary_top = 100
        enemy.boundary_bottom = 550
        enemy.boundary_left = 1000
        enemy.boundary_right = 1400
        enemy.change_x = random.randint(3,5)
        enemy.change_y = random.randint(3,5)
        enemy.player = self.player
        enemy.level = self
        self.enemy_list.add(enemy)
       
        enemy = Enemy(2700,500,"rock.png")
        enemy.rect.x = 2700
        enemy.rect.y = 300
        enemy.boundary_top = 100
        enemy.boundary_bottom = 550
        enemy.boundary_left = 2500
        enemy.boundary_right = 2900
        enemy.change_x = random.randint(3,5)
        enemy.change_y = random.randint(3,5)
        enemy.player = self.player
        enemy.level = self
        self.enemy_list.add(enemy)
 # Add candles
        level = [ 
                [ STATUE, 2600, 500],
                [ STATUE, 2900, 500],
                [ STATUE, 3200, 500]
                 ]

        for platform in level:
            block =   Platform(platform[1],platform[2], TILEX, TILEY,platform[0])
            block.rect.x = platform[1]
            block.rect.y = platform[2]
            block.player = self.player
            self.loot_list.add(block)

        # Add star
        level = [ [ STAR, 1100, 200],
                  [ STAR, 1900, 200],
                  [ STAR, 1950,150],

                 ]
        for platform in level:
            block =   Platform(platform[1],platform[2], TILEX, TILEY,platform[0])
            block.rect.x = platform[1]
            block.rect.y = platform[2]
            block.player = self.player
            self.star_list.add(block)
# Create platforms for the level 9
class Level_09(Level):

    """ Definition for level 9. """

    def __init__(self, player):
        """ Create level 9. """
        # Call the parent constructor
        Level.__init__(self, player)

        self.background = pygame.image.load(os.path.join('images',"orbit.png")).convert()
        self.level_limit = -2500
        
        # Add candles
        level = [ 
                [ CANDLE, 400, 500],
                [ CANDLE, 1000, 400],
                [ CANDLE, 2100, 400]
                 ]
        for platform in level:
            block =   Platform(platform[1],platform[2], TILEX, TILEY,platform[0])
            block.rect.x = platform[1]
            block.rect.y = platform[2]
            block.player = self.player
            self.loot_list.add(block)

def main():
    """ Main Program """
    

    # Set the height and width of the screen
    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size)
    gui = pygame.Surface(size, SRCALPHA)
    gui.fill((255,255,255,228))
    screen.blit(gui,(0,0))

    icon = pygame.image.load(os.path.join('images', CANDLE))
    pygame.display.set_caption("MyPySky python based sky fan art game")
    pygame.display.set_icon(icon)

    # Create the player
    player = Player()

    # Create all the levels
    level_list = []
    level_list.append(Level_01(player))
    level_list.append(Level_02(player))
    level_list.append(Level_03(player))
    level_list.append(Level_04(player))
    level_list.append(Level_05(player))
    level_list.append(Level_06(player))
    level_list.append(Level_07(player))
    level_list.append(Level_08(player))
    level_list.append(Level_09(player))


    # Set the current level
    current_level_no = 0
    current_level = level_list[current_level_no]

    active_sprite_list = pygame.sprite.Group()
    player.level = current_level

    player.rect.x = 140
    player.rect.y = SCREEN_HEIGHT - player.rect.height
    active_sprite_list.add(player)

    #Loop until the user clicks the close button.
    done = False

    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()

    # -------- Main Program Loop -----------
    while not done:
        for event in pygame.event.get(): # User did something
            if event.type == pygame.QUIT: # If user clicked close
                done = True # Flag that we are done so we exit this loop

            if event.type == pygame.KEYDOWN:
                if event.key == K_a or event.key == K_LEFT:
                    player.go_left()
                if event.key == K_d or event.key == K_RIGHT:
                    player.go_right()
                if event.key == K_w or event.key == K_UP:
                    player.jump()
                if event.key == K_q:
                    done = True

            if event.type == pygame.KEYUP:
                if event.key == K_a or event.key == K_LEFT and player.change_x < 0:
                    player.stop()
                if event.key == K_d or event.key == K_RIGHT and player.change_x > 0:
                    player.stop()
            
        # Update the player.
        active_sprite_list.update()

        # Update items in the level
        current_level.update()

        # If the player gets near the right side, shift the world left (-x)
        if player.rect.x >= 800:
            diff = player.rect.x - 800
            player.rect.x = 800
            current_level.shift_world(-diff)

        # If the player gets near the left side, shift the world right (+x)
        if player.rect.x <= 10:
            diff = 10 - player.rect.x
            player.rect.x = 10
            current_level.shift_world(diff)

        def button(msg,x,y,w,h,inactive,active,action=None):
            """create the gui button function"""
            mouse = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()
            print(click)
            if x+w > mouse[0] > x and y+h > mouse[1] > y:
                pygame.draw.rect(gui, active,(x,y,w,h))

                if click[0] == 1 and action != None:
                    action()        
            else:
                pygame.draw.rect(gui, inactive,(x,y,w,h))

            myfont.render_to(screen, (x+w//2,y), msg, WHITE, None, size = TILEY)
        def stats(score,health):
            """display score and health and buttons on the screen"""
            hp = hex(health)
            if health <= 0:
                HI = pygame.image.load(os.path.join('images', 'hi0x0.png'))
            else:
                HI = pygame.image.load(os.path.join('images', 'hi'+str(hp)+'.png'))
                screen.blit(HI, (500,4))
            CANDY = pygame.image.load(os.path.join('images', 'candy.png'))
            screen.blit(CANDY,(4, 4,))
            myfont.render_to(screen,  (54,4), str(score), WHITE, None, size  = TILEY)
            myfont.render_to(screen, (600,4),str(health), WHITE, None, size = TILEY)
            button("<",100,450,50,50, GRAY, GREY,player.go_left)
            button(">",950,450,50,50,GRAY,GREY,player.go_right)
            button("^",125,400,50,50,GRAY,GREY,player.jump)
            button("^",925,400,50,50,GRAY,GREY,player.jump)
            button("||",900,450,50,50,GRAY,GREY, player.stop )
            button("||",150,450,50,50,GRAY,GREY, player.stop )

        # if player health less than zero go to end screen

        if player.health < 0:
            current_level = level_list[8]
            player.level = current_level
            player.rect.x = 1000

        # If the player gets to the end of the level, go to the next level
        current_position = player.rect.x + current_level.world_shift
        if current_position < current_level.level_limit:
            player.rect.x = 120
            if current_level_no < len(level_list)-1:
                current_level_no += 1
                current_level = level_list[current_level_no]
                player.level = current_level

        # ALL CODE TO DRAW SHOULD GO BELOW THIS COMMENT
        current_level.draw(screen)
        active_sprite_list.draw(screen)
        stats(player.score,player.health)

        # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT

        # Limit to 60 frames per second
        clock.tick(60)

        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()

    # Be IDLE friendly. If you forget this line, the program will 'hang'
    # on exit.
    pygame.quit()

if __name__ == "__main__":
    main()

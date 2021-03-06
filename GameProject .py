import pygame
from enum import Enum
from pytmx.util_pygame import load_pygame
import os.path
import pyscroll
import pyscroll.data
from pyscroll.group import PyscrollGroup
import threading
import random

s_width = 800
s_height = 700
play_width = 300  
play_height = 600



top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height

pygame.init()

pygame.mixer.init()
pygame.mixer.music.load("ArcadeMusic.mp3")

pistolSound = pygame.mixer.Sound("pistol.wav")
runSound = pygame.mixer.Sound("running.wav")
hitmarkSound = pygame.mixer.Sound("hitmark.wav")
jumpSound = pygame.mixer.Sound("jump.wav")
damageTakenSound = pygame.mixer.Sound("damageTaken.wav")
enemyGun = pygame.mixer.Sound("enemyGun.wav")
hpGain = pygame.mixer.Sound("hpGain.wav")

pistolSound.set_volume(0.4)

class CurrentAnim(Enum):
    LEFT = 0
    RIGHT = 1
    UP = 2
    
class ObjectType(Enum):
    PLAYER = 0,
    ENEMY = 1,
    BULLET = 2,
    ELEVATOR = 3,
    DOOR = 4
    
class ElevatorDir(Enum):
    UP = 0,
    DOWN = 1

W, H = 1270, 720
# define configuration variables here
RESOURCES_DIR = 'data'
MAP_FILENAME = 'newmap.tmx'


# make loading maps a little easier
def get_map(filename):
    return os.path.join(RESOURCES_DIR, filename)

# make loading images a little easier
def load_image(filename):
    return pygame.image.load(os.path.join(RESOURCES_DIR, filename))

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

screen = pygame.display.set_mode((W, H))
 
def draw_text_middle(text, size, color, surface):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, 1, color)
    surface.blit(label, (W/4, H/2))
    
def draw_final_score(text, size, color, surface):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, 1, color)
    surface.blit(label, (W/3+100, H / 4))

def draw_window(surface):
    surface.fill((0,0,0))
    
    font = pygame.font.SysFont('comicsans', 60)
    label = font.render('Elevator action', 1, (255,255,255))

    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), 30))

#Create the text used to display the score and draw it on the screen
def draw_score(screen, x, y, score):
    font = pygame.font.Font(None, 36)  # Choose the font for the text
    text = font.render("Score = " + str(score), 1, WHITE)  # Create the text
    screen.blit(text, (x, y))  # Draw the text on the screen

def draw_health(screen,x,y,health):
    font = pygame.font.Font(None,36)
    text = font.render("Health = "+ str(health),1, RED)
    screen.blit(text, (x,y))

def pistolFire():
   pygame.mixer.Sound.play(pistolSound)
def run():
    pygame.mixer.Sound.play(runSound) 
    
class GameOverTimer(pygame.sprite.Sprite):
    def __init__(self):
        self.startTime = 30
    def UpdateTimer():
        pass
    def RenderTimer():
        pass

class Door():
     def __init__(self,posX,posY):

        self.positionX = posX
        self.positionY = posY
        self.bIsPlayer = ObjectType.DOOR      
        
class Bullet(pygame.sprite.Sprite):
    def __init__(self,filename,posX,posY,facing):
        pygame.sprite.Sprite.__init__(self)
       
        self.image = pygame.image.load(filename).convert_alpha()
        self.image = pygame.transform.scale(self.image,[5,5])
        self.positionX = posX
        self.positionY = posY
        self.rect = self.image.get_rect()
        self.feet = pygame.Rect(0,0, self.rect.width /2, 8)
        self.left = pygame.Rect(0,0,self.rect.width / 10,20)
        self.right = pygame.Rect(0,0,self.rect.width / 10,20)
        self.vel = 2
        self.bFired = False
        self.bIsPlayer = ObjectType.BULLET
        self.facing = 6*facing
              
            
    def UpdatePosition(self):
        

        self.positionX += self.facing
            
        self.rect.topleft = [self.positionX,self.positionY]
        self.feet.midbottom = self.rect.midbottom
        
        self.left.midleft = self.rect.midleft
        self.right.midright = self.rect.midright
        
    def debugDraw(self):
        pygame.draw.rect(screen,RED,self.rect)
                      
class Enemy(pygame.sprite.Sprite):
    def __init__(self,filename):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(filename).convert_alpha()
        
        self.velocityX = 0
        self.velocityY = 0
        self._positionX = 0
        self._positionY = 0

        self.rect = self.image.get_rect()
        self.feet = pygame.Rect(0,0, self.rect.width /2, 8)
        self.left = pygame.Rect(0,0,self.rect.width / 10,20)
        self.right = pygame.Rect(0,0,self.rect.width / 10,20)
        self.bIsPlayer = ObjectType.ENEMY
        self.flipRight = False
        self.flipLeft = True
        
        self.facing = 1
        self.bIsFiring = False
        self.velY = 0
        self.bCollided = False
        self.result = 0
        self.bIsWalking = True
        self.WalkAnimIndex = 0
        
        self.lastUpdate = 0
        self.bIsDead = False
        self.DeathAnimIndex = 0
        self.deathAnimDelay = 50
        self.bDeathAnimCompleted = False
        self.ChangeDirTimer = 70
        self.FireUpdate = 0
        
    def updateDir(self):
        if pygame.time.get_ticks() - self.lastUpdate > self.ChangeDirTimer:
            if self.facing <= 0:
                self.facing = 1
            elif  self.facing > 0:
                self.facing = -1
                
            self.lastUpdate = pygame.time.get_ticks()
                
    def setVelocity(self):
        self.velocityX = self.facing
        self.velocityY = self.velY 

        
    def setAnim(self, filename):

        
        self.image = pygame.image.load(filename).convert_alpha()
        
        if self.facing == -1:
            self.image = pygame.transform.flip(self.image,True, False)
    
    
    def UpdateAnim(self,animDelay):
         
        if self.result <= 100 and self.result >= -100:
            pass
            #self.bIsWalking = False
        else:
            self.bIsWalking = True
            
            
        if self.bIsDead == False:    
            if self.bIsWalking == True:
                    self.setAnim(WalkAnimList[self.WalkAnimIndex])
                    if self.WalkAnimIndex < len(WalkAnimList)-1:
                        if pygame.time.get_ticks() - self.lastUpdate > animDelay:
                            self.WalkAnimIndex +=1
                            self.lastUpdate = pygame.time.get_ticks()
                      
                    
                    else:
                        self.WalkAnimIndex = 0
            else:
                 self.setAnim(IdleAnimList[0])
                 self.WalkAnimIndex = 0
                 
        else:
             self.PlayDeathAnim()

    def PlayDeathAnim(self):
        if self.bIsDead == True:
            self.setAnim(DeathAnimList[self.DeathAnimIndex])
            if self.DeathAnimIndex < len(DeathAnimList)-1:
                if pygame.time.get_ticks() - self.lastUpdate > self.deathAnimDelay:
                    self.DeathAnimIndex +=1
                    self.lastUpdate = pygame.time.get_ticks()
            else:
                self.bDeathAnimCompleted = True 
                
  
    def UpdatePosition(self):
        #self.image = pygame.transform.scale(self.image,[70,70])

        self._positionX += self.velocityX
        self._positionY += self.velocityY
            
        self.rect.topleft = [self._positionX,self._positionY]
        self.feet.midbottom = self.rect.midbottom
        
        self.left.midleft = self.rect.midleft
        self.right.midright = self.rect.midright

        
    def AIRotate(self):
         if self.result > 0:
             self.facing = 1
             if self.flipRight == True: 
                 self.image = pygame.transform.flip(self.image,True, False)
                 self.flipRight = False
                 self.flipLeft = True
         elif self.result < 0:
             self.facing = -1
             if self.flipLeft == True:
                 self.image = pygame.transform.flip(self.image,True, False) 
                 self.flipLeft = False
                 self.flipRight = True
                 
                 
    def debugDraw(self):
        pygame.draw.rect(screen,RED,self.rect)

class Character(pygame.sprite.Sprite):
    def __init__(self,filename):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(filename).convert_alpha()
        #self.image = pygame.transform.scale(self.image,[2,2])
        self.velocityX = 0
        self.velocityY = 0
        self._positionX = 0
        self._positionY = 0
        
        self.rect = self.image.get_rect()
        self.feet = pygame.Rect(0,0, self.rect.width /20, 8)
        self.left = pygame.Rect(0,0,self.rect.width / 10,20)
        self.right = pygame.Rect(0,0,self.rect.width / 10,20)
        self.bIsPlayer = ObjectType.PLAYER
        self.flipRight = False
        self.flipLeft = True
        self.bIsShooting = False
        self.ShootAnimDelay = 50
        self.PlayerShootAnimIndex = 0
        self.lastUpdate = 0
        self.bPlayShootingAnim = False
        self.bPlayerCrouching = False
   
    def setVelocity(self, velX, velY):
        if self.bPlayerCrouching == False:
            self.velocityX = velX
        else:
            self.velocityX = 0
        self.velocityY = velY
        
    def setAnim(self, filename,currentAnim):
        
        self.image = pygame.image.load(filename).convert_alpha()
        
        if currentAnim == CurrentAnim.LEFT:
            self.image = pygame.transform.flip(self.image,True, False)
       # self.rect = self.image.get_rect()
         
    def PlayShootAnim(self,currentAnim):
        
        if self.bPlayShootingAnim == True:
            self.setAnim(PlayerShootAnimList[self.PlayerShootAnimIndex],currentAnim)
            if self.PlayerShootAnimIndex < len(PlayerShootAnimList)-1:
                if pygame.time.get_ticks() - self.lastUpdate > self.ShootAnimDelay:
                    self.PlayerShootAnimIndex +=1
                    self.lastUpdate = pygame.time.get_ticks()
            else:
                self.PlayerShootAnimIndex =0
                self.bPlayShootingAnim = False
               # self.bShootCompleted = True 
  
    def UpdatePosition(self):
        
        #self.image = pygame.transform.scale(self.image,[70,70])
        self._positionX += self.velocityX
        self._positionY += self.velocityY
            
        self.rect.topleft = [self._positionX,self._positionY]
        self.feet.midbottom = [self.rect.midbottom[0],self.rect.midbottom[1]-15]
        
        self.left.midleft = [self.rect.midleft[0] + 25,self.rect.midleft[1]]
        self.right.midright = [self.rect.midright[0] - 25,self.rect.midright[1]]

class Elevator(pygame.sprite.Sprite):
    def __init__(self,filename,posX,posY):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(filename).convert_alpha()
        self.image = pygame.transform.scale(self.image,[70,80])
        self._positionX = posX
        self._positionY = posY
        self.startPosY = self._positionY
        self.velocityY = 0
        self.rect = self.image.get_rect()
        self.feet = pygame.Rect(0,0, self.rect.width, 8)
        self.left = pygame.Rect(0,0,self.rect.width / 10,20)
        self.right = pygame.Rect(0,0,self.rect.width / 10,20)
        self.bIsPlayer = ObjectType.ELEVATOR
        self.CollideWithElavator = False
        
 
            
        self.Dir = ElevatorDir.DOWN
    def setVelocity(self):
        self.velocityY = 1
            
    def UpdatePosition(self):
        
       if self._positionY == self.startPosY - 100:
            self.Dir = ElevatorDir.DOWN
       elif  self._positionY == self.startPosY + 250:
           self.Dir = ElevatorDir.UP
           
       if self.Dir == ElevatorDir.DOWN:
           self._positionY += self.velocityY
       else:
           self._positionY -= self.velocityY
           
       self.rect.topleft = [self._positionX,self._positionY]
       self.feet.midbottom = self.rect.midbottom
        
       self.left.midleft = self.rect.midleft
       self.right.midright = self.rect.midright
             
#---IDLE ANIMATIONS---
  
IdleAnimList = []
IdleAnimList.append("Gun/idle/idle01.png")    
#---WALK ANIMATIONS---
WalkAnimList = []
WalkAnimList.append("Gun/Running/run1.png")
WalkAnimList.append("Gun/Running/run2.png")
WalkAnimList.append("Gun/Running/run3.png")
WalkAnimList.append("Gun/Running/run4.png")
WalkAnimList.append("Gun/Running/run5.png")
WalkAnimList.append("Gun/Running/run6.png")
WalkAnimList.append("Gun/Running/run7.png")
WalkAnimList.append("Gun/Running/run8.png")

PlayerWalkAnimList = []
PlayerWalkAnimList.append("Detective/Run/Run_01.png")
PlayerWalkAnimList.append("Detective/Run/Run_02.png")
PlayerWalkAnimList.append("Detective/Run/Run_03.png")
PlayerWalkAnimList.append("Detective/Run/Run_04.png")
PlayerWalkAnimList.append("Detective/Run/Run_05.png")
PlayerWalkAnimList.append("Detective/Run/Run_06.png")
PlayerWalkAnimList.append("Detective/Run/Run_07.png")
PlayerWalkAnimList.append("Detective/Run/Run_08.png")

PlayerShootAnimList = []
PlayerShootAnimList.append("Detective/Shoot/Shoot_01.png")
PlayerShootAnimList.append("Detective/Shoot/Shoot_02.png")
PlayerShootAnimList.append("Detective/Shoot/Shoot_03.png")
PlayerShootAnimList.append("Detective/Shoot/Shoot_04.png")
PlayerShootAnimList.append("Detective/Shoot/Shoot_05.png")

PlayerIdleAnimList = []
PlayerIdleAnimList.append("Detective/Idle/Idle_01.png")

playerCrouchAnimList = []
playerCrouchAnimList.append("Detective/Crouch/Crouch_01.png")
playerCrouchAnimList.append("Detective/Crouch/Crouch_02.png")
playerCrouchAnimList.append("Detective/Crouch/Crouch_03.png")
playerCrouchAnimList.append("Detective/Crouch/Crouch_04.png")
playerCrouchAnimList.append("Detective/Crouch/Crouch_05.png")
playerCrouchAnimList.append("Detective/Crouch/Crouch_06.png")

#--Jump ANIMATIONS--
JumpAnimList = []
JumpAnimList.append("Adventurer-1.5/Individual Sprites/adventurer-crnr-jmp-00.png");
JumpAnimList.append("Adventurer-1.5/Individual Sprites/adventurer-crnr-jmp-01.png");

DeathAnimList = []
DeathAnimList.append("Gun/dead/dead01.png")
DeathAnimList.append("Gun/dead/dead02.png")
DeathAnimList.append("Gun/dead/dead03.png")
DeathAnimList.append("Gun/dead/dead04.png")
DeathAnimList.append("Gun/dead/dead05.png")
DeathAnimList.append("Gun/dead/dead06.png")
DeathAnimList.append("Gun/dead/dead07.png")
DeathAnimList.append("Gun/dead/dead08.png")
DeathAnimList.append("Gun/dead/dead09.png")
DeathAnimList.append("Gun/dead/dead10.png")
DeathAnimList.append("Gun/dead/dead11.png")

BulletImage = ("photos/bullet.png") 

ElevatorImage = ("Elevator.png")

BulletsPlayer = []
BulletsEnemy = []
Enemies = []
elevator = []
doors = []

class Game(object):
        
      filename = get_map(MAP_FILENAME)
              
      def __init__(self):
        
        # true while running
        self.currentAnim = CurrentAnim.RIGHT 
        # load data from pytmx
        tmx_data = load_pygame(self.filename)
        # setup level geometry with simple pygame rects, loaded from pytmx
        self.walls = list()

        for object in tmx_data.objects:
            self.walls.append(pygame.Rect(
                object.x, object.y,
                object.width, object.height))
            

        # create new data source for pyscroll
        map_data = pyscroll.data.TiledMapData(tmx_data)
        # create new renderer (camera)
        self.map_layer = pyscroll.BufferedRenderer(map_data, screen.get_size(), clamp_camera=False, tall_sprites=0)
        self.map_layer.zoom =1.8
        
        # pyscroll supports layered rendering.  our map has 3 'under' layers
        # layers begin with 0, so the layers are 0, 1, and 2.
        # since we want the sprite to be on top of layer 1, we set the default
        # layer for sprites as 2
        self.group = PyscrollGroup(map_layer=self.map_layer, default_layer=1) 
        
        self.doorPosX = 157
        self.doorPosY = 208
        self.offset = 0
        
        for j in range(2):
                for i in range(39):
                    doors.append(Door(self.doorPosX,self.doorPosY))  
                    self.doorPosY +=113 - self.offset
                    self.offset += 0.06
                
                self.doorPosX = 270 
                self.offset = 0
                self.doorPosY = 208
                
                
        self.doorPosX = 457  
        self.doorPosY = 208
        self.offset = 0
        for j in range(2):
                for i in range(39):
                    doors.append(Door(self.doorPosX,self.doorPosY))  
                    self.doorPosY +=113 - self.offset
                    self.offset += 0.06
                
                self.doorPosX = 588 
                self.offset = 0
                self.doorPosY = 208
    
            
        
        self.elevatorInitX = 350
        self.elevatorInitY = 200


     
        for i in range(20):
            elevator.append(Elevator(ElevatorImage,self.elevatorInitX,self.elevatorInitY))
            self.elevatorInitY += 250
        
        for i in elevator:
            self.group.add(i)
      
                
   
        self.playerCharacter = Character(PlayerWalkAnimList[0])
        #self.playerCharacter._position = self.map_layer.map_rect.center
        self.playerCharacter._positionX += 300
        self.playerCharacter._positionY += 20
        
 

        self.group.add(self.playerCharacter)
            
          #Variables
        self.animDelay = 50
        self.JumpTimer = 1700
        self.FireDelay = 2000
        self.lastUpdate = 0
        self.SpawnlastUpdate = 0
        self.JumplastUpdate = 0
        self.AttacklastUpdate = 0
        
        self.ScoreIncreaseTimer = 0
        
        self.playerVel = [0, 0]
        self.velX = 0
        self.velY = 0
        self.jumpVel = 0.5
      

        self.Gravity = 0
        self.bIsJumping = False
        self.bCanJump = True
        self.WalkAnimIndex = 0
        self.CrouchAnimIndex = 0
        self.AttackAnimIndex = 0
        self.bIsWalking = False
        self.bCollided = False
        self.bCanMoveRight = True
        self.bCanMoveLeft = True
        
        self.bIsFiring = False
        self.bHasFired = False
        self.bCanFire = True
       
        
    
        self.bAddEnemy = False
        self.facing = 1
        self.PlayeBulletOffset = 0

       
        self.bCanSpawnEnemy = True
        
        self.WalkSoundTimer = 0

        pygame.display.set_caption("Elevator action")

        self.clock = pygame.time.Clock()
        
        self.score = 0
        self.health = 10
        self.bHealthCheck = True
        self.bGameOver = False
        self.bLevelPassed = False
        
               
      def MovementHandle(self):
            
            
            self.keys = pygame.key.get_pressed()
            
            if self.keys[pygame.K_LEFT]:
                self.bIsWalking = True
                self.currentAnim = CurrentAnim.LEFT 
                
            
            elif self.keys[pygame.K_RIGHT]:
                self.bIsWalking = True
                self.currentAnim = CurrentAnim.RIGHT 
                    
            if self.bIsWalking == True:
               
                if self.currentAnim == CurrentAnim.LEFT:
                       if self.bCanMoveLeft == True:
                           self.velX = -2.5      
                           
                elif self.currentAnim == CurrentAnim.RIGHT:
                       if self.bCanMoveRight == True:
                           self.velX = 2.5 
                           
  

      def AddEnemy_thread(self):
            count = 0
            if count < 1 and len(Enemies) < 50:
      
                for i in doors:
                    if self.playerCharacter._positionY >= i.positionY - random.randrange(20,200) and self.playerCharacter._positionY <= i.positionY + random.randrange(20,200) and  self.playerCharacter._positionX >= i.positionX - random.randrange(20,200) and self.playerCharacter._positionX <= i.positionX + random.randrange(20,200) :
                            enemy = Enemy(WalkAnimList[0])
                            enemy._positionX = i.positionX
                            enemy._positionY = i.positionY
                            Enemies.append(enemy)
                            self.group.add(enemy)
                            count +=1
                            self.bCanSpawnEnemy = False
                            if count >=2:
                                count =0
              
      def Bullet_thread_player(self):
          if self.currentAnim == CurrentAnim.LEFT:
              self.facing = -1
              self.PlayeBulletOffset = -10
          elif self.currentAnim == CurrentAnim.RIGHT:
              self.facing = 1
              self.PlayeBulletOffset = 10
          BulletsPlayer.append(Bullet(BulletImage,self.playerCharacter._positionX + self.PlayeBulletOffset,self.playerCharacter._positionY+20,self.facing))
          self.group.add(BulletsPlayer[len(BulletsPlayer)-1])
          
          
      def Bullet_thread_enemy(self):
          for i in Enemies:
              BulletsEnemy.append(Bullet(BulletImage,i._positionX,i._positionY+5,i.facing))
              self.group.add(BulletsEnemy[len(BulletsEnemy)-1])
                
                
      def run(self,done):
          
            for event in pygame.event.get():

                    if event.type == pygame.QUIT:
                        pygame.quit()
                        
                     
            
            if self.bIsWalking == True:
                if pygame.time.get_ticks() - self.WalkSoundTimer > 500:
                    runSound.play(0)
                    self.WalkSoundTimer = pygame.time.get_ticks()
            
            self.keys = pygame.key.get_pressed()
            
            if self.keys[pygame.K_SPACE]:
                if self.bCanJump == True:
                    jumpSound.play(0)
                    self.bIsJumping = True
                    self.bCanJump = False
            
            
            if self.keys[pygame.K_z]:
                if self.bCanFire == True:
                    self.bIsFiring = True
                    self.bHasFired = True
                    self.bCanFire = False
                    pistolFire()
                else:
                    self.bIsFiring = False
            else:
                self.bIsFiring = False
                self.bCanFire = True
                
                
                
            if self.bIsWalking == False:
                self.playerCharacter.setAnim(PlayerIdleAnimList[0], self.currentAnim)
            
            if self.keys[pygame.K_x]:
                pass
                
                                    
            if self.keys[pygame.K_q]:
                pass


            
            if self.keys[pygame.K_e]:
                if self.bAddEnemy == False:
                    self.bAddEnemy = True
    
                
            else:
                self.bIsWalking = False
                
                                
            if self.keys[pygame.K_DOWN]:
                self.playerCharacter.bPlayerCrouching = True
            else:
                self.playerCharacter.bPlayerCrouching = False
                
            
         
            if self.bIsWalking == False:
                self.velX = 0
                
            if self.bIsJumping == True:
                self.bIsInAir = True
                self.bCollided = False
                if self.jumpVel > 0:
                    self.velY -=self.jumpVel
                    self.jumpVel -= 0.03
                else:
                    self.jumpVel = 0.5
                    self.velY = 0
                    
                    self.bIsJumping = False
                    
            
            self.MovementHandle()
                    
            for sprite in self.group.sprites():
                
                if sprite.bIsPlayer == ObjectType.PLAYER:
                    

                            
                    for i in elevator:    
                        if sprite.feet.collidelist(self.walls) > -1 or i.CollideWithElavator == True:

                            
                            self.bCollided = True
                        
                            if self.bIsJumping == False:
                                self.velY = 0
                                if self.bCanJump == False:
                                    if self.bCollided == True:
                                        self.bCanJump = True         
                   
                        else:
                            self.bCollided = False
                        
                elif sprite.bIsPlayer == ObjectType.ENEMY:
                     if sprite.feet.collidelist(self.walls) > -1 and i.CollideWithElavator == False:
                         sprite.bCollided = True
                     else:
                         sprite.bCollided = False
            
            for i in elevator:            
                if i.CollideWithElavator == False:
                        if self.bCollided == False:    
                            self.velY += 0.1/len(elevator)
                        
                else:
                    if i.Dir == ElevatorDir.DOWN:
                        if self.bIsJumping == False:
                            self.velY += 1.0/len(elevator)+0.82
                    else:
                        self.velY -= 1.0 * 1.1
               
            for i in Enemies:  
                if i.bCollided == False:
                    i.velY +=0.1
                else:
                    i.velY = 0.0
                       
            
                i.setVelocity()
                i.result = self.playerCharacter._positionX - i._positionX
                
                i.updateDir()
                #print(i.result)
                if i.result <= 100 and i.result >= -100 and i._positionY >= self.playerCharacter._positionY - 20 and i._positionY <= self.playerCharacter._positionY + 20:
                    i.AIRotate()
                    i.velocityX = 0

                if i.bIsFiring == True and i.result <= 600 and i.result >= -600 and i._positionY >= self.playerCharacter._positionY - 20 and i._positionY <= self.playerCharacter._positionY + 20:
                    thread = threading.Thread(target=self.Bullet_thread_enemy)
                    enemyGun.play(0)
                    thread.start()
                    i.bIsFiring = False
                
                if i.bIsFiring == False:
                    if pygame.time.get_ticks() - i.FireUpdate > self.FireDelay*random.randrange(2,8):
                        i.bIsFiring = True
                        i.FireUpdate = pygame.time.get_ticks()
                    
                i.UpdatePosition()
                
                if i.bIsDead == False:
                    if i.velocityX != 0:
                        i.UpdateAnim(self.animDelay)
                    else:
                        i.setAnim(IdleAnimList[0])
                else:
                    i.UpdateAnim(self.animDelay)
                    
            if self.playerCharacter.right.collidelist(self.walls) > -1:
                    
                    self.bCanMoveRight = False
            else:
                    self.bCanMoveRight = True
                       
            if self.playerCharacter.left.collidelist(self.walls) > -1:
                    self.bCanMoveLeft = False
            else:
                    self.bCanMoveLeft = True
                    
                    
            for i in Enemies:
                if i.left.collidelist(self.walls) > -1:
                    i.velocityX = 0
                    i.facing = 1
                elif i.right.collidelist(self.walls) > -1:
                    i.velocityX = 0
                    i.facing = -1                     

            if self.bIsFiring == True:
                self.playerCharacter.bPlayShootingAnim = True
                    
            if self.playerCharacter.bPlayShootingAnim == False:
                
                if self.playerCharacter.bPlayerCrouching == False:

                    if self.bIsWalking == True :
                
                        self.playerCharacter.setAnim(PlayerWalkAnimList[self.WalkAnimIndex],self.currentAnim)
                        if self.WalkAnimIndex < len(PlayerWalkAnimList)-1:
                            if pygame.time.get_ticks() - self.lastUpdate > self.animDelay:
                                self.WalkAnimIndex +=1
                                self.lastUpdate = pygame.time.get_ticks()
                        else:
                            self.WalkAnimIndex = 0

            
                    else:
                        self.WalkAnimIndex = 0
                else:
                     self.playerCharacter.setAnim(playerCrouchAnimList[self.CrouchAnimIndex],self.currentAnim)
                     if self.CrouchAnimIndex < len(playerCrouchAnimList)-1:
                         if pygame.time.get_ticks() - self.lastUpdate > self.animDelay:
                             self.CrouchAnimIndex +=1
                             self.lastUpdate = pygame.time.get_ticks()
                             
                     else:
                            self.CrouchAnimIndex = len(playerCrouchAnimList)-1
                     
                    
            else:
                self.playerCharacter.PlayShootAnim(self.currentAnim)     
                
            self.playerCharacter.setVelocity(self.velX, self.velY)
           
                
            if self.bCanSpawnEnemy == True:   
                threadAddEnemy = threading.Thread(target=self.AddEnemy_thread)
                threadAddEnemy.start()
           
                
            if self.bCanSpawnEnemy == False:
                if pygame.time.get_ticks() - self.SpawnlastUpdate > 8000:
                    self.SpawnlastUpdate = pygame.time.get_ticks()
                    self.bCanSpawnEnemy = True
                    
                    
                
            self.group.center(self.playerCharacter.rect.center)      
            self.playerCharacter.UpdatePosition()
            
  
            #print(self.bCanSpawnEnemy)
            
            
            if self.bIsFiring == True:
                thread = threading.Thread(target=self.Bullet_thread_player)
                thread.start()
                
            
            if BulletsPlayer:    
                for i in BulletsPlayer:
                    i.UpdatePosition()
                    
                    #print("[ "+str(i.positionX)+", "+str(i.positionY)+" ]")
                    if i.positionX > W or i.positionX < 0:
                        self.group.remove(i)
                        BulletsPlayer.pop(BulletsPlayer.index(i))
                        
            if len(BulletsPlayer) > 20:
                for i in BulletsPlayer:
                    BulletsPlayer.pop(BulletsPlayer.index(i))
                    
                    
   
            if BulletsEnemy:    
                for i in BulletsEnemy:
                    i.UpdatePosition()
                    
                    if i.positionX > W or i.positionX < 0:
                        self.group.remove(i)

                        BulletsEnemy.pop(BulletsEnemy.index(i))
                        
            
            for i in elevator:
                
                 if self.playerCharacter.rect[1] >= i.rect[1] - 20 and self.playerCharacter.rect[1] <= i.rect[1] + 20 and self.playerCharacter.rect[0] >= i.rect[0] - 50 and self.playerCharacter.rect[0] <= i.rect[0] + 50:
                     i.CollideWithElavator = True
                 else:
                     i.CollideWithElavator = False
                 i.setVelocity()
                 i.UpdatePosition()
                 
                 
            for i in Enemies:
                if i._positionY >= self.playerCharacter._positionY + 200 or i._positionY <= self.playerCharacter._positionY - 200:
                    self.group.remove(i)
                    Enemies.pop(Enemies.index(i))
                if i.velocityY > 20:
                    self.group.remove(i)
                    Enemies.pop(Enemies.index(i))
                if i.bDeathAnimCompleted == True:
                    self.group.remove(i)
                    Enemies.pop(Enemies.index(i))
                    
            
            for i in BulletsPlayer:
                if i.rect.collidelist(self.walls) > -1:
                     self.group.remove(i)
                     BulletsPlayer.pop(BulletsPlayer.index(i))
            
            
            for i in BulletsEnemy:
                if i.rect.collidelist(self.walls) > -1 :
                     self.group.remove(i)
                     BulletsEnemy.pop(BulletsEnemy.index(i))
                
            for i in BulletsPlayer:
                for j in Enemies:
                    if (i.rect[1] <= j.rect[1]+20 and i.rect[1] >= j.rect[1]-20) and ( i.rect[0] <= j.rect[0] + 5 and i.rect[0] >= j.rect[0] - 5) :
                        j.bIsDead = True
                        if pygame.time.get_ticks() - self.ScoreIncreaseTimer > 1000:
                            self.score +=50
                            self.ScoreIncreaseTimer = pygame.time.get_ticks()
                        
                        self.bHealthCheck = True
                        hitmarkSound.play(0)
                        
                        self.group.remove(i)
                        
                        try:
                            BulletsPlayer.pop(BulletsPlayer.index(i))
                        except:
                            continue
                        
            for i in BulletsEnemy:
                if self.playerCharacter.bPlayerCrouching == False and self.bIsJumping == False:
                    if (i.rect[1] <= self.playerCharacter.rect[1]+20 and i.rect[1] >= self.playerCharacter.rect[1]-20) and ( i.rect[0] <= self.playerCharacter.rect[0] + 5 and i.rect[0] >= self.playerCharacter.rect[0] - 5):
                        #print("PLAYER HIT")
                        self.playerCharacter._positionY -=4
                        print(i.facing)
                        if i.facing < 0:
                            self.playerCharacter._positionX -=5
                            
                        elif i.facing > 0:
                            self.playerCharacter._positionX +=5
                        self.health -=1
                        self.score -= 75
                        damageTakenSound.play(0)
                        self.group.remove(i)
                        BulletsEnemy.pop(BulletsEnemy.index(i))
                        
            if self.score == 250 and self.bHealthCheck == True:
               self.health += 1
               hpGain.play(0)
               self.bHealthCheck = False
            if self.score == 500 and self.bHealthCheck == True:
               self.health += 1
               hpGain.play(0)
               self.bHealthCheck = False
            if self.score == 750 and self.bHealthCheck == True:
               self.health += 1
               hpGain.play(0)
               self.bHealthCheck = False
            if self.score == 1000 and self.bHealthCheck == True:
               self.health += 1
               hpGain.play(0)
               self.bHealthCheck = False
            if self.score == 1500 and self.bHealthCheck == True:
               self.health += 1
               hpGain.play(0)
               self.bHealthCheck = False
            if self.score == 2000 and self.bHealthCheck == True:
               self.health += 2
               hpGain.play(0)
               self.bHealthCheck = False
            if self.score == 3000 and self.bHealthCheck == True:
               self.health += 3
               hpGain.play(0)
               self.bHealthCheck = False
            if self.score == 4000 and self.bHealthCheck == True:
               self.health += 3
               hpGain.play(0)
               self.bHealthCheck = False
            if self.score == 5000 and self.bHealthCheck == True:
               self.health += 3
               hpGain.play(0)
               self.bHealthCheck = False
            if self.score == 10000 and self.bHealthCheck == True:
               self.health += 5
               hpGain.play(0)
               self.bHealthCheck = False

            if self.playerCharacter._positionX >= 687 - 40 and self.playerCharacter._positionX <= 687 + 40 and self.playerCharacter._positionY >= 4657 - 40 and self.playerCharacter._positionY <= 4657 + 40:
                self.bLevelPassed = True
            if self.health<=0:
                self.bGameOver = True
                
            print(str(self.playerCharacter._positionX) + ", "+str(self.playerCharacter._positionY))    
                
            self.group.draw(screen)
            draw_score(screen, 30, 30, self.score)
            draw_health(screen,1120,30,self.health)
            pygame.display.flip()

            self.clock.tick(60)
     
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1)

done = False
game = Game()

start = False
while not done:
    pygame.display.update()
    
    print(len(elevator))
        
    if start == True:
        game.run(done)
    if start == False:
        pygame.display.set_caption('Elevator action')
        screen.fill((0,0,0))
        draw_text_middle('Press SPACE to begin.', 60, (255, 255, 255), screen)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                
    
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            start = True
            
            
    if game.bGameOver == True and game.bLevelPassed == False:
        screen.fill((0,0,0))
        start = False
        draw_text_middle('Game Over.Press R to restart or Q to quit', 40, (255, 255, 255), screen)
        draw_final_score('SCORE = '+str(game.score), 60, (255, 255, 255), screen)
        #pygame.display.update()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]:
            pygame.quit()
            done = True
            
        elif keys[pygame.K_r]:

            elevator.clear()
            Enemies.clear() 
            BulletsPlayer.clear() 
            doors.clear()
            BulletsEnemy.clear()
            game.group.clear(screen,screen)
            del game
            game = Game()
            start == True
            game.bGameOver = False
            
    elif game.bGameOver == False and game.bLevelPassed == True:
        
        screen.fill((0,0,0))
        start = False
        draw_text_middle('Level cleared! Press R to restart or Q to quit', 40, (255, 255, 255), screen)
        draw_final_score('SCORE = '+str(game.score), 60, (255, 255, 255), screen)
        #pygame.display.update()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]:
            pygame.quit()
            done = True
            
        elif keys[pygame.K_r]:

            elevator.clear()
            Enemies.clear() 
            BulletsPlayer.clear() 
            doors.clear()
            BulletsEnemy.clear()
            game.group.clear(screen,screen)
            del game
            game = Game()
            start == True
            game.bLevelPassed = False
 

pygame.quit()
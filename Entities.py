from typing import Any
import pygame as pg
import math , random, time
from PIL import Image
import Background as bg
from pygame_widgets.progressbar import ProgressBar

def rotate_surface(pygame_surface, angle):
    # Convert Pygame surface to PIL Image
    pil_image = Image.frombytes('RGBA', pygame_surface.get_size(), pygame_surface.get_buffer())

    # Rotate the PIL Image
    rotated_pil_image = pil_image.rotate(angle, expand=True, resample= Image.BICUBIC)

    # Convert back to Pygame surface
    rotated_pygame_surface = pg.image.fromstring(rotated_pil_image.tobytes(), rotated_pil_image.size, 'RGBA').convert_alpha()

    return rotated_pygame_surface
def Chance(Percentage):
    x = random.randint(1, 100)

    if x <= Percentage:
        return True
    else:
        return False
    
#Bullet Handling
bullets = pg.sprite.Group()

#Enemy Handling
enemies = pg.sprite.Group()
move_enemies = True
# Powers Handeling
powers = pg.sprite.Group()

# ProgressBar
progressbar_img = pg.image.load("Assets/progressbar.png")
progressbar_rect= progressbar_img.get_rect()
progressbar_rect.topright = (0,0)

# Misc
mobcap= 5
score = 0

class Enemy(pg.sprite.Sprite):
    def __init__(self, screen):
        super().__init__()
        self.screen = screen
        
        self.type = random.randint(1,5)
        self.image = pg.image.load(f"assets/enemies/enemy_{self.type}.png").convert_alpha()
        self.rect = self.image.get_rect()

        # Spawning
        side = random.randint(1,4)
        if side == 1:
            self.speed = 5
            self.rect.bottomleft = (random.randint(0,800),0)

        if side == 2:
            self.speed = 4
            self.rect.bottomleft = (800 ,random.randint(0,600))

        if side == 3:
            self.speed = 3
            self.rect.topleft = (random.randint(0,800),600)

        if side == 4:
            self.speed = 2
            self.rect.bottomright = (0,random.randint(0,600))

        self.position = pg.Vector2(self.rect.centerx,self.rect.centery)
        # Attributes

        if self.type == 1:
            self.speed = 5

        elif self.type == 2:
            self.speed = 4
        
        elif self.type == 3:
            self.speed = 3

        elif self.type == 4:
            self.speed = 2

        elif self.type == 5:
            self.speed = 1

        self.direction = pg.Vector2(0, 0)
        self.target_direction = pg.Vector2(0, 0)
        self.zigzag_timer = 0
        self.smoothness = 0.1



    def dynamic_rotation(self):
        # making the sprite rotate towards the mouse

        target = player_rect.center

        self.angle = round(math.degrees(math.atan2((target[1] - self.rect.y) , target[0] - self.rect.x)) +85) *-1
        self.R_Image = rotate_surface(self.image, self.angle).convert_alpha()
        self.mask = pg.mask.from_surface(self.R_Image)

    def draw(self):

        (x, y) = self.R_Image.get_size()
        (rx , ry) = self.rect.size

        (Rx , Ry) = self.rect.topleft

        x = (x-rx)/2
        y = (y-ry)/2
        
        self.screen.blit(self.R_Image, (Rx - x , Ry - y))

    def update(self):
        if move_enemies:
            self.Move()
        self.dynamic_rotation()

    def Move(self):
        if self.zigzag_timer <= 0:
            # Randomly change direction
            offset = pg.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
            direction = player_rect.center - self.position + offset
            self.target_direction = direction.normalize()
            self.zigzag_timer = random.randint(10, 30)  # Adjust as needed

        # Interpolate direction for smooth transition
        self.direction = self.direction.lerp(self.target_direction, self.smoothness)

        # Update position based on interpolated direction
        self.position += self.direction * self.speed
        self.rect.center = self.position
        self.zigzag_timer -= 1

class Bullets(pg.sprite.Sprite):
    def __init__(self, type):
        pg.sprite.Sprite.__init__(self)

        self.Point_A = player_rect.center
        self.Point_B = pg.mouse.get_pos()

        self.image = pg.image.load(f"Assets/Bullets/bullet{type}.png")
        self.image = pg.transform.scale(self.image, (16,16))
        self.rect = self.image.get_rect()
        self.rect.center = self.Point_A

        angle = round(math.degrees(math.atan2((self.Point_B[1] - self.rect.y) , self.Point_B[0] - self.rect.x)) +90) *-1
        self.R_Image = rotate_surface(self.image, angle).convert_alpha()
        self.mask = pg.mask.from_surface(self.R_Image)

        speed = 8

        self.dx = self.Point_B[0] - self.Point_A[0]
        self.dy = self.Point_B[1] - self.Point_A[1]

        distance = (self.dx**2 + self.dy**2)**0.5

        self.step_size = speed / distance

        # Use floating-point numbers to store the bullet's position and velocity
        self.x = float(self.rect.centerx)
        self.y = float(self.rect.centery)
        self.vx = self.dx * self.step_size
        self.vy = self.dy * self.step_size

    def update(self):
        # Update the bullet's position using floating-point numbers
        self.x += self.vx
        self.y += self.vy

        # Update the rect.center property to match the new position
        self.rect.center = (int(self.x), int(self.y))

        if self.rect.centerx > 850 or self.rect.centery > 650 or self.rect.centerx < -50 or self.rect.centery < -50:
            self.kill()

    def draw(self,screen):
        screen.blit(self.R_Image, self.rect)

class Player(pg.sprite.Sprite):
    def __init__(self, x, y, screen):

        pg.sprite.Sprite.__init__(self)
        self.image = pg.image.load('Assets/player.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.screen = screen

        self.health = 100
        self.max_health = 100
        self.x_vel = 0
        self.x_acc = 0
        self.y_vel = 0
        self.y_acc = 0
        self.Speedcap = 10

        self.speed = 1.0
        self.active_effects = []
        self.effects = [
            {'name': 'speedboost'   , 'timer': 5 * 60, 'run' : False},
            {'name': 'freeze'       , 'timer': 3 * 60, 'run' : False},
            {'name': 'shield'       , 'timer': 1 * 60, 'run' : False}
        ]
        self.sheilded = False

        self.L_Shoot = False
        self.L_Shoot_Flag = False

        self.R_Shoot = False
        self.R_Shoot_Flag = False

        self.R_time_last  = time.time()
        self.R_time       = None
        self.Reload       = 0.5 #Sec

        self.T_time_last  = time.time()
        self.T_time       = None
        self.Teleport     = 1.5 #Sec
        
        self.font = pg.font.SysFont("bahnschrift", 30)

        global player_rect
        player_rect = self.rect

    def draw(self):

        (x, y) = self.R_Image.get_size()
        (rx , ry) = self.rect.size

        (Rx , Ry) = self.rect.topleft

        x = (x-rx)/2
        y = (y-ry)/2
        
        self.screen.blit(self.R_Image, (Rx - x , Ry - y))

        global bar, reloadbar, teleportbar, health_text
        bar , health_text = self.healthbar()
        reloadbar = self.reloadbar()
        teleportbar = self.teleportbar()

    def movment(self):
        # Inputs

        key = pg.key.get_pressed()
        
        (L_click,M_click,R_click) = pg.mouse.get_pressed()

        # Reload Timer
        self.R_time = time.time() - self.R_time_last # in sec
        self.T_time = time.time() - self.T_time_last # in sec

        if L_click and not self.L_Shoot_Flag:
            self.L_Shoot_Flag = True
            self.shoot()
        
        if not L_click and self.L_Shoot_Flag:
            self.L_Shoot_Flag = False

        if R_click and not self.R_Shoot_Flag:
            self.R_Shoot_Flag = True
            self.teleport()
        
        if not R_click and self.R_Shoot_Flag:
            self.R_Shoot_Flag = False

        if (key[pg.K_LEFT] or key[pg.K_a]) and self.rect.x > 0:
            self.x_acc = -1 * self.speed
            self.x_vel += self.x_acc
            bg.scroll -= 1 * self.speed
        elif (key[pg.K_RIGHT] or key[pg.K_d]) and self.rect.x < 800:
            self.x_acc = 1 * self.speed
            self.x_vel += self.x_acc
            bg.scroll += 1 * self.speed
        else:
            self.x_acc = 0
            self.x_vel += self.x_acc

        if (key[pg.K_UP] or key[pg.K_w]) and self.rect.y > 0:
            self.y_acc = -1 * self.speed
            self.y_vel += self.y_acc
        elif (key[pg.K_DOWN] or key[pg.K_s]) and self.rect.y < 600:
            self.y_acc = 1 * self.speed
            self.y_vel += self.y_acc
        else:
            self.y_acc = 0
            self.y_vel += self.y_acc

        # Updating player's position
        self.rect.x += self.x_vel
        self.rect.y += self.y_vel

        self.x_vel = max(-self.Speedcap, min(self.x_vel, self.Speedcap))
        self.y_vel = max(-self.Speedcap, min(self.y_vel, self.Speedcap))
        
        # Friction

        if abs(self.x_vel) < 1:
            self.x_vel = 0
        else:
            self.x_vel *= 0.9

        if abs(self.y_vel) < 1:
            self.y_vel = 0
        else:
            self.y_vel *= 0.9

        self.x_vel = round(self.x_vel,2)
        self.y_vel = round(self.y_vel,2)

        global player_rect
        player_rect = self.rect

    def dynamic_rotation(self):
        # making the sprite rotate towards the mouse

        mouse_pos = pg.mouse.get_pos()

        self.angle = round(math.degrees(math.atan2((mouse_pos[1] - self.rect.y) , mouse_pos[0] - self.rect.x)) +90) *-1
        self.R_Image = rotate_surface(self.image, self.angle)
        self.mask = pg.mask.from_surface(self.R_Image)
        global player_mask
        player_mask = self.mask

    def shoot(self):
        # Shooting bullets
        if self.R_time >= self.Reload:
            bullets.add(Bullets(0))
            self.R_time_last = time.time()

    def healthbar(self):
        # Drawing healthbar
        Healthbar = ProgressBar(self.screen, 20, 530 , 200, 30, lambda: (self.health/self.max_health), curved= True)
        health_text = self.font.render("Health", True, (255,255,255))

        return Healthbar , health_text
    
    def reloadbar(self):
        # Drawing reloadbar
        Reloadbar = ProgressBar(self.screen, 20, 560 , 200, 5, lambda: self.R_time//self.Reload, curved= True, completedColour= (50,50,255))
        return Reloadbar
    
    def teleportbar(self):
        # Drawing reloadbar
        Reloadbar = ProgressBar(self.screen, 20, 565 , 200, 5, lambda: self.T_time//self.Teleport, curved= True, completedColour= (163,42,208))
        return Reloadbar

    def end(self):
        pass

    def teleport(self):
        if self.T_time >= self.Teleport:
            M_pos = pg.mouse.get_pos()
            self.rect.center = M_pos
            self.T_time_last = time.time()

            #Particles
            bg.Particles.add(bg.Particle("Teleport", M_pos))
    
    def update(self):

        self.movment()
        self.dynamic_rotation()
        # Checks for active effects
        for i in self.active_effects:
            match i:
                case "nuke":
                    self.nuke()
                case "freeze":
                    self.freeze()
                case "speedboost":
                    self.speedboost()
                case "shield":
                    self.shield()
                case "teleportation":
                    self.teleportation()
                case "multi_fire":
                    self.multi_fire()

    def use_power(self, power):
        match power:
            case "nuke":
                self.nuke()
            case "freeze":
                self.freeze()
            case "speedboost":
                self.speedboost()
            case "shield":
                self.shield()
            case "teleportation":
                self.teleportation()
            case "multi_fire":
                self.multi_fire()

    # Powers / Effects
    def heal(self):
        if self.health < self.max_health:
            self.health += 10

        if self.health > self.max_health:
            self.health = self.max_health

    def nuke(self):
        global score
        for i in enemies:
            bg.Particles.add(bg.Particle("Death", (i.rect.center)))
            if progressbar_rect.topleft != (0,0):
                    progressbar_rect.centerx += 8
            score += 1
            i.kill()

    def freeze(self):
        global move_enemies
        if not self.effects[2]['run']:
            self.effects[2]['run'] = True
            self.active_effects.append("freeze")

            move_enemies = False

        self.effects[2]['timer'] -= 1

        if self.effects[2]['timer'] <= 0:
            self.effects[2]['timer'] = 3*60
            self.effects[2]['run'] = False
            self.active_effects.remove("freeze")

            move_enemies = True

    def multi_fire(self):
        pass

    def shield(self):
        if not self.effects[2]['run']:
            self.effects[2]['run'] = True
            self.active_effects.append("shield")

            self.sheilded = True
            self.image = pg.image.load('Assets/Player_sheilded.png').convert_alpha()

        self.effects[2]['timer'] -= 1

        if self.effects[2]['timer'] <= 0:
            self.effects[2]['timer'] = 5*60
            self.effects[2]['run'] = False
            self.active_effects.remove("shield")

            self.sheilded = False
            self.image = pg.image.load('Assets/player.png').convert_alpha()

    def speedboost(self):
        if not self.effects[0]['run']:
            self.effects[0]['run'] = True
            self.active_effects.append("speedboost")

            self.speed = 1.75

        self.effects[0]['timer'] -= 1

        if self.effects[0]['timer'] <= 0:
            self.effects[0]['timer'] = 7*60
            self.effects[0]['run'] = False
            self.active_effects.remove("speedboost")

            self.speed = 1.0

    def teleportation(self):
        self.T_time = self.Teleport+10

class mouse(pg.sprite.Sprite):
    def __init__(self, file , screen):
        super().__init__()
        self.image = pg.image.load(f"Assets/{file}")
        self.image = pg.transform.scale(self.image, (20,20))
        self.rect = self.image.get_rect()
        self.rect.center = pg.mouse.get_pos()

        self.screen = screen

    def Draw(self):
        self.rect.center = pg.mouse.get_pos()
        self.screen.blit(self.image, self.rect)

class Powers(pg.sprite.Sprite):
    def __init__(self, player : Player, xy):
        super().__init__()

        self.sub = player
        x , y = xy
        powers = ['freeze', 'multi_fire', 'nuke', 'shield', 'teleportation', 'speedboost']
        self.type = random.choice(powers)
        self.image = pg.image.load(f"Assets/PowerUps/{self.type}.png")
        self.rect = self.image.get_rect()
        self.rect.center = (x , y)

        self.life = 60 * 3 # 3 means sec
    def update(self):
        self.life -= 1

        if self.life <= 0 :
            self.kill()

    def draw(self, screen : pg.surface.Surface):
        screen.blit(self.image, self.rect)
        
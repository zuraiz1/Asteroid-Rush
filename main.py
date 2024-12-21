import pygame , Background , Audio, time, Entities
from Entities import *
from sys import exit
import pygame_widgets as pygame_w
from pygame_widgets.textbox import TextBox
from pygame_widgets.slider import Slider
from pygame_widgets.button import ButtonArray

# Settings
WIDTH = 800
HEIGHT = 600
SpawnRate = 150
VOLUME = 0.15

global has_run_for_menu, has_run_for_game, has_run_for_options
has_run_for_menu = False
has_run_for_game = False
has_run_for_options = False

# Time Handling
global Last_time, New_time, dt
Last_time = None
dt = None

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Warrior")
clock = pygame.time.Clock()

# Music

# Making the player and Powers
player = Player(WIDTH/2, HEIGHT/2 , screen)

def Chance(Percentage):
    x = random.randint(1, 100)

    if x <= Percentage:
        return True
    else:
        return False
    
def spawn(Percentage):  # out of 10000
    x = random.randint(1, 10000)

    if x <= Percentage:
        return True
    else:
        return False

class Game_State():
    def __init__(self):
        self.state = "menu"

    def change_state(self, state):
        self.state = state

    def Game_State_Manager(self):
        if self.state == "game":
            self.game()
        elif self.state == "menu":
            self.menu()
        elif self.state == "options":
            self.options()

    def menu(self):
        global has_run_for_menu , buttonArray
        if not has_run_for_menu:
            has_run_for_menu = True
            # Creates an array of buttons
            buttonArray = ButtonArray(
                # Mandatory Parameters
                screen,  # Surface to place button array on
                50,  # X-coordinate
                HEIGHT/2 - 100,  # Y-coordinate
                200,  # Width
                200,  # Height
                (1, 3),  # Shape: 2 buttons wide, 2 buttons tall
                border=10,  # Distance between buttons and edge of array
                texts=('Play', 'Options', 'Quit'),  # Sets the texts of each button (counts left to right then top to bottom)
                # When clicked, print number
                onClicks=(lambda: self.change_state("game"), lambda: self.change_state("options"), lambda: exit()),
                # Optional
                separationThickness = 20,
                colour = (0,0,0)
            )
            pygame.mouse.set_visible(False)
            global Mouse
            Mouse = mouse("Menu_Mouse.png", screen)

            Audio.music.play("Menu_BG", VOLUME)

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                exit()
            
            # Navigation
            if event.type == pygame.KEYDOWN:
                if event.key == (pygame.K_w or pygame.K_UP):
                    pass

                if event.key == (pygame.K_s or pygame.K_DOWN):
                    pass

        # Rendering
        Background.draw_menu(screen)
        pygame_w.update(events)
        Mouse.Draw()
        pygame.display.update()

    def init_options(self):
        global slider, output
        slider = Slider(screen, 100, 100, 400, 20, min=0, max=99, step=1)
        output = TextBox(screen, 475, 200, 50, 50, fontSize=30)
        output.disable()
    
    def options(self):
        global has_run_for_options, buttonArray
        if not has_run_for_options:
            has_run_for_options = True

            buttonArray = None

            self.init_options()
            pygame.mouse.set_visible(False)
            global Mouse
            Mouse = mouse("Menu_Mouse.png", screen)
            Audio.music.play("Menu_BG", VOLUME)

        output.setText(slider.getValue())

        events = pygame.event.get()

        for ev in events:
            if ev.type == pygame.QUIT:
                exit()

        # Rendering
        screen.fill((9,1,22))

        pygame_w.update(events)
        Mouse.Draw()

        pygame.display.update()

    def game(self):

        # Making the cursor
        global has_run_for_game, buttonArray
        if not has_run_for_game:
            has_run_for_game = True
            Audio.music.play("Main_Track", VOLUME)
            global Mouse, Last_time

            pygame.mouse.set_visible(False)
            Mouse = mouse("mouse(ATK).png" , screen)

            Last_time = time.time()

            buttonArray = None

        global New_time, dt

        New_time = time.time()
        dt = New_time - Last_time
        Last_time = New_time
        
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()


        #game code
        player.update()
        global mobcap
        if spawn(SpawnRate) and len(enemies) < mobcap:
            enemies.add(Enemy(screen))

        # Collision Checks
        if pygame.sprite.spritecollide(player, enemies, True, pygame.sprite.collide_mask):
            if player.sheilded:
                player.effects[0]['timer'] = 0
            else:
                player.health -= 10

            if player.health <= 0:
                player.end()

        # Powers Collision Checks
        for x in powers:
            if pygame.sprite.collide_rect(x, player):
                player.use_power(x.type)
                x.kill()

        for i in enemies:
            if pygame.sprite.spritecollide(i, bullets, True, pygame.sprite.collide_mask):
                # Spawing powers
                if Chance(50):
                    powers.add(Powers(player, i.rect.center))

                Background.Particles.add(Background.Particle("Death", (i.rect.center)))

                global score
                score += 1
                if progressbar_rect.topleft != (0,0):
                    progressbar_rect.centerx += 8
                i.kill()
                
        enemies.update()
        bullets.update()
        powers.update()
        Background.Particles.update()

        # Rendering
        Background.draw_Background(screen)
        
        for enemy in enemies:
            enemy.draw()
        for bullet in bullets:
            bullet.draw(screen)

        Background.Particles.draw(screen)

        powers.draw(screen)
        player.draw()
        Mouse.Draw()
        pygame_w.update(events)
        screen.blit(Entities.health_text, (20, 530))
        screen.blit(progressbar_img, progressbar_rect)
        pygame.display.update()

Game = Game_State()
while True:
    Game.Game_State_Manager()

    clock.tick(60)
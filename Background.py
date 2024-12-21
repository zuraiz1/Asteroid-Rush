import pygame, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

pygame.init()
temp_Screen = pygame.display.set_mode((800,600))

global scroll

scroll = 0

def load(File):
    image = pygame.image.load(f"Assets/Background/{File}").convert_alpha()
    image = pygame.transform.smoothscale(image, (800,600))
    return image

base = load("Base.png")
stars1 = load("stars1.png")
stars2 = load("stars2.png")

menu_BG = load("Menu BackGround.jpeg")

Background_Img = [base, stars1, stars2]

def draw_Background(screen):

    for x in range(5):
        speed = 1
        for i in range(3):
            screen.blit(Background_Img[i], (((x * Background_Img[i].get_width()) - scroll * speed) - 1920,0))
            speed += 0.5

def draw_menu(screen):
    screen.blit(menu_BG, (0,0))

# Particles

def extract(sheet_name, Area : tuple) -> list:
    width, hight = Area
    sheet = pygame.image.load(f"Assets/Particles/{sheet_name}.png")

    frames = []

    for y in range(sheet.get_height()//hight):
        for x in range(sheet.get_width()//width):
            image = pygame.Surface((width, hight)).convert_alpha()
            image.blit(sheet, (0, 0), (x * width, y *hight, width, hight))
            image.set_colorkey((0,0,0))
            frames.append(image)
        
    return frames

"Add any needed frames list here"
Teleportation_frames = extract("teleport", (96,80))
Death_frames = extract("Death", (133,132))

# Particles

Particles = pygame.sprite.Group()

class Particle(pygame.sprite.Sprite):
    def __init__(self,name ,Coordinnates):
        super().__init__()
        self.x = Coordinnates[0]
        self.y = Coordinnates[1]

        self.counter = 0
        self.state = 0

        match name:
            case "Teleport":
                self.frames = Teleportation_frames
            case "Death":
                self.frames = Death_frames

        self.image = self.frames[self.state]
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

    def update(self):
        self.counter += 1
        if self.counter >= 2:
            self.counter = 0
            self.state += 1
            if self.state >= len(self.frames):
                self.kill()
            else:
                self.image = self.frames[self.state]
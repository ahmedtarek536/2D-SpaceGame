import pygame
import random
from random import uniform


# general setup
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280,720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Space shooter")
running = True
clock = pygame.time.Clock()

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load("images/player.png").convert_alpha()
        self.rect = self.image.get_rect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.direction = pygame.math.Vector2(1,2)
        self.speed = 300

        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 400

        self.mask = pygame.mask.from_surface(self.image)
        # mask_surf = mask.to_surface()
        # self.image = mask_surf

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True
    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = (int(keys[pygame.K_RIGHT])) - (int(keys[pygame.K_LEFT]))
        self.direction.y = (int(keys[pygame.K_DOWN])) - (int(keys[pygame.K_UP]))
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt

        if keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf, self.rect.midtop, (all_sprites , laser_sprites))
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()
        self.laser_timer()

class Star(pygame.sprite.Sprite):
    def __init__(self, groups , surface):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(center = (random.randint(0 , WINDOW_WIDTH) , random.randint(0, WINDOW_HEIGHT))) 

class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(midbottom = pos)
        self.mask = pygame.mask.from_surface(self.image)
    def update(self, dt):
        self.rect.centery -= 400 * dt
        if self.rect.bottom < 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.origins = self.image
        self.rect =self.image.get_rect(center = (random.randint(0, WINDOW_WIDTH) , -2))
        self.mask = pygame.mask.from_surface(self.image)
        self.start_time = pygame.time.get_ticks()
        self.lifetime =3000
        self.direction = pygame.Vector2(uniform(-0.5,0.5), 1)
        self.speed = random.randint(400,500)
        self.rotation = 0
        self.rotation_speed = random.randint(40,80) 
    def update(self , dt):
        self.rect.center += self.direction * self.speed * dt
        if self.rect.bottom > WINDOW_HEIGHT:
            self.kill()
        if pygame.time.get_ticks() - self.start_time >= self.lifetime: 
            self.kill()
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.origins, self.rotation,1)
        self.rect = self.image.get_rect(center = self.rect.center)

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos , groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center = pos)
    def update(self, dt):
        self.frame_index += 80 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index) % len(self.frames)] 
        else:
            self.kill()


def display_score():
    current_time = pygame.time.get_ticks() 
    text_surf = font.render(str(current_time) ,True, (240,240,240))
    text_rect = text_surf.get_rect(midbottom = (WINDOW_WIDTH/2, WINDOW_HEIGHT-50))
    display_surface.blit(text_surf, text_rect)
    pygame.draw.rect(display_surface, "red" , text_rect.inflate(20,20).move(0,0), 5 ,10 )


# import
star_surf = pygame.image.load("images/star.png").convert_alpha()
meteor_surf = pygame.image.load("images/meteor.png").convert_alpha()
laser_surf = pygame.image.load("images/laser.png").convert_alpha()
font = pygame.font.Font("images/Oxanium-Bold.ttf", 30)
explosion_frames = [(pygame.image.load(f"images/explosion/{i}.png").convert_alpha() )for i in range(21)]

laser_sound = pygame.mixer.Sound("audio/laser.wav")
laser_sound.set_volume(0.5)
explosion_sound = pygame.mixer.Sound("audio/explosion.wav")
damage_sound = pygame.mixer.Sound("audio/damage.ogg")
game_music = pygame.mixer.Sound("audio/game_music.wav")
game_music.set_volume(0.3)
game_music.play()
game_music.play(loops = -1)



all_sprites = pygame.sprite.Group()
meteor_sprites =  pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
for i in range(20):
    Star(all_sprites ,star_surf)

player = Player(all_sprites)




# customer events -> meteor event
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 500)


def collisions(): 
    global running
    collision_sprites_player = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask)
    if collision_sprites_player:
        running = False

    for laser in laser_sprites:
        collision_sprites = pygame.sprite.spritecollide(laser,meteor_sprites, True)
        if collision_sprites: 
            laser.kill()
            AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprites)
            explosion_sound.play()
            


while running:
    dt = clock.tick() / 1000
    # event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event:
            Meteor(meteor_surf,(all_sprites, meteor_sprites))
    all_sprites.update(dt)
    collisions()

    # draw the game
    display_surface.fill('#3a2e3f')
    display_score()
    all_sprites.draw(display_surface)

    
  
    pygame.display.update()
pygame.quit()







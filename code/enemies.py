from settings import *
from random import choice
from timer import Timer

class Tooth(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, collision_sprites):
        super().__init__(groups)
        self.frames, self.frame_index = frames, 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(topleft = pos)
        self.z = Z_LAYERS['main']

        self.direction = choice((-1,1))
        self.collision_rects = [sprite.rect for sprite in collision_sprites]
        self.speed = 200

        self.hit_timer = Timer(250)

    def reverse(self):
        if not self.hit_timer.active:
            self.direction *= -1
            self.hit_timer.activate()
    
    def update(self, dt):
        self.hit_timer.update()
        # animate
        self.frame_index += ANIMATION_SPEED * dt
        self.image = self.frames[int(self.frame_index % len(self.frames))]
        if self.direction < 0:  # We are moving left so flip image
            self.image = pygame.transform.flip(self.image, True, False) # Horizontal True, Vertical False axis


        # move
        self.rect.x += self.direction * self.speed * dt

        # reverse direction 
        # small rectangle that says if there a platform below next to enemies
        floor_rect_right = pygame.FRect(self.rect.bottomright, (1,1))
        floor_rect_left = pygame.FRect(self.rect.bottomleft, (-1,1))

        # OVO SAM JA NAPRAVIO :)
        # side_rect_right = pygame.FRect(self.rect.bottomright, (1,-1))
        # side_rect_left = pygame.FRect(self.rect.bottomleft, (-1,-1))
        wall_rect = pygame.FRect(self.rect.topleft + vector(-1,0),(self.rect.width + 2, 1))

        if floor_rect_right.collidelist(self.collision_rects) < 0 and self.direction > 0 :
            self.direction = -1
        elif  floor_rect_left.collidelist(self.collision_rects) < 0 and self.direction < 0 :
            self.direction = 1
        elif wall_rect.collidelist(self.collision_rects) != -1:
            self.direction *= -1
        # elif  side_rect_right.collidelist(self.collision_rects) > 0 and self.direction > 0:
        #     self.direction = -1
        # elif  side_rect_left.collidelist(self.collision_rects) > 0 and self.direction < 0:
        #     self.direction = 1

class Shell(pygame.sprite.Sprite):

    def __init__(self, pos, frames, groups, reverse, player, create_pearl):
        super().__init__(groups)

        if reverse:
            #flip all frames in frames
            self.frames = {}
            for key, surfs in frames.items():
                self.frames[key] = [pygame.transform.flip(surf, True, False) for surf in surfs]
            self.bullet_direction = -1 
        else:
            self.frames = frames
            self.bullet_direction = 1 
        self.frame_index = 0
        self.state = 'idle'
        self.image = self.frames[self.state][self.frame_index]
        
        self.rect = self.image.get_frect(topleft = pos)
        self.old_rect = self.rect.copy()    # Because we use collision group (collision_sprites)
        self.z = Z_LAYERS['main'] 
        self.player = player
        self.shoot_timer = Timer(2000)
        self.has_fired = False
        self.create_pearl = create_pearl

    def state_management(self):
        player_pos, shell_pos = vector(self.player.hitbox_rect.center), vector(self.rect.center)
        player_near = shell_pos.distance_to(player_pos) < 2000
        player_front = shell_pos.x < player_pos.x if self.bullet_direction > 0 else shell_pos.x > player_pos.x
        player_level = abs(shell_pos.y - player_pos.y) < 30     # abs  :)

        if player_near and player_front and player_level and not self.shoot_timer.active:
            self.state = 'fire'
            self.frame_index = 0
            self.shoot_timer.activate()


    def update(self, dt):
        self.shoot_timer.update()
        self.state_management() 

        # animation / attacl
        self.frame_index += ANIMATION_SPEED * dt
        if self.frame_index < len(self.frames[self.state]):
            self.image = self.frames[self.state][int(self.frame_index)]

            # fire
            if self.state == 'fire' and int(self.frame_index) == 3 and not self.has_fired:
                self.create_pearl(self.rect.center, self.bullet_direction)
                self.has_fired = True

        else:
            self.frame_index = 0
            if self.state == 'fire':
                self.state = 'idle'
                self.has_fired = False

class Pearl(pygame.sprite.Sprite):
    def __init__(self, pos, groups, surf, direction, speed):
        self.pearl = True
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = pos + vector(50 * direction,0))   # Pearl location
        self.direction = direction
        self.speed = speed
        self.z = Z_LAYERS['main']
        self.timers = {'lifetime' : Timer(10000), 'reverse' : Timer(250)}
        self.timers['lifetime'].activate()

    def reverse(self):
        if not self.timers['reverse'].active:
            self.direction *= -1
            self.timers['reverse'].activate()

    def update(self,dt):
        for timer in self.timers.values():
            timer.update()

        self.rect.x += self.direction * self.speed * dt
        if not self.timers['lifetime'].active:
            self.kill()
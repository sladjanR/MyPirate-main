from settings import *
from timer import Timer
from os.path import join    # Gives relative paths to specific os
from math import sin

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites, semi_collision_sprites, frames, data, jump_sound):
        # general setup
        super().__init__(groups)
        self.z = Z_LAYERS['main']
        self.data = data
        
        # image
        self.frames, self.frame_index = frames, 0
        self.state, self.facing_right = 'idle', True
        self.image = self.frames[self.state][self.frame_index]

        # Rects
        self.rect = self.image.get_frect(topleft = pos)
        
        self.hitbox_rect = self.rect.inflate(-70,-10) # On the left side we are shrinking rectangle by 36 and vertical on 18 on each side (-100, -36)
        self.old_rect = self.hitbox_rect.copy()
        self.start_pos = pos

        #------------------------
        # Movement
        # We can get vector because we import that from settings
        self.direction = vector(0,0)
        self.speed = 300    # Before we added data time (dt) it was 0.2
        self.gravity = 800 # Because fall speed is not the same with speed of x, so we created another variable
        self.jump = False
        self.jump_heigt = 400
        self.attacking = False

        #---------------------------
        # Collision
        self.collision_sprites = collision_sprites
        self.semi_collision_sprites = semi_collision_sprites
    

        # We want to know is player on surface, and if he is, then he can again jump
        self.on_surface = {"floor" : False, "left" : False, "right": False}
        self.platform = None

        # timer
        self.timers= {
            "wall jump" : Timer(200),
            "wall slide block" : Timer(250),
            "platform skip" : Timer(200),    # Experiment with all of this
            "attack block": Timer(3000),
            'hit': Timer(400),
        }

        #Audio
        self.jump_sound = jump_sound
        self.jump_sound.set_volume(0.1)

    def input(self):
        keys = pygame.key.get_pressed()
        input_vector = vector(0,0)

        if not self.timers["wall jump"].active:
            if keys[pygame.K_RIGHT]:
                input_vector.x += 1
                self.facing_right = True

            if keys[pygame.K_LEFT]:
                self.facing_right = False

                input_vector.x -= 1
            if keys[pygame.K_DOWN]:
                self.timers["platform skip"].activate()

            if keys[pygame.K_x]:
                self.attack()
            
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
            self.direction.x = input_vector.normalize().x if input_vector else input_vector.x  # normalize() -> We want to be sure that length is ALWAYS 1
            # Above we are used thernal operator because we cant normalize if vector have no elements
            # We added later to normalize only x (horizontal), but for y we want to be more than 1 (be faster)

        if keys[pygame.K_SPACE]:
            # self.direction.y = -100 -> This can be feature :)
            self.jump = True
    
    def attack(self):
        if not self.timers['attack block'].active:
            self.attacking = True
            self.frame_index = 0
            self.timers["attack block"].activate()


    def move(self, dt):
        # horizontal
        #self.rect.topleft += self.direction * self.speed * dt -> That was it look before
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision("horizontal")
        

        # vertical
        # If we fall longer it be faster, because of that we use Data Time (dt)
        # Also we want to fall be frame independent, if framerate changes not change behavior (because of that we divide by 2 and use two times)


        if not self.on_surface["floor"] and any((self.on_surface["left"], self.on_surface["right"])) and not self.timers["wall slide block"].active:
            self.direction.y = 0
            self.hitbox_rect.y += self.gravity / 10 * dt

        else:
            self.direction.y += self.gravity / 2  * dt
            self.hitbox_rect.y += self.direction.y * dt
            self.direction.y += self.gravity / 2  * dt


        # TODO: (srpski): OVAJ self.collision mi pravi problem, treba da je postavljen posle self.jump upita, ali jedino ovako radi
        self.collision("vertical")
        self.semi_collision()

        if self.jump:
            if self.on_surface["floor"]:
                self.direction.y = -self.jump_heigt
                self.timers["wall slide block"].activate()
                self.hitbox_rect.bottom -= 1   # Player is not glued to the platform
                self.jump_sound.play()
            elif any((self.on_surface["left"], self.on_surface["right"])) and not self.timers["wall slide block"].active:  # Once player is on wall, and we try to jump, we activate timer and not allow any left and right input
                self.timers["wall jump"].activate()     # To block two inputs (left and right)
                self.direction.y = -self.jump_heigt
                self.direction.x = 1 if self.on_surface["left"] else -1
                self.jump_sound.play()
            self.jump = False

        self.rect.center = self.hitbox_rect.center
    

    def platform_move(self, dt):
        if self.platform:
            self.hitbox_rect.topleft += self.platform.direction * self.platform.speed * dt       # We want to our player moves with platform with same speed and direction
    
    def check_contact(self):
        # We want to create a cuple of small rectangles around our player 1.08
        floor_rect = pygame.Rect(self.hitbox_rect.bottomleft,(self.hitbox_rect.width, 2))
        # Wall collision left and right 1.13
        right_rect = pygame.Rect(self.hitbox_rect.topright + vector(0, self.hitbox_rect.height / 4), (2, self.hitbox_rect.height / 2))
        left_rect = pygame.Rect(self.hitbox_rect.topleft  + vector(-2, self.hitbox_rect.height / 4), (2, self.hitbox_rect.height / 2))

        # To see if it works
        # pygame.draw.rect(self.display_surface, "yellow", floor_rect)
        # pygame.draw.rect(self.display_surface, "yellow", right_rect)
        # pygame.draw.rect(self.display_surface, "yellow", left_rect)

        collide_rects = [sprite.rect for sprite in self.collision_sprites]
        semi_collide_rect = [sprite.rect for sprite in self.semi_collision_sprites]

        # collisions
        self.on_surface["floor"] = True if floor_rect.collidelist(collide_rects) >= 0 or floor_rect.collidelist(semi_collide_rect) >= 0 and self.direction.y >=0 else False
        self.on_surface["right"] = True if right_rect.collidelist(collide_rects) >= 0 else False
        self.on_surface["left"]  = True if left_rect.collidelist(collide_rects)   >= 0 else False
        # print(self.on_surface)

        self.platform = None
        sprites = self.collision_sprites.sprites() + self.semi_collision_sprites.sprites()
        for sprite in [sprite for sprite in sprites if hasattr(sprite, 'moving')]:
            if sprite.rect.colliderect(floor_rect):
                self.platform = sprite


        #TODO:
        # Improve this that direction.y not goes no infinity :), it uses so much memory (of course we set that to 0 when is collision)
        # but what if we stay in one position so much time ;)


    def collision(self, axis):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):      
                if axis == "horizontal":
                    # Left collision -> but this isn't enought
                    if self.hitbox_rect.left <= sprite.rect.right and int(self.old_rect.left) >= int(sprite.old_rect.right):     # All old_rects in the int() function

                        self.hitbox_rect.left = sprite.rect.right

                    # Right collision
                    if self.hitbox_rect.right >= sprite.rect.left and int(self.old_rect.right) <= int(sprite.old_rect.left):
                        self.hitbox_rect.right = sprite.rect.left

                else: # Vertical collision
                    # Top
                    if self.hitbox_rect.top <=  sprite.rect.bottom and int(self.old_rect.top) >= int(sprite.old_rect.bottom):
                        self.hitbox_rect.top = sprite.rect.bottom
                        if hasattr(sprite, "moving"):
                            self.hitbox_rect.top += 6  # Fix bug when moving platform goes down, and player jumps, then player stucking in the middle of platform
                                                # You can TODO add timer to disable collison for the better feeling
                    # Bottom
                    if self.hitbox_rect.bottom >= sprite.rect.top and int(self.old_rect.bottom) <= int(sprite.old_rect.top):
                        self.hitbox_rect.bottom = sprite.rect.top
                    
                    self.direction.y = 0

    def semi_collision(self):
        if not self.timers["platform skip"].active:
            for sprite in self.semi_collision_sprites:
                if sprite.rect.colliderect(self.hitbox_rect):
                    if self.hitbox_rect.bottom >= sprite.rect.top and int(self.old_rect.bottom) <= sprite.old_rect.top:     # Added later to be in int()
                        self.hitbox_rect.bottom = sprite.rect.top
                        if self.direction.y > 0:
                            self.direction.y = 0


    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt
        if self.state == 'attack' and self.frame_index >= len(self.frames[self.state]):
            self.state = 'idle'

        self.image = self.frames[self.state][int(self.frame_index % len(self.frames[self.state]))]
        self.image = self.image if self.facing_right else pygame.transform.flip(self.image, True, False)

        if self.attacking and self.frame_index > len(self.frames[self.state]):
            self.attacking = False

    def get_state(self):
        if self.on_surface['floor']:
            if self.attack:
                self.state = 'attack'
            else:
                self.state = 'idle' if self.direction.x == 0 else 'run'
        else:
            if self.attacking:
                self.state = 'air_attack'
            else:
                if any((self.on_surface['left'], self.on_surface['right'])):
                    self.state = 'wall'
                else:
                    self.state = 'jump' if self.direction.y < 0 else 'fall'

    def get_damage(self):
        if not self.timers['hit'].active:
            self.data.health -= 1
            self.timers['hit'].activate()

    def flicker(self):  # Indicate that player current gets damage
        if self.timers['hit'].active and sin(pygame.time.get_ticks() * 150) >= 0:
            white_mask = pygame.mask.from_surface(self.image) #every pixel transparent will be black, and every that not will be white
            white_surf = white_mask.to_surface()

            # Important
            white_surf.set_colorkey('black')    # To remove black color, to be transparent
            self.image = white_surf

    def check_game_over(self):
        if self.data.health <= 0:
            self.hitbox_rect.x = self.start_pos[0]
            self.hitbox_rect.y = self.start_pos[1]
            # self.hitbox_rect.x = 2064
            # self.hitbox_rect.y = 372
            self.data.coins -= 10
            self.data.health = 2

    # Override
    def update(self, dt):
        self.old_rect = self.hitbox_rect.copy()    # Our old position before collision, to now from which side is collision, where is player before
        self.update_timers()

        self.input()
        self.move(dt)
        self.platform_move(dt)
        self.check_contact()

        self.get_state()
        self.check_game_over()
        self.animate(dt)
        self.flicker()
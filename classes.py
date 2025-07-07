import math, random
import pygame

#Global variables
FPS = 60
WIDTH = 720
HEIGHT = 640
MODE = 0
SOUND = 0
_BASE_HP = 1
_BASE_STR = 10
_BASE_SPD = 8

#Storage
def state():
    return [
        pygame.image.load("./imgs/ship.png").convert_alpha(),
        pygame.image.load("./imgs/ship_grace.png").convert_alpha(),
        pygame.image.load("./imgs/ship_shoot.png").convert_alpha(),
        pygame.image.load("./imgs/ship_shoot2.png").convert_alpha(),
        pygame.image.load("./imgs/ship_shoot3.png").convert_alpha(),
        ]

def ally_proj():
    return [
        pygame.image.load("./imgs/supply01.png").convert_alpha(),
        pygame.image.load("./imgs/supply02.png").convert_alpha(),
        pygame.image.load("./imgs/supply03.png").convert_alpha(),
        pygame.image.load("./imgs/supply04.png").convert_alpha(),
        pygame.image.load("./imgs/supply05.png").convert_alpha(),
        pygame.image.load("./imgs/supply06.png").convert_alpha(),
        ]

def death():
    return [
        pygame.image.load("./imgs/death1.png").convert_alpha(),
        pygame.image.load("./imgs/death2.png").convert_alpha(),
        pygame.image.load("./imgs/death3.png").convert_alpha(),
        pygame.image.load("./imgs/death4.png").convert_alpha(),
        pygame.image.load("./imgs/death5.png").convert_alpha(),
        pygame.image.load("./imgs/death6.png").convert_alpha(),
        pygame.image.load("./imgs/death7.png").convert_alpha(),
        pygame.image.load("./imgs/death8.png").convert_alpha(),
        pygame.image.load("./imgs/death9.png").convert_alpha(),
        pygame.image.load("./imgs/death10.png").convert_alpha(),
        pygame.image.load("./imgs/death11.png").convert_alpha(),
        pygame.image.load("./imgs/death12.png").convert_alpha(),
        pygame.image.load("./imgs/death13.png").convert_alpha()
    ]

def enemy_img():
    return [
        ["./imgs/space11.png", "./imgs/space12.png", "./imgs/space13.png", "./imgs/space14.png", "./imgs/space15.png"],
        ["./imgs/space21.png", "./imgs/space22.png", "./imgs/space23.png", "./imgs/space24.png", "./imgs/space25.png"],
        ["./imgs/space31.png", "./imgs/space32.png", "./imgs/space33.png", "./imgs/space34.png", "./imgs/space35.png"],
        ["./imgs/space81.png", "./imgs/space82.png", "./imgs/space83.png", "./imgs/space84.png", "./imgs/space85.png"],
        ["./imgs/space71.png", "./imgs/space72.png", "./imgs/space73.png", "./imgs/space74.png", "./imgs/space75.png"],
        ["./imgs/space61.png", "./imgs/space62.png", "./imgs/space63.png", "./imgs/space64.png", "./imgs/space65.png"],
        ["./imgs/space51.png", "./imgs/space52.png", "./imgs/space53.png", "./imgs/space54.png", "./imgs/space55.png"],
        ["./imgs/space91.png", "./imgs/space92.png", "./imgs/space93.png", "./imgs/space94.png", "./imgs/space95.png"],
        ["./imgs/space41.png", "./imgs/space42.png", "./imgs/space43.png", "./imgs/space44.png", "./imgs/space45.png"],
        ["./imgs/space10.1.png", "./imgs/space10.2.png", "./imgs/space10.3.png", "./imgs/space10.4.png", "./imgs/space10.5.png"],
        ["./imgs/space11.1.png", "./imgs/space11.2.png", "./imgs/space11.3.png", "./imgs/space11.4.png", "./imgs/space11.5.png"],
        ["./imgs/space12.1.png", "./imgs/space12.2.png", "./imgs/space12.3.png", "./imgs/space12.4.png", "./imgs/space12.5.png"],
        ["./imgs/space13.1.png", "./imgs/space13.2.png", "./imgs/space13.3.png", "./imgs/space13.4.png", "./imgs/space13.5.png"],
        ["./imgs/space14.1.png", "./imgs/space14.2.png", "./imgs/space14.3.png", "./imgs/space14.4.png", "./imgs/space14.5.png"]
    ]

def enemy_proj():
    return [
        pygame.image.load("./imgs/supply10.png").convert_alpha(),
        pygame.image.load("./imgs/supply20.png").convert_alpha(),
        pygame.image.load("./imgs/supply30.png").convert_alpha(),
        pygame.image.load("./imgs/supply40.png").convert_alpha(),
        pygame.image.load("./imgs/supply50.png").convert_alpha(),
    ]

def boss():
    return [
        pygame.image.load("./graph/boss01.png").convert_alpha(),
        pygame.image.load("./graph/boss02.png").convert_alpha(),
        pygame.image.load("./graph/boss03.png").convert_alpha(),
        pygame.image.load("./graph/boss04.png").convert_alpha()
    ]

def moveset():
    return [
        "neutral", "sniper", "spiral", "zigzag", "hover", "crazy"
    ]

#Classes
class Entity(pygame.sprite.Sprite):
    def __init__(self, health_point, speed, strength):
        super().__init__()
        self.health_point = health_point
        self.strength = strength
        self.speed = speed
        self.alive = True
        self.image = None
        self.rect = None

        self.image = pygame.Surface((32, 32))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()

    def take_damage(self, damage):
        self.health_point -= damage
        if self.health_point < 0:
            self.health_point = 0
            self.alive = False
            return

class Ship(Entity):
    def __init__(self, images, movement_mode="mode1"):
        super().__init__(_BASE_HP, _BASE_SPD, _BASE_STR)
        self.grace = 5000
        self.life = 1
        self.score = 0
        self.bomb = 3
        self.level = 4
        self.movement_mode = movement_mode

        self.shooting_cd = 70
        self.last_shot = 0
        self.firing = False
        self.firing_time = 0

        self.skin = images
        self.image = self.skin[0]
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT - 50)

        self.hitbox = pygame.Rect(0, 0, 10, 10)
        self.hitbox.centerx = self.rect.centerx
        self.hitbox.centery = self.rect.centery + 6

        self.invincible = False
        self.invincible_time = 5000
        self.invincible_start = 0

        self.dframes = death()
        self.death_timer = 0


    def update(self):
        if self.alive:
            self.hitbox.center = self.rect.center
            self.hitbox.centerx = self.rect.centerx
            self.hitbox.centery = self.rect.centery + 7

            keys = pygame.key.get_pressed()

            # === Movement mode 1: wasd ===
            if self.movement_mode == "mode1":
                if keys[pygame.K_a]:
                    self.rect.x -= self.speed if not keys[pygame.K_LSHIFT] else self.speed // 2
                    if self.rect.left < 0:
                        self.rect = self.rect.move(WIDTH - 32, 0)
                if keys[pygame.K_d]:
                    self.rect.x += self.speed if not keys[pygame.K_LSHIFT] else self.speed // 2
                    if self.rect.right > WIDTH:
                        self.rect = self.rect.move(-WIDTH + 32, 0)
                if keys[pygame.K_w]:
                    self.rect.y -= self.speed if not keys[pygame.K_LSHIFT] else self.speed // 2
                    if self.rect.top <= 0:
                        self.rect.top = 0
                if keys[pygame.K_s]:
                    self.rect.y += self.speed if not keys[pygame.K_LSHIFT] else self.speed // 2
                    if self.rect.bottom > HEIGHT:
                        self.rect.bottom = HEIGHT

            # === Movement mode 2: arrow keys ===
            else:
                if keys[pygame.K_LEFT]:
                    self.rect.x -= self.speed if not keys[pygame.K_LSHIFT] else self.speed // 2
                    if self.rect.left < 0:
                        self.rect = self.rect.move(WIDTH - 32, 0)
                if keys[pygame.K_RIGHT]:
                    self.rect.x += self.speed if not keys[pygame.K_LSHIFT] else self.speed // 2
                    if self.rect.right > WIDTH:
                        self.rect = self.rect.move(-WIDTH + 32, 0)
                if keys[pygame.K_UP]:
                    self.rect.y -= self.speed if not keys[pygame.K_LSHIFT] else self.speed // 2
                    if self.rect.top <= 0:
                        self.rect.top = 0
                if keys[pygame.K_DOWN]:
                    self.rect.y += self.speed if not keys[pygame.K_LSHIFT] else self.speed // 2
                    if self.rect.bottom > HEIGHT:
                        self.rect.bottom = HEIGHT

            if self.firing and pygame.time.get_ticks() - self.firing_time > 100:
                self.image = self.skin[0]
                self.firing = False

            if self.invincible:
                if (pygame.time.get_ticks() // 400) % 2 == 0:
                    self.image = self.skin[1]
                else:
                    self.image = self.skin[0]
            if self.invincible and pygame.time.get_ticks() - self.invincible_start > self.invincible_time:
                self.invincible = False
                self.image = self.skin[0]
        else:
            tsd = pygame.time.get_ticks() - self.death_timer
            frame_dura = 200
            fridx = tsd // frame_dura
            if fridx < len(self.dframes):
                self.image = self.dframes[fridx]
            else:
                if self.life > 1:
                    self.health_point = 1
                    self.life -= 1
                    self.rect.center = (WIDTH // 2, HEIGHT - 50)
                    self.grace_period()
                    self.alive = True
                else:
                    self.kill()
                    print("L")
                    exit()
    #Override
    def take_damage(self, amount):
        if not self.invincible:
            super().take_damage(amount) #super already have self
            if self.health_point <= 0:
                self.alive = False
                self.death_timer = pygame.time.get_ticks()

class Enemy(Entity):
    def __init__(self, health_point, speed, points, behavior):
        super().__init__(health_point, speed, 10)
        self.image = pygame.Surface((32, 32))  # Placeholder for enemy image
        self.image.fill((0, 0, 255))  # Default blue
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, 50)
        self.points = points
        self.spawn_time = pygame.time.get_ticks()
        self.leave = 15000
        self.behavior = behavior
        self.shoot_start = pygame.time.get_ticks()
        self.shoot_duration = 500
        self.shoot_cd = 20
        self.last_shot = 0
        self.shot = False

        #Sniper boy
        self.direction = random.choice([-1,1])
        self.last_aim = 0
        self.aim_cd = random.randint(1000, 2000)
        self.sniper_burst_size = 10
        self.sniper_burst_count = 0
        self.sniper_bullet_delay = 30
        self.sniper_last_bullet_time = 0

        #Spiral boy
        self.phase = 0 
        self.angle = 0

        #Zigzag boy 
        self.vertical = 1
        self.horizontal = 1
        self.zigzag_counter = 0

        #Hover boy
        self.hover_start_x = self.rect.x

        #Crazy boy
        self.crazy_counter = 0

    def move_and_shoot(self, projectile_group, player_pos = None):
        now = pygame.time.get_ticks()
        bspd = 2
        if not self.alive:
            return
        if now - self.spawn_time > self.leave:
            self.kill()
            return
        if self.behavior == "neutral":
            self.rect.x += int(10 * math.sin(now / 300))
            if not self.shot:
                if now - self.shoot_start < self.shoot_duration:
                    if now - self.last_shot > self.shoot_cd:
                        angles = [-15, 0, 15]
                        for angle in angles:
                            rad = math.radians(angle)
                            dx = bspd * math.sin(rad)
                            dy = bspd * math.cos(rad)
                            proj = enemy_proj()[0]
                            bullet = Projectile(self.rect.centerx, self.rect.centery,
                                                proj, dy, dx, owner = "enemy")
                            projectile_group.add(bullet)
                        self.last_shot = now
                else:
                    self.shot = True

        elif self.behavior == "sniper":
            self.rect.x += self.speed * self.direction // 1.5

            if self.rect.left < 0:
                self.rect.left = 0
                self.direction *= -1
            if self.rect.right > WIDTH:
                self.rect.right = WIDTH
                self.direction *= -1
            
            if not self.shot:
                if now - self.last_aim > self.aim_cd and player_pos:
                    
                    # If we have bullets left in the burst and it's time to shoot
                    if now - self.sniper_last_bullet_time > self.sniper_bullet_delay:
                        # Calculate direction to player
                        dx = player_pos[0] - self.rect.centerx
                        dy = player_pos[1] - self.rect.centery
                        
                        # Normalize direction vector
                        distance = max(1, math.sqrt(dx*dx + dy*dy))
                        dx = dx / distance
                        dy = dy / distance
                        
                        # Create bullet aimed at player
                        proj = enemy_proj()[1]
                        bullet = Projectile(
                            self.rect.centerx, self.rect.centery,
                            proj, dy * 8, dx * 8, owner="enemy"
                        )
                        projectile_group.add(bullet)
                        self.sniper_last_bullet_time = now
                        
                        self.shot = True
                        self.last_aim = now
                        self.aim_cd = random.randint(1000, 3000)
            

        elif self.behavior == "spiral":
            self.angle += 0.1
            radius = 50
            self.rect.x = WIDTH // 2 + math.cos(self.angle) * radius
            self.rect.y = 100 + math.sin(self.angle) * radius
            
            # Shoot circle pattern
            if now - self.shoot_start < self.shoot_duration:
                if now - self.last_shot > 100:
                    for i in range(0, 360, 30):
                        rad = math.radians(i)
                        dx = bspd * math.cos(rad)
                        dy = bspd * math.sin(rad)
                        proj = enemy_proj()[2]
                        bullet = Projectile(self.rect.centerx, self.rect.centery,
                                            proj, dy, dx, owner="enemy")
                        projectile_group.add(bullet)
                    self.last_shot = now
            else:
                self.shot = True
        
        elif self.behavior == "zigzag":
            self.rect.y += (self.speed * self.horizontal) // 1.5

            if self.rect.top <= 0 or self.rect.bottom >= HEIGHT // 5:
                self.horizontal *= -1

            self.rect.x += (self.speed * self.vertical) // 1.5

            if self.rect.left <= 0 or self.rect.right >= WIDTH:
                self.vertical *= -1
            
            if not self.shot:
                if now - self.shoot_start < 3000:
                    if now - self.last_shot > 100:
                        proj = enemy_proj()[3]
                        dy = bspd
                        bullet = Projectile(self.rect.centerx, self.rect.centery,
                                            proj, dy, owner="enemy")
                        projectile_group.add(bullet)
                        self.last_shot = now
                else:
                    self.shot = True
        
        elif self.behavior == "crazy":
            self.crazy_counter += 1
            if self.crazy_counter % 30 == 0:
                self.rect.x += random.randint(-self.speed * 2, self.speed * 2)
                self.rect.y += random.randint(-self.speed, self.speed)
                
                # Keep in bounds
                if self.rect.left < 0: self.rect.left = 0
                if self.rect.right > WIDTH: self.rect.right = WIDTH
                if self.rect.top < 0: self.rect.top = 0
                if self.rect.bottom > HEIGHT // 2: self.rect.bottom = HEIGHT // 2
            
            # Unpredictable shooting
            if now - self.last_shot > random.randint(50, 300):
                pattern = random.choice(["spray", "burst", "targeted"])
                
                if pattern == "spray":
                    # Spray bullets in wide arc
                    for angle in range(-45, 46, 15):
                        rad = math.radians(angle)
                        dx = bspd * math.sin(rad)
                        dy = bspd * math.cos(rad)
                        proj = enemy_proj()[random.randint(0, 4)]
                        bullet = Projectile(self.rect.centerx, self.rect.centery,
                                            proj, dy, dx, owner="enemy")
                        projectile_group.add(bullet)
                
                elif pattern == "burst":
                    # Quick burst of bullets
                    for _ in range(5):
                        angle = random.randint(-30, 30)
                        rad = math.radians(angle)
                        dx = bspd * math.sin(rad)
                        dy = bspd * math.cos(rad)
                        proj = enemy_proj()[random.randint(0, 4)]
                        bullet = Projectile(self.rect.centerx, self.rect.centery,
                                            proj, dy, dx, owner="enemy")
                        projectile_group.add(bullet)
                
                elif pattern == "targeted":
                    # Aimed shots in player's general direction
                    if player_pos:
                        for _ in range(3):
                            # Calculate approximate direction to player
                            dx = player_pos[0] - self.rect.centerx + random.randint(-50, 50)
                            dy = player_pos[1] - self.rect.centery + random.randint(-50, 50)
                            
                            # Normalize direction vector
                            distance = max(1, math.sqrt(dx*dx + dy*dy))
                            dx = dx / distance
                            dy = dy / distance
                            
                            proj = enemy_proj()[random.randint(0, 4)]
                            bullet = Projectile(self.rect.centerx, self.rect.centery,
                                                proj, dy * 4, dx * 4, owner="enemy")
                            projectile_group.add(bullet)
                
                self.last_shot = now


class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, image, direction_y, direction_x=0, owner="enemy"):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = direction_x
        self.dy = direction_y
        self.owner = owner
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

        # Remove if off screen
        if (self.rect.bottom < 0 or self.rect.top > HEIGHT or
            self.rect.right < 0 or self.rect.left > WIDTH):
            self.kill()
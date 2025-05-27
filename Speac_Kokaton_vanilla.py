import math
import pygame
import sys
import random
import math
import pygame.mixer
import time

pygame.init()
WIDTH, HEIGHT = 480, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("space_kokaton")
clock = pygame.time.Clock()

WHITE = (255, 255, 255) 
RED = (255, 0, 0)

# 画像読み込み
bg_img = pygame.image.load("fig/space_bg.jpg")
player_img = pygame.image.load("fig/1.png")
enemy_img = pygame.image.load("fig/alien1.png")
beam_img = pygame.image.load("fig/beam.png")
beam_img = pygame.transform.rotate(beam_img, 90)
sad_kokaton_img = pygame.image.load("fig/8.png")
explosion_img = pygame.image.load("fig/explosion.gif").convert_alpha()

#音
pygame.mixer.init()
explosion_sound = pygame.mixer.Sound("fig/explosion.mp3")
beam_sound = pygame.mixer.Sound("fig/beam1.mp3")
gameover_sound = pygame.mixer.Sound("fig/gameover.mp3")

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT - 60))
        self.hp = 3  # HP（ライフ）追加

    def update(self, keys):
        speed = 8 if keys[pygame.K_LSHIFT] else 5
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += speed

class Beam(pygame.sprite.Sprite):
    def __init__(self, x, y, angle=0):
        super().__init__()
        self.original_image = beam_img
        self.image = pygame.transform.rotate(self.original_image, -angle)
        self.rect = self.image.get_rect(center=(x, y))

        self.angle = math.radians(angle)
        self.speed = 10
        self.vx = self.speed * math.sin(self.angle)
        self.vy = -self.speed * math.cos(self.angle)
        beam_sound.play() #　←　ビーム音を鳴らす

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy

        # 画面外に出たら削除
        if (self.rect.bottom < 0 or self.rect.top > HEIGHT or
            self.rect.right < 0 or self.rect.left > WIDTH):
            self.kill()

class Bomb(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        radius = 8
        self.image = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 255, 0), (radius, radius), radius)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            explosion_group.add(Explosion(self.rect.center))
            self.kill()

# 追加機能始
class HanshaBomb(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        radius = 8 #  弾の大きさ
        self.image = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 0, 0), (radius, radius), radius)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed_y = 4
        self.speed_x = 5
        self.direction_x = 1 
        self.direction_y = -1

    def update(self):
        self.rect.y += self.speed_y * self.direction_y
        self.rect.x += self.speed_x * self.direction_x

        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.direction_x *= -1

        if self.rect.top <= 0:
            self.direction_y *= -1

        if self.rect.top > HEIGHT:
            explosion_group.add(Explosion(self.rect.center))
            self.kill()

    
class TuijuBomb(pygame.sprite.Sprite):
    def __init__(self, x, y, target):
        super().__init__()
        radius = 10
        self.image = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (0, 255, 0), (radius, radius), radius)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 2
        self.target = target  

    def update(self):
        dx = self.target.rect.centerx - self.rect.centerx
        dy = self.target.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist != 0:
            dx, dy = dx / dist, dy / dist
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed

        if self.rect.top > HEIGHT or self.rect.left < 0 or self.rect.right > WIDTH:
            self.kill()

class bakuhatuBomb(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        radius = 15
        self.image = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 165, 0), (radius, radius), radius)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 30  # 弾の速さ
        self.timer = 10  # 爆発までの時間

    def update(self):
        self.rect.y += self.speed
        self.timer -= 1
        if self.timer <= 0 or self.rect.top > HEIGHT:
            explosion_group.add(Explosion(self.rect.center))
            # 爆風の範囲内にあるプレイヤーやビームに影響を与える
            if self.rect.colliderect(player.rect):
                global game_over
                game_over = True
            self.kill()
# 追加機能終

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect(center=(random.randint(40, WIDTH-40), -40))
        self.speed = random.randint(2, 4)
        self.dx = random.choice([-2, -1, 1, 2])
        self.drop_timer = 0
        self.fast_bomb = random.random() < 0.2

    def update(self):
        self.rect.y += self.speed
        self.rect.x += self.dx

        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.dx *= -1

        self.drop_timer += 1  
        
        if self.rect.top > HEIGHT:
            self.kill()

        if self.drop_timer > 60:
            self.drop_timer = 0
            # 追加機能始
            if random.random() < 1.0: # 弾の確率
                if self.fast_bomb:
                    bomb = Bomb(self.rect.centerx, self.rect.bottom)
                    bomb.speed = 10
                    bomb_group.add(bomb)
                else:
                    if random.random() < 0.2:
                        bomb = Bomb(self.rect.centerx, self.rect.bottom)
                        bomb_group.add(bomb)
                if random.random() < 0.3:
                        bomb_group.add(TuijuBomb(self.rect.centerx, self.rect.bottom, player))
                if random.random() < 0.5:
                        bomb_group.add(bakuhatuBomb(self.rect.centerx, self.rect.bottom))
                bomb_group.add(HanshaBomb(self.rect.centerx, self.rect.bottom))
            # 追加機能終





class Gravity(pygame.sprite.Sprite):
    def __init__(self, life):
        super().__init__()
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 100))
        self.rect = self.image.get_rect()
        self.life = life

    def update(self):
        self.life -= 1
        if self.life < 0:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = explosion_img
        self.rect = self.image.get_rect(center=pos)
        self.life = 15
        explosion_sound.play() # ←　爆発音を鳴らす

    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()

player = Player()
player_group = pygame.sprite.Group(player)
beam_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
bomb_group = pygame.sprite.Group()
gravity_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

score = 0
skill_points = 0  # 追加1：スキルポイント用変数
font = pygame.font.SysFont("Arial", 24)

enemy_timer = 0
scroll_y = 0
game_over = False

while True:
    screen.fill((0, 0, 0))

    scroll_y = (scroll_y + 2) % HEIGHT
    screen.blit(bg_img, (0, -HEIGHT + scroll_y))
    screen.blit(bg_img, (0, scroll_y))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if len(beam_group) < 100:
                angles = [-15, 0, 15] if pygame.key.get_mods() & pygame.KMOD_LSHIFT else [0]
                for angle in angles:
                    beam_group.add(Beam(player.rect.centerx, player.rect.top, angle))
    if not game_over:
        keys = pygame.key.get_pressed()
        player.update(keys)

        if keys[pygame.K_SPACE]:
            if len(beam_group) < 10:
                beam_group.add(Beam(player.rect.centerx, player.rect.top))

        if keys[pygame.K_RETURN] and skill_points >= 300 and len(gravity_group) == 0:
            gravity_group.add(Gravity(400))
            skill_points -= 300 #追加機能1:重力場にスキルポイントを使う

        enemy_timer += 1
        if enemy_timer > 30:
            enemy_timer = 0
            if len(enemy_group) < 3:   
                enemy_group.add(Enemy())

        if gravity_group:
            gravity = gravity_group.sprites()[0]
            for enemy in enemy_group:
                if gravity.rect.colliderect(enemy.rect):
                    explosion_group.add(Explosion(enemy.rect.center))
                    enemy.kill()
                    score += 100
                    skill_points += 10 # ← 追加機能1スキルポイントの加算
            for bomb in bomb_group:
                if gravity.rect.colliderect(bomb.rect):
                    explosion_group.add(Explosion(bomb.rect.center))
                    bomb.kill()
                    score += 50
                    skill_points += 5 #追加機能1スキルポイントも加算

        gravity_group.update()
        beam_group.update()
        enemy_group.update()
        bomb_group.update()
        explosion_group.update()

        # ビームと敵の衝突判定
        collisions = pygame.sprite.groupcollide(beam_group, enemy_group, True, True)
        if collisions:
            for enemy_list in collisions.values():
                for enemy in enemy_list:
                    explosion_group.add(Explosion(enemy.rect.center))
            score += 100 * len(collisions)
            skill_points += 10 * len(collisions) # ← 追加機能1:スキルポイントの加算

        # ビームと爆弾の衝突判定
        bomb_collisions = pygame.sprite.groupcollide(beam_group, bomb_group, True, True)
        if bomb_collisions:
            for bomb_list in bomb_collisions.values():
                for bomb in bomb_list:
                    explosion_group.add(Explosion(bomb.rect.center))
            score += 50 * len(bomb_collisions)
            skill_points += 5 * len(bomb_collisions) #追加機能1:スキルポイントの加算

        # HPによる衝突処理（ここが変更点）
        hit_bomb = pygame.sprite.spritecollideany(player, bomb_group)
        hit_enemy = pygame.sprite.spritecollideany(player, enemy_group)
        if hit_bomb:
            explosion_group.add(Explosion(player.rect.center))
            hit_bomb.kill()
            player.hp -= 1
        if hit_enemy:
            explosion_group.add(Explosion(player.rect.center))
            hit_enemy.kill()
            player.hp -= 1
        if player.hp <= 0:
            game_over = True

        # 描画
        gravity_group.draw(screen)
        player_group.draw(screen)
        beam_group.draw(screen)
        enemy_group.draw(screen)
        bomb_group.draw(screen)
        explosion_group.draw(screen)

        score_text = font.render(f"Score: {score}", True, WHITE)
        skill_text = font.render(f"Skill: {skill_points}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(skill_text, (10, 40))

        hp_text = font.render(f"HP: {player.hp}", True, RED)
        screen.blit(hp_text, (10, 40))

    else:
        game_over_text = font.render("GAME OVER", True, RED)
        score_text = font.render(f"Final Score: {score}", True, WHITE)
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 80))
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 - 40))
        kokaton_rect = sad_kokaton_img.get_rect(center=(WIDTH//2, HEIGHT//2 + 80))
        screen.blit(sad_kokaton_img, kokaton_rect)

    pygame.display.update()
    clock.tick(60)

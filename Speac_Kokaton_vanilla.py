import math
import pygame
import sys
import random

pygame.init()
WIDTH, HEIGHT = 480, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("space_kokaton")
clock = pygame.time.Clock()

# 色定義
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

        if self.rect.top > HEIGHT:
            self.kill()

        self.drop_timer += 1
        if self.drop_timer > 60:
            self.drop_timer = 0
            if random.random() < 0.2:
                bomb = Bomb(self.rect.centerx, self.rect.bottom)
                if self.fast_bomb:
                    bomb.speed = 10
                bomb_group.add(bomb)

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

        if keys[pygame.K_RETURN] and score >= 2000 and len(gravity_group) == 0:
            gravity_group.add(Gravity(400))
            score -= 2000

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
            for bomb in bomb_group:
                if gravity.rect.colliderect(bomb.rect):
                    explosion_group.add(Explosion(bomb.rect.center))
                    bomb.kill()
                    score += 50

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

        # ビームと爆弾の衝突判定
        bomb_collisions = pygame.sprite.groupcollide(beam_group, bomb_group, True, True)
        if bomb_collisions:
            for bomb_list in bomb_collisions.values():
                for bomb in bomb_list:
                    explosion_group.add(Explosion(bomb.rect.center))
            score += 50 * len(bomb_collisions)

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
        screen.blit(score_text, (10, 10))

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

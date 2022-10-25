import pygame as pg
import random
import time
import threading

tps = 600
width = 360
height = 600
column = 8
row = 6
bullet_ready = True
bullet_num = 5
shoot_over = True
white = (255,255,255)
running = True
atk = 100
player_pos = width / 2
level = 0

pg.init()  # 初始化pygame
pg.display.set_caption("碰碰法師")  # 設定標題
screen = pg.display.set_mode((width, height))  # 設定視窗大小
clock = pg.time.Clock()

class Player(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((40,40))
        self.image.fill((0,0,0))
        self.rect = self.image.get_rect()  # 位置
        self.rect.centerx = width/2
        self.rect.bottom = height -10
        self.health = 1000  # 當前血量
        self.full_health = 1000  # 最大血量

    def shoot(self, mouse_pos):  # 發射子彈
        if mouse_pos[1] < 530:  # 若發射角度過低則不發射
            global bullet_ready, bullet_recycle
            bullet_ready = False  # 發射後在下一輪前不能發射
            bullet_recycle = 0
            for i in range(bullet_num):  # 讓子彈依序發射
                ball = Ball(self.rect.centerx, self.rect.top, mouse_pos)
                sprites.add(ball)
                bullet_group.add(ball)
                time.sleep(40/tps)
                
    def draw_health(self, screen, x, y):
        if self.health <= 0:  # 若生命小於等於0則結束遊戲
            self.health = 0
            global running
            running = False
        if self.health > self.full_health:  # 顯示血量條
            self.health = self.full_health
        bar_length = 100
        bar_height = 10
        fill = (self.health/self.full_health)*bar_length
        outline_rect = pg.Rect(x, y, bar_length, bar_height)
        fill_rect = pg.Rect(x, y, fill, bar_height)
        pg.draw.rect(screen, (0,255,0), fill_rect)
        pg.draw.rect(screen, (0,0,0), outline_rect, 2)

class Ball(pg.sprite.Sprite):
    def __init__(self, x, y, mouse_pos):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((20, 20))
        self.image.fill((255,255,0))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.x = int(self.rect.x)
        self.y = int(self.rect.y)
        self.speed = 1
        self.dir = pg.math.Vector2(mouse_pos[0] - x, mouse_pos[1] - y).normalize()  # 發射方向
        self.speedx = float(self.dir[0] * self.speed)
        self.speedy = float(self.dir[1] * self.speed)

    def update(self):
        self.x += float(self.speedx)
        self.y += float(self.speedy)
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        if self.rect.right > width or self.rect.left < 0:  # 撞牆反彈
            self.speedx = -self.speedx
        if self.rect.top < 0:  # 觸頂反彈
            self.speedy -= self.speedy * 2
        if self.rect.bottom >= player.rect.top + 10:  #觸底回收
            global shoot_over, level, player_pos, bullet_recycle
            if player_pos == '':  # 球第一個落下的位置決定玩家下一個位置
                player_pos = self.rect.centerx
            self.kill()
            bullet_recycle += 1
            if bullet_recycle == bullet_num:  # 子彈全數回收後開啟下一回合
                shoot_over = True

# 敵人與物件
class AddBall(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((60, 60))
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect()
        self.rect.topleft = ((x, y))
        self.survival_time = 0
    
    def round_end(self):
        i.rect.y += 60
        i.survival_time += 1
        if i.survival_time == 7:
            i.kill()

class AddSkill(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((60, 60))
        self.image.fill((0, 0, 200))
        self.rect = self.image.get_rect()
        self.rect.topleft = ((x, y))
        self.survival_time = 0

    def round_end(self):
        i.rect.y += 60
        i.survival_time += 1
        if i.survival_time == 7:
            i.kill()

class Monster1(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((60, 60))
        self.image.fill((0, 0, 150))
        self.rect = self.image.get_rect()
        self.rect.topleft = ((x, y))
        self.health = 1500
        self.survival_time = 0
    def round_end(self):
        self.survival_time += 1
        if self.survival_time == 7:
            self.kill()
        player.health -= 50
        self.rect.y += 60

class Monster2(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((60, 60))
        self.image.fill((0, 0, 100))
        self.rect = self.image.get_rect()
        self.rect.topleft = ((x, y))
        self.health = 2000
        self.survival_time = 0
    def round_end(self):
        self.survival_time += 1
        if self.survival_time == 7:
            player.health -= 200
            self.kill()
        self.rect.y += 60

# 生成敵人與物件到場上
class CreateMap:
    def __init__(self):
        self.block = 60
        self.enemy_map = []
        self.none = 0

    def create(self):
        self.enemy_map = [0, 0, 0, 0, 0, 0]
        for i in range(row):
            self.enemy_map[i] = random.randint(0, 5+level//10)
            if self.enemy_map[i] == 0:
                self.none += 1
            if self.enemy_map[i] == 1:
                self.none += 1
                for j in range(i):
                    if self.enemy_map[j] == 1:
                        self.enemy_map[i] = 0
            if self.enemy_map[i] == 2:
                self.none += 1
                for j in range(i):
                    if self.enemy_map[j] == 2:
                        self.enemy_map[i] = 0
        if self.none == 0:
            x = random.randint(0, row-1)
            self.enemy_map[x] = random.randint(0,2)
        for i in range(row):
            object = ''
            if self.enemy_map[i] == 0:
                continue
            if self.enemy_map[i] == 1:
                object = AddBall(i*self.block + 1, 61)
                add_ball_group.add(object)
            if self.enemy_map[i] == 2:
                object = AddSkill(i*self.block + 1, 61)
                add_skill_group.add(object)
            if self.enemy_map[i] == 3 or self.enemy_map[i] == 8:
                object = Monster1(i*self.block + 1, 61)
                monster_group.add(object)
            if 8 > self.enemy_map[i] > 3 or self.enemy_map[i] > 8:
                object = Monster2(i*self.block + 1, 61)
                monster_group.add(object)
            sprites.add(object)

player = Player()
map = CreateMap()
bullet_group = pg.sprite.Group()
add_ball_group = pg.sprite.Group()
add_skill_group = pg.sprite.Group()
monster_group = pg.sprite.Group()
sprites = pg.sprite.Group()
sprites.add(player)

while running:
  # 偵測輸入
    clock.tick(tps)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.MOUSEBUTTONDOWN and bullet_ready:
            mouse_pos = event.pos
            shoot = threading.Thread(target=player.shoot, args=(mouse_pos,))
            shoot.start()

  # 更新遊戲
    sprites.update()
    hits = pg.sprite.groupcollide(monster_group, bullet_group, False, False)
    for hit in hits:  # 碰撞反彈
        hit_pos = hit.rect.center
        bullet_pos = hits[hit][0].rect.center
        if abs(hit_pos[0] - bullet_pos[0]) >= abs(hit_pos[1] - bullet_pos[1]):
            if (hits[hit][0].speedx > 0 and hit_pos[0] - bullet_pos[0] > 0) or (hits[hit][0].speedx < 0 and hit_pos[0] - bullet_pos[0] < 0):
                hits[hit][0].speedx = -hits[hit][0].speedx
        if abs(hit_pos[0] - bullet_pos[0]) <= abs(hit_pos[1] - bullet_pos[1]):
            if (hits[hit][0].speedy > 0 and hit_pos[1] - bullet_pos[1] > 0) or (hits[hit][0].speedy < 0 and hit_pos[1] - bullet_pos[1] < 0):
                hits[hit][0].speedy = -hits[hit][0].speedy
        if hits[hit][0].speedx == 0:
            hits[hit][0].speedy = -hits[hit][0].speedy
        hit.health -= atk
        if hit.health <= 0:
            hit.kill()
            heal = random.randint(0,1)
            if heal == 1:
                player.health += 300
    add_balls = pg.sprite.groupcollide(add_ball_group, bullet_group, True, False)
    for add_ball in add_balls:
        bullet_num += 1
        bullet_recycle += 1
    pg.sprite.groupcollide(add_skill_group, bullet_group, True, False)
    if shoot_over:
        for i in monster_group:
            i.round_end()
        for i in add_ball_group:
            i.round_end()
        for i in add_skill_group:
            i.round_end()
        level += 1
        player.rect.centerx = player_pos
        player_pos = ''
        map.create()
        shoot_over, bullet_ready = False, True

  # 顯示畫面
    screen.fill(white)
    player.draw_health(screen, 5, 10)
    sprites.draw(screen)
    pg.display.update()

pg.quit()
# TODO：美工設計
# TODO：碰撞反彈算法優化
# TODO：遊戲開始、結算畫面與紀錄
# TODO：技能系統
# TODO：參數調整
# TODO：把球換成圓形
# TODO：怪物血量條

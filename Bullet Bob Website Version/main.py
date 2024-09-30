# /// script
# dependencies = [
#  "pygame",
#  "asyncio",
#  "random",
#  "math"
# ]
# ///

import pygame
import asyncio
import random
import math

async def main():

  w_width = 720
  w_height = w_width

  pygame.init()
  window = pygame.display.set_mode((w_width, w_height))
  pygame.display.set_caption("Bullet Bob")
  bullets = []
  enemies = []
  enemy_speed = 1
  bullet_speed = 10

  #sounds
  player_hurt_sound = pygame.mixer.Sound("sfx/player_hurt.ogg")
  assault_rifle_fired = pygame.mixer.Sound("sfx/assault_rifle_sound.ogg")
  enemy_death_sound = pygame.mixer.Sound("sfx/enemy_death.ogg")
  shotgun_fired = pygame.mixer.Sound("sfx/shotgun_sound.ogg")
  bullet_hit_sound = pygame.mixer.Sound("sfx/bullet_hit_sound_clipped.ogg")

  player_hurt_sound.set_volume(1)
  assault_rifle_fired.set_volume(0.3)
  enemy_death_sound.set_volume(1)
  shotgun_fired.set_volume(0.3)
  bullet_hit_sound.set_volume(1)

  pygame.mixer.set_num_channels(32)

  player_skin = pygame.image.load("person.png").convert_alpha()
  player_skin = pygame.transform.scale(player_skin, (20, 40))

  ak_gun = pygame.image.load("aka_gun.png").convert_alpha()
  ak_gun = pygame.transform.scale(ak_gun, (60, 20))
  ak_gun_flipped = pygame.transform.flip(ak_gun, True, False)

  shoot_gun = pygame.image.load("shoot_gun.png").convert_alpha()
  shoot_gun = pygame.transform.scale(shoot_gun, (60, 20))
  shoot_gun_flipped = pygame.transform.flip(shoot_gun, True, False)

  rocket_launcher = pygame.image.load("rocket_launcher.png").convert_alpha()
  rocket_launcher = pygame.transform.scale(rocket_launcher, (60, 20))
  rocket_launcher_flipped = pygame.transform.flip(rocket_launcher, True, False)

  bullet_skin = pygame.image.load("Bullet.png").convert_alpha()
  bullet_skin = pygame.transform.scale(bullet_skin, (20, 10))

  rocket_skin = pygame.image.load("rocket.png").convert_alpha()
  rocket_skin = pygame.transform.scale(rocket_skin, (30, 10))

  current_gun = "Assault Rifle"

  num_bullets_shot = 1
  score = 0
  bullets_hit = 0
  bullets_missed = 0
  pointx, pointy = pygame.mouse.get_pos()
  reload = 0
  reload_max = 3
  px = 0
  py = 0

  def blitRotate(surf, image, pos, originPos, angle):

    # offset from pivot to center
    image_rect = image.get_rect(topleft = (pos[0] - originPos[0], pos[1]-originPos[1]))
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center
    
    # roatated offset from pivot to center
    rotated_offset = offset_center_to_pivot.rotate(-angle)

    # roatetd image center
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)

    # get a rotated image
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)

    # rotate and blit the image
    rotated_image.set_colorkey("white")
    rotated_image.convert_alpha()
    surf.blit(rotated_image, rotated_image_rect)

  #player class
  class Player(pygame.sprite.Sprite):
    #init method
    def __init__(self, x, y):
      self.x = x
      self.y = y
      self.enemy_spawn_timer = 1
      self.health = 100
      self.mx, self.my = pygame.mouse.get_pos()
      if current_gun == "Assault Rife" or current_gun == "Rocket Launcher":
        self.bullets_fired = 1
      else:
        self.bullets_fired = 12

    #draw healthbar method
    def healthbar(self):
      self.healthbar_rect = pygame.rect.Rect(self.x - 10, self.y - 10, self.health/2.5, 4)
      self.healthbar_bg = pygame.rect.Rect(self.x - 10, self.y - 10, 40, 4)
      pygame.draw.rect(window, (255, 0, 0), self.healthbar_bg)
      pygame.draw.rect(window, (0, 255, 0), self.healthbar_rect)

    #draw the character's weapon
    def spinny_gun(self):
      self.mx, self.my = pygame.mouse.get_pos()
      self.diffx = self.x - self.mx
      self.diffy = self.y - self.my
      if self.diffx == 0:
        self.diffx += 0.00000001
      self.angle = -math.atan(self.diffy / self.diffx)
      self.angle = (self.angle * 180) / math.pi
      if current_gun == "Assault Rifle":
        if self.mx < self.x:
          blitRotate(window, ak_gun_flipped, (self.x + 4, self.y + 25), (30, 10), self.angle)
        else:
          blitRotate(window, ak_gun, (self.x + 16, self.y + 25), (30, 10), self.angle)
      elif current_gun == "Shotgun":
        if self.mx < self.x:
          blitRotate(window, shoot_gun_flipped, (self.x + 4, self.y + 25), (30, 10), self.angle)
        else:
          blitRotate(window, shoot_gun, (self.x + 16, self.y + 25), (30, 10), self.angle)
      elif current_gun == "Rocket Launcher":
        if self.mx < self.x:
          blitRotate(window, rocket_launcher_flipped, (self.x + 4, self.y + 25), (30, 10), self.angle)
        else:
          blitRotate(window, rocket_launcher, (self.x + 16, self.y + 25), (30, 10), self.angle)

    #draw the character and spawn enemies occasionally
    def draw(self):
      if self.x > 700:
        self.x = 700
      elif self.x < 0:
        self.x = 0
      
      if self.y < 0:
        self.y = 0
      elif self.y > 680:
        self.y = 680
      self.rect = pygame.rect.Rect(self.x, self.y, 20, 40)
      window.blit(player_skin, (self.x, self.y))
      self.spinny_gun()
      self.healthbar()
      self.enemy_spawn_timer -= 1
      if self.enemy_spawn_timer < 1:
        enemies.append(Enemy())
        self.enemy_spawn_timer = random.randint(8, 40)
      self.bullets_fired = 1 if current_gun == "Assault Rifle" else 16
    
    #change player's position
    def move(self, speedx, speedy):
      self.x += speedx
      self.y += speedy

    #create bullets
    def shoot(self):
      self.mx, self.my = pygame.mouse.get_pos()
      for i in range(self.bullets_fired):
        bullets.append(Bullet(self.x, self.y, self.mx, self.my))
      if current_gun == "Assault Rifle":
        pygame.mixer.Sound.play(assault_rifle_fired)
      elif current_gun == "Shotgun":
        pygame.mixer.Sound.play(shotgun_fired)

  #bullet class
  class Bullet(pygame.sprite.Sprite):
    #init method, also calculates the bullet's direction
    def __init__(self, x, y, mx, my):
      if current_gun == "Assault Rifle":
        self.wobble = random.uniform(-0.1, 0.1)
      elif current_gun == "Shotgun":
        self.wobble = random.uniform(-0.5, 0.5)
      elif current_gun == "Rocket Launcher":
        self.wobble = 0

      self.mousex = mx
      self.mousey = my
      self.aim_offset = 0
      if self.mousex > x:
        self.aim_offset = 14
      self.x = x + self.aim_offset
      self.y = y + 20
      self.negative = 1
      if self.mousex > self.x:
        self.negative = -1
      self.diffx = self.x - self.mousex
      self.diffy = self.y - self.mousey
      if self.diffx == 0:
        self.diffx += 0.00000001
      self.angle = math.atan(self.diffy / self.diffx) + self.wobble
      if current_gun == "Rocket Launcher":
        self.rect = pygame.rect.Rect(self.x, self.y, 30, 10)
      else:
        self.rect = pygame.rect.Rect(self.x, self.y, 20, 10)
      
      self.flipped = True if self.mousex > self.x else False
      if current_gun == "Rocket Launcher":
        self.explode_rect = pygame.rect.Rect(self.x, self.y, 50, 50)
        self.explode_rect.center = (self.x, self.y)
      else:
        self.explode_rect = pygame.rect.Rect(self.x, self.y, 0, 0)
    
    #draw bullet and rotate the image to look like it is flying in that direction
    def draw(self):
      self.rect = pygame.rect.Rect(self.x, self.y, 20, 10)
      if current_gun == "Rocket Launcher":
        if self.flipped:
          blitRotate(window, rocket_skin, (self.x, self.y), (10, 5), -self.angle * 180 / math.pi)
        else:
          blitRotate(window, pygame.transform.flip(rocket_skin, True, False), (self.x, self.y), (10, 5), -self.angle * 180 / math.pi)
      #other guns
      else:
        if self.flipped:
          blitRotate(window, bullet_skin, (self.x, self.y), (10, 5), -self.angle * 180 / math.pi)
        else:
          blitRotate(window, pygame.transform.flip(bullet_skin, True, False), (self.x, self.y), (10, 5), -self.angle * 180 / math.pi)
      #calculate the positions
      self.x -= math.cos(self.angle) * bullet_speed * self.negative
      self.y -= math.sin(self.angle) * bullet_speed * self.negative

  #enemy class
  class Enemy(pygame.sprite.Sprite):
    #init method
    def __init__(self):
      #pick a random position on any side to spawn at
      self.side = random.randint(0, 3)
      if self.side == 0:
        self.s_x_max = 1
        self.s_x_min = 0
        self.s_y_max = 700
        self.s_y_min = 0
      elif self.side == 1:
        self.s_x_max = 700
        self.s_x_min = 0
        self.s_y_max = 1
        self.s_y_min = 0
      elif self.side == 2:
        self.s_x_max = 700
        self.s_x_min = 699
        self.s_y_max = 700
        self.s_y_min = 0
      elif self.side == 3:
        self.s_x_max = 700
        self.s_x_min = 0
        self.s_y_max = 700
        self.s_y_min = 699

      #spawn and set some variables
      self.x = random.randint(self.s_x_min, self.s_x_max)
      self.y = random.randint(self.s_y_min, self.s_y_max)
      self.move_speed = enemy_speed + random.uniform(0, 1)
      self.rect = pygame.rect.Rect(self.x, self.y, 20, 20)
      self.health = 4
    
    #move the enemy and calculate which direction it is going
    def move(self, playerx, playery):
      self.playerx = player.x
      self.playery = player.y

      self.negative = 1
      if self.playerx < self.x:
        self.negative = - 1
      self.diffx = self.x - self.playerx
      self.diffy = self.y - self.playery
      if self.diffx == 0:
        self.diffx += 0.000001
      self.angle = math.atan(self.diffy / self.diffx)
      self.x += math.cos(self.angle) * self.move_speed * self.negative
      self.y += math.sin(self.angle) * self.move_speed * self.negative

    #draw the enemies' healthbar if they are damaged
    def healthbar(self):
      self.healthbar_rect = pygame.rect.Rect(self.x - 7, self.y - 10, self.health * 8 + 1, 4)
      self.healthbar_bg = pygame.rect.Rect(self.x - 7, self.y - 10, 33, 4)
      if self.health < 4:
        pygame.draw.rect(window, (255, 0, 0), self.healthbar_bg)
        pygame.draw.rect(window, (0, 255, 0), self.healthbar_rect)
    
    #draw the enemy
    def draw(self):
      self.rect = pygame.rect.Rect(self.x, self.y, 20, 20)
      pygame.draw.rect(window, (255, 0, 0), self.rect)
      self.healthbar()

  class Button(pygame.sprite.Sprite):
    def __init__(self, font_size, button_size, button_xy, button_text):
      self.b_font = pygame.font.Font("slkscr.ttf", font_size)
      self.text = self.b_font.render(button_text, True, (255, 255, 255))
      self.text_rect = self.text.get_rect()
      self.text_rect.center = button_xy
      self.b_rect = pygame.rect.Rect(button_xy, button_size)
      self.b_rect.center = button_xy
      self.color = (100, 100, 100)
      self.collide = False

    def draw_button(self):
      pygame.draw.rect(window, self.color, self.b_rect)
      window.blit(self.text, self.text_rect)

    def mouse_over(self, mxy):
      if self.b_rect.collidepoint((mxy)):
        self.color = (150, 150, 150)
        self.collide = True
      else:
        self.color = (100, 100, 100)
        self.collide = False

  def render_text(text, size, xy):
    temp_font = pygame.font.Font("slkscr.ttf", size)
    temp_text = temp_font.render(f"{text}", True, (255, 100, 0))
    temp_rect = temp_text.get_rect()
    temp_rect.topleft = xy
    window.blit(temp_text, temp_rect)

  def render_menu_text(text, size, xy):
    temp_font = pygame.font.Font("slkscr.ttf", size)
    temp_text = temp_font.render(f"{text}", True, (255, 255, 255))
    temp_rect = temp_text.get_rect()
    temp_rect.center = xy
    window.blit(temp_text, temp_rect)

  return_button = Button(24, (100, 30), (55, 700), "Return")
  #quit_button = Button(32, (500, 100), (360, 500), "Quit Game")
  start_button = Button(32, (500, 100), (360, 350), "Start Game")

  #creating a player object
  player = Player(w_width / 2 - 10, w_height / 2 - 20)
  speedx = 0
  speedy = 0
  time_passed = 0

  async def game_over_screen(time_passed):
    game_over = True
    while game_over:
      await asyncio.sleep(0)
      window.fill((0, 0, 0))
      pointx, pointy = pygame.mouse.get_pos()
      return_button.mouse_over((pointx, pointy))
      return_button.draw_button()
      render_menu_text("Game Over", 96, (360, 150))
      render_menu_text(f"Score: {score}", 24, (360, 300))
      render_menu_text(f"Bullets Fired: {bullets_hit + bullets_missed}", 24, (360, 350))
      if score / 5 == 0:
        render_menu_text(f"Enemies Killed: Zip. Zilch. Nada.", 24, (360, 400))
      else:
        render_menu_text(f"Enemies Killed: {int(score / 5)}", 24, (360, 400))

      if bullets_hit == 0:
        render_menu_text(f"Accuracy: Can't hit a barn if you were in it.", 24, (360, 450))
      else:
        render_menu_text(f"Accuracy: {math.floor(100 * 100 * bullets_hit / (bullets_hit + bullets_missed)) / 100}%", 24, (360, 450))
      
      if score / 5 == 0:
        render_menu_text(f"Bullets Per Enemy: Literally infinity.", 24, (360, 500))
      else:
        render_menu_text(f"Bullets Per Enemy: {math.floor(100*(bullets_hit + bullets_missed) / (score / 5)) / 100}", 24, (360, 500))

      render_menu_text(f"Time Passed: {time_passed / 1000} seconds", 24, (360, 550))
      pygame.display.update()
      for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN and return_button.collide:
          game_over = False
    time_passed = 0

  #start music
  pygame.mixer.music.set_volume(0.4)
  pygame.mixer.music.load("sfx/background_music.ogg")
  pygame.mixer.music.play(-1)

  running = True
  #game loop
  while running:
    await asyncio.sleep(0)
    game_running = False
    pointx, pointy = pygame.mouse.get_pos()
    window.fill((0, 0, 0))
    #quit_button.mouse_over((pointx, pointy))
    start_button.mouse_over((pointx, pointy))
    #quit_button.draw_button()
    start_button.draw_button()
    render_menu_text("Bullet Bob", 96, (360, 150))
    
    #get quit event and check for button presses
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        running = False
      if event.type == pygame.MOUSEBUTTONDOWN and start_button.collide:
        game_running = True
        window.fill((0, 0, 0))
        pygame.display.update()
        pygame.time.delay(500)
      #if event.type == pygame.MOUSEBUTTONDOWN and quit_button.collide:
      #  running = False

    #ingame loop, when you are playing
    while game_running:
      await asyncio.sleep(0)

      #get quit event
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          running = False
      
      if not running:
        break
      #say hello to my little friend
      if current_gun == "Assault Rifle":
        reload_max = 3
      elif current_gun == "Shotgun":
        reload_max = 30
      elif current_gun == "Rocket Launcher":
        reload_max = 50

      if pygame.mouse.get_pressed()[0] and reload < 1:
        reload = reload_max
        player.shoot()
      else:
        reload -= 1
      
      #movement controls
      keys = pygame.key.get_pressed()
      if keys[pygame.K_w] or keys[pygame.K_UP]:
        speedy = -5
      if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        speedy = 5
      if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        speedx = -5
      if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        speedx = 5
      if keys[pygame.K_1]:
        current_gun = "Assault Rifle"
      if keys[pygame.K_2]:
        current_gun = "Shotgun"
      #rocket launcher not working right now
      """
      if keys[pygame.K_3]:
        current_gun = "Rocket Launcher"
      """

      #check if enemies collide with the player
      for opposition in enemies:
        c_rect = player.rect
        op_rect = opposition.rect
        if c_rect.colliderect(op_rect):
          enemies.remove(opposition)
          player.health -= 5
          pygame.mixer.Sound.play(player_hurt_sound)

      #check if bullets collide with enemies
      for opponent in enemies:
        for projectile in bullets:
          p_rect = projectile.rect
          o_rect = opponent.rect
          if p_rect.colliderect(o_rect):
            opponent.health -= 1.5 if current_gun == "Assault Rifle" else 1
            bullets_hit += 1
            pygame.mixer.Sound.play(bullet_hit_sound)
            bullets.remove(projectile)

          #remove bullets that are offscreen
          if projectile.x < 0 or projectile.x > 720:
            if projectile in bullets:
              bullets.remove(projectile)
              bullets_missed += 1
          if projectile.y < 0 or projectile.y > 720:
            if projectile in bullets:
              bullets.remove(projectile)
              bullets_missed += 1
          elif opponent.health <= 0:
            if opponent in enemies:
              enemies.remove(opponent)
              pygame.mixer.Sound.play(enemy_death_sound)
              score += 5
      
      #game over, reset some variables
      if player.health <= 0:
        await game_over_screen(time_passed)
        game_running = False
        player.health = 100
        enemies = []
        bullets = []
        score = 0
        bullets_hit = 0
        bullets_missed = 0
        time_passed = 0
        player.x = w_width / 2 - 10
        player.y = w_height / 2 - 20
        break

      #draw the bullets and enemies
      window.fill((143, 150, 29))
      for b in bullets:
        b.draw()
      for e in enemies:
        e.move(px, py)
        e.draw()

      #draw the player and some other stuff
      player.draw()
      player.move(speedx, speedy)
      speedx = 0
      speedy = 0
      render_text(f"Score: {score}  Time: {math.floor(time_passed / 1000)} seconds", 16, (10, 10))
      pygame.display.update()
      pygame.time.delay(25)
      time_passed += 25

    pygame.display.update()
    pygame.time.delay(25)

asyncio.run(main())
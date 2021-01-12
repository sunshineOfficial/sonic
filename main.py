import os
import sys
import itertools
import pygame
from time import *

pygame.init()
pygame.display.set_caption('Sonic')
size = WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode(size)

FPS = 60
clock = pygame.time.Clock()
timer_spindash = 0
y_field = -250
x_field = -1000


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    pass


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def generate_level(level):
    new_player, x, y = None, None, None
    new_rings = []
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '*':
                Tile('spikes', x, y, tiles_group, all_sprites, spikes_group)
            elif level[y][x] == '#':
                Tile('ground', x, y, tiles_group, all_sprites, ground_group)
            elif level[y][x] == '%':
                Tile('underground', x, y, tiles_group, all_sprites, ground_group)
            elif level[y][x] == '&':
                new_rings.append(Ring(x, y))
            elif level[y][x] == '@':
                new_player = Player(x, y)

    return new_player, new_rings, x, y


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    max_width = max(map(len, level_map))

    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def screen_update():
    if not next_way_close:
        camera.update(player)
    for sprite in all_sprites:
        camera.apply(sprite)

    all_sprites.update()
    all_sprites.draw(screen)
    player_group.draw(screen)

    pygame.display.flip()


def image_ring_mainer(ring_count, rings):
    rings_images = []
    for elem in rings:
        for other in range(ring_count * 5):
            rings_images.append(elem)

    return rings_images


tile_images = {
    'ground': load_image('ground.png'),
    'underground': load_image('underground.png'),
    'empty': load_image('empty.png'),
    'spikes': load_image('spikes.png', colorkey=-1)
}

player_image = load_image('idle.png', colorkey=-1)
ghost_image = load_image('ghost.png')
ring_image = load_image('ring.png', colorkey=-1)
hurt_image = load_image('hurt.png', colorkey=-1)

running_player_images = [load_image('run_1.png', colorkey=-1), load_image('run_2.png', colorkey=-1),
                         load_image('run_3.png', colorkey=-1), load_image('run_4.png', colorkey=-1)]

jumping_player_images = [load_image('jump_1.png', colorkey=-1), load_image('jump_2.png', colorkey=-1),
                         load_image('jump_3.png', colorkey=-1), load_image('jump_4.png', colorkey=-1),
                         load_image('jump_5.png', colorkey=-1)]
spindash_player_images = [load_image('spindash.png', colorkey=-1), load_image('spindash_2.png', colorkey=-1),
                          load_image('spindash_3.png', colorkey=-1), load_image('spindash_4.png', colorkey=-1),
                          load_image('spindash_5.png', colorkey=-1), load_image('spindash_6.png', colorkey=-1)]

dust_spindash_player_images = []
dust = [load_image('dust.png', colorkey=-1), load_image('dust_2.png', colorkey=-1),
        load_image('dust_3.png', colorkey=-1), load_image('dust_4.png', colorkey=-1),
        load_image('dust_5.png', colorkey=-1), load_image('dust_6.png', colorkey=-1)]
for i in dust:
    for u in range(2):
        dust_spindash_player_images.append(i)

walking_player_images = []
walking = [load_image('walk.png', colorkey=-1), load_image('walk.png', colorkey=-1),
           load_image('walk_2.png', colorkey=-1), load_image('walk_2.png', colorkey=-1),
           load_image('walk_3.png', colorkey=-1), load_image('walk_3.png', colorkey=-1),
           load_image('walk_4.png', colorkey=-1), load_image('walk_4.png', colorkey=-1),
           load_image('walk_5.png', colorkey=-1), load_image('walk_5.png', colorkey=-1),
           load_image('walk_6.png', colorkey=-1), load_image('walk_6.png', colorkey=-1),
           load_image('walk_7.png', colorkey=-1), load_image('walk_7.png', colorkey=-1),
           load_image('walk_8.png', colorkey=-1), load_image('walk_8.png', colorkey=-1)]
for i in walking:
    for u in range(3):
        walking_player_images.append(i)

local_wall = load_image('thewall.png')

rings = [load_image('ring.png', colorkey=-1), load_image('ring_2.png', colorkey=-1),
         load_image('ring_3.png', colorkey=-1), load_image('ring_4.png', colorkey=-1)]

rings_sunshine = [load_image('ring_shine.png', colorkey=-1), load_image('ring_shine_2.png', colorkey=-1),
                  load_image('ring_shine_3.png', colorkey=-1), load_image('ring_shine_4.png', colorkey=-1)]

jump_cycle = itertools.cycle(jumping_player_images)
spindash_cycle = itertools.cycle(spindash_player_images)
walking_cycle = itertools.cycle(walking_player_images)
dust_cycle = itertools.cycle(dust_spindash_player_images)
run_cycle = itertools.cycle(running_player_images)

sound_ring = pygame.mixer.Sound("data/_music_/ring.wav")
sound_ring.set_volume(0.2)

sound_theme = pygame.mixer.Sound("data/_music_/mushroom_hill_act_1.flac")
sound_theme.set_volume(0.1)

sound_jump = pygame.mixer.Sound("data/_music_/jump.wav")
sound_jump.set_volume(0.2)

sound_crouch = pygame.mixer.Sound("data/_music_/crouch.wav")
sound_crouch.set_volume(0.2)

sound_lost_of_ring = pygame.mixer.Sound("data/_music_/lost_ring.wav")
sound_lost_of_ring.set_volume(0.2)

sound_spindash = pygame.mixer.Sound("data/_music_/sonic-spindash.mp3")
sound_spindash.set_volume(0.2)

tile_width = tile_height = 60


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, *args):
        super().__init__(*args)
        self.image = tile_images[tile_type]
        self.width = self.image.get_rect().width
        self.height = self.image.get_rect().height
        self.rect = self.image.get_rect().move(
            self.width * pos_x, self.height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.width = self.image.get_rect().width
        self.height = self.image.get_rect().height
        self.rect = self.image.get_rect().move(
            self.width * pos_x, (self.height * pos_y) + 80)

        self.speed = 1
        self.speed_y = 0
        self.gravity = 1
        self.counter = 0

        self.crouching = False
        self.running = False
        self.jumping = False
        self.damaged = False
        self.spindashing = False
        self.smart_crouching = False

    def move(self, key):
        global x_field, y_field
        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN] and keys[pygame.K_SPACE] and not self.jumping and not sonic_spin:
            self.spindashing = True

        elif (keys[pygame.K_DOWN] and keys[pygame.K_RIGHT]) or (keys[pygame.K_DOWN] and keys[pygame.K_LEFT]):
            pass

        elif key == pygame.K_DOWN and not self.jumping and not sonic_spin:
            sound_crouch.play()
            image_timer = 0
            self.crouching = True
            self.smart_crouching = False
            self.image = load_image('crouch.png', colorkey=-1)
            self.rect.y += 8
            if self.speed < 0:
                self.flip(self.image)
            screen.fill((0, 0, 0))
            screen.blit(local_wall, (x_field, y_field - 8))
            screen.blit(text2, (10, 30))
            screen_update()
            while image_timer < 1000000:
                image_timer += 1
            self.image = load_image('crouch_2.png', colorkey=-1)
            self.rect.y += 19
            if self.speed < 0:
                self.flip(self.image)
            self.smart_crouching = True
            y_field -= 19
        elif key == pygame.K_LEFT and not self.damaged:
            self.running = True
            self.speed = -1
        elif key == pygame.K_RIGHT and not self.damaged:
            self.running = True
            self.speed = 1
        if key == pygame.K_SPACE and not self.jumping and not self.crouching and not stop_jump:
            self.jumping = True
            sound_jump.play()
            self.speed_y = 15

    def flip(self, image):
        self.image = pygame.transform.flip(image, True, False)


class Ring(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = ring_image
        self.width = self.image.get_rect().width
        self.height = self.image.get_rect().height
        self.rect = self.image.get_rect().move(
            self.width * pos_x, (self.height * pos_y) + 60)


class Ghost(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group)
        self.image = ghost_image
        self.width = self.image.get_rect().width
        self.height = self.image.get_rect().height
        self.rect = self.image.get_rect().move(pos_x, pos_y)


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


if __name__ == '__main__':
    player = None
    rings_plain = None
    camera = Camera()

    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    ground_group = pygame.sprite.Group()
    spikes_group = pygame.sprite.Group()
    rings_group = pygame.sprite.Group()

    ghost_right = Ghost(615, 310)
    ghost_left = Ghost(600, 310)
    ghost_down = Ghost(608, 318)

    start_screen()

    try:
        player, rings_plain, level_x, level_y = generate_level(load_level('level.txt'))
    except FileNotFoundError:
        print('error')
        terminate()

    rings_cycle = itertools.cycle(image_ring_mainer(len(rings_plain), rings))
    sonic_spin = False
    stop_jump = False
    complete_ring = []
    shine_list = []
    timer_shine = []
    clock = pygame.time.Clock()
    f2 = pygame.font.Font('data/Pixel_font_sonic.ttf', 30)
    running = True
    next_way_close = False
    one_shift = False
    two_shift = False
    rest = False
    color = 'white'
    rest_timer = 0
    timer_dust = 0
    timer_walk = 0
    num_of_rings = 0
    sound_theme.play()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                player.move(event.key)
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT and not sonic_spin and not next_way_close:
                    player.running = False
                if event.key == pygame.K_DOWN and not sonic_spin:
                    if not next_way_close:
                        y_field = -250
                        player.rect.y -= 27
                        player.crouching = False
                    else:
                        one_shift = True
                if not next_way_close:
                    player.smart_crouching = False
                    player.spindashing = False
                    one_shift = False
                    two_shift = False
                if timer_spindash > 0:
                    if timer_spindash > 60:
                        pass
                    else:
                        player.rect.y -= 24
                timer_spindash = 0
                if player.spindashing and event.key == pygame.K_SPACE and not sonic_spin:
                    if not next_way_close:
                        player.spindashing = False
                    else:
                        two_shift = True
                if player.speed < 0:
                    player.flip(player_image)
                else:
                    player.image = player_image

        screen.fill((0, 0, 0))
        screen.blit(local_wall, (x_field, y_field))
        text2 = f2.render(f"RINGS:  {num_of_rings}", False, color)

        screen.blit(text2, (10, 25))

        changes_ring, num = False, None
        for i, elem in enumerate(rings_plain):  # Ring load
            elem.image = next(rings_cycle)
            if 650 > elem.rect.x > 590 and (elem.rect.y == 336 or elem.rect.y == 319 or elem.rect.y == 335):
                sound_ring.play()
                complete_ring.append(elem)
                timer_shine.append((elem, 0))
                del rings_plain[i]
                changes_ring = True
                num_of_rings += 1

        if changes_ring:
            shine_list.append(itertools.cycle(image_ring_mainer(1, rings_sunshine)))
            rings_cycle = itertools.cycle(image_ring_mainer(len(rings_plain), rings))

        for i, elem in enumerate(complete_ring):
            elem.image = next(shine_list[i])
            for t in range(len(timer_shine)):
                if timer_shine:
                    if timer_shine[t][0] == elem:
                        if timer_shine[t][1] > 45:
                            del complete_ring[i]
                            elem.image = ghost_image
                        else:
                            timer_shine[t] = (elem, timer_shine[t][1] + 1)

        if player.spindashing and player.smart_crouching and not next_way_close:
            if timer_spindash > 60:
                next_way_close = True
                sound_spindash.play()
                if timer_spindash == 61:
                    if player.speed > 0:
                        player.rect.x -= 43
                image = next(dust_cycle)
            else:
                image = next(spindash_cycle)
            player.image = image
            if player.speed < 0:
                player.flip(image)
            timer_spindash += 1

        elif player.spindashing and player.smart_crouching and next_way_close:
            if one_shift and two_shift:
                next_way_close = False
                sonic_spin = True
                field_speed = 7
                player.spindashing = False
                player.crouching = False
                walk_key = False
                finish_spin = False
                flag_spindash = 0
                spin_speed = 0
                timer_dust = 0
                timer_walk = 0
            else:
                timer_dust += 1
                if timer_dust % 2 == 0:
                    image = next(dust_cycle)
                player.image = image
                if player.speed < 0:
                    player.flip(image)

        if not next_way_close:
            if sonic_spin and not pygame.sprite.spritecollideany(ghost_right, spikes_group) \
                    and not pygame.sprite.spritecollideany(ghost_left, spikes_group) and \
                    not pygame.sprite.spritecollideany(ghost_down, spikes_group):
                if flag_spindash == 0:
                    player.rect.y -= 10
                if player.speed > 0 and spin_speed == 0:
                    spin_speed = 40
                if player.speed < 0 and spin_speed == 0:
                    spin_speed = -40
                if flag_spindash % 10 == 0:
                    field_speed -= 1
                if field_speed <= 0:
                    field_speed = 1
                player.rect.x += spin_speed
                if not finish_spin:
                    if spin_speed > 0:
                        x_field -= field_speed
                    else:
                        x_field += field_speed
                j_image = next(jump_cycle)
                player.image = j_image
                flag_spindash += 1
                if flag_spindash % 3 == 0 and not finish_spin:
                    if spin_speed > 0:
                        spin_speed -= 1
                    else:
                        spin_speed += 1

                if player.jumping and not stop_jump:
                    if not walk_key:
                        player.rect.y -= 16
                        y_field += 16
                        walk_key = True
                if not player.jumping and walk_key is True and pygame.sprite.spritecollideany(player, ground_group):
                    timer_walk += 1
                    esperate_timer = 0
                    while esperate_timer != 100000:
                        esperate_timer += 1
                    j_image = next(walking_cycle)
                    stop_jump = True
                    finish_spin = True
                    if timer_walk % 3 == 0:
                        if spin_speed > 0:
                            spin_speed -= 1
                        else:
                            spin_speed += 1
                        field_speed = 2
                        if spin_speed > 0:
                            x_field -= field_speed
                        else:
                            x_field += field_speed
                else:
                    j_image = next(jump_cycle)
                player.image = j_image
                if spin_speed < 0:
                    player.flip(j_image)
                if abs(spin_speed) == 1:
                    if not finish_spin:
                        player.rect.y -= 24
                    sonic_spin = False
                    player.image = player_image
                    if spin_speed < 0:
                        player.flip(player_image)
                    stop_jump = False
            elif sonic_spin and (pygame.sprite.spritecollideany(ghost_right, spikes_group)
                                 or pygame.sprite.spritecollideany(ghost_left, spikes_group)) \
                    and pygame.sprite.spritecollideany(player, ground_group):
                sonic_spin = False
                player.spindashing = False
                player.crouching = False
                finish_spin = False
                stop_jump = False
                player.rect.y -= 24
                player.image = j_image
                if player.speed < 0:
                    player.rect.x += 20
                    player.flip(j_image)
                else:
                    player.rect.x -= 20
                y_field = -240
                screen.blit(local_wall, (x_field, y_field))
                screen_update()

            elif sonic_spin and pygame.sprite.spritecollideany(ghost_down, spikes_group) and \
                    not pygame.sprite.spritecollideany(ghost_left, spikes_group) and \
                    not pygame.sprite.spritecollideany(ghost_right, spikes_group) and \
                    not pygame.sprite.spritecollideany(player, ground_group):
                sonic_spin = False

            if player.running and not player.jumping and not sonic_spin:
                color = 'white'
                if -10 < player.speed < 0:
                    if player.counter % 5 == 0:
                        player.speed -= 1
                    player.counter += 1

                elif 10 > player.speed > 0:
                    if player.counter % 5 == 0:
                        player.speed += 1
                    player.counter += 1
                else:
                    player.counter = 0

                if player.speed > 0 and not pygame.sprite.spritecollideany(ghost_right, spikes_group):
                    player.rect.x += player.speed
                elif player.speed < 0 and not pygame.sprite.spritecollideany(ghost_left, spikes_group):
                    player.rect.x += player.speed
                if not pygame.sprite.spritecollideany(ghost_left, spikes_group) and not pygame.sprite.spritecollideany(
                        ghost_right, spikes_group):
                    if player.speed > 0:
                        x_field -= 1
                    else:
                        x_field += 1
                if abs(player.speed) < 10:
                    image = next(walking_cycle)
                else:
                    image = next(run_cycle)

                player.image = image
                if player.speed < 0:
                    player.flip(image)
            elif player.running and player.jumping and not sonic_spin and not player.damaged:
                if player.speed > 0 and not pygame.sprite.spritecollideany(ghost_right, spikes_group):
                    player.rect.x += player.speed
                    if player.speed > 0:
                        x_field -= 1
                    else:
                        x_field += 1
                    if player.speed == 10:
                        player.rect.x += 3
                        x_field -= 1
                    if player.speed == -10:
                        player.rect.x -= 3
                        x_field += 1
                elif player.speed < 0 and not pygame.sprite.spritecollideany(ghost_left, spikes_group):
                    player.rect.x += player.speed
                    if player.speed > 0:
                        x_field -= 1
                    else:
                        x_field += 1
                    if player.speed == 10:
                        player.rect.x += 3
                        x_field -= 1
                    if player.speed == -10:
                        player.rect.x -= 3
                        x_field += 1

            if player.jumping or not pygame.sprite.spritecollideany(player, ground_group):
                player.rect.y -= player.speed_y
                player.speed_y -= player.gravity
                y_field += player.speed_y
                y_field += player.gravity
                j_image = next(jump_cycle)
                player.image = j_image
                if player.speed < 0:
                    player.flip(j_image)
                if player.speed_y < -15:
                    player.speed_y = -15
                if pygame.sprite.spritecollideany(player, ground_group):
                    player.speed_y = 0
                    player.jumping = False
                    if player.speed < 0:
                        player.flip(player_image)
                    else:
                        player.image = player_image
                    if player.damaged:
                        rest = True
                        rest_timer = 0
                    player.damaged = False

            if player.jumping and pygame.sprite.spritecollideany(ghost_down, spikes_group):
                player.speed_y = 15
                player.damaged = True
                color = 'red'
                sound_lost_of_ring.play()
                if num_of_rings > 1:
                    num_of_rings = 0

            if player.damaged:
                player.rect.x -= 5
                player.image = hurt_image

            if rest and rest_timer != 101:
                rest_timer += 1
                if int(str(rest_timer)[0]) % 2 == 0:
                    player.image = ghost_image
                else:
                    if not player.running and not player.jumping and not player.crouching:
                        player.image = player_image
            if rest_timer == 100:
                rest = False
                rest_timer = 0

            if not player.jumping and pygame.sprite.spritecollideany(ghost_down, ground_group) and \
                    not player.spindashing and not player.crouching and not sonic_spin:
                player.rect.y -= 1

        screen_update()
        clock.tick(FPS)
    pygame.quit()

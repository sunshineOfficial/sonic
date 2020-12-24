import os
import sys
import itertools
import pygame

pygame.init()
pygame.display.set_caption('Sonic')
size = WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode(size)

FPS = 60
clock = pygame.time.Clock()
timer_spindash = 0

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
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y, tiles_group, all_sprites)
            elif level[y][x] == '#':
                Tile('ground', x, y, tiles_group, all_sprites, ground_group)
            elif level[y][x] == '@':
                new_player = Player(x, y)
    return new_player, x, y


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    max_width = max(map(len, level_map))

    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def screen_update():
    camera.update(player)
    for sprite in all_sprites:
        camera.apply(sprite)

    all_sprites.update()
    all_sprites.draw(screen)
    player_group.draw(screen)

    pygame.display.flip()


tile_images = {
    'ground': load_image('ground.png'),
    'empty': load_image('empty.png')
}

player_image = load_image('idle.png', colorkey=-1)
running_player_images = [load_image('run_1.png', colorkey=-1), load_image('run_2.png', colorkey=-1),
                         load_image('run_3.png', colorkey=-1), load_image('run_4.png', colorkey=-1)]
run_cycle = itertools.cycle(running_player_images)

jumping_player_images = [load_image('jump_1.png', colorkey=-1), load_image('jump_2.png', colorkey=-1),
                         load_image('jump_3.png', colorkey=-1), load_image('jump_4.png', colorkey=-1),
                         load_image('jump_5.png', colorkey=-1)]
spindash_player_images = [load_image('spindash.png', colorkey=-1), load_image('spindash_2.png', colorkey=-1),
                         load_image('spindash_3.png', colorkey=-1), load_image('spindash_4.png', colorkey=-1),
                         load_image('spindash_5.png', colorkey=-1), load_image('spindash_6.png', colorkey=-1)]
walking_player_images = []
jump_cycle = itertools.cycle(jumping_player_images)
spindash_cycle = itertools.cycle(spindash_player_images)

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
            self.width * pos_x, self.height * pos_y)

        self.speed = 6
        self.speed_y = 0
        self.gravity = 1

        self.crouching = False
        self.running = False
        self.jumping = False
        self.spindashing = False
        self.smart_crouching = False

    def move(self, key):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN] and keys[pygame.K_SPACE] and not self.jumping:
            self.spindashing = True

        elif key == pygame.K_DOWN and not self.jumping:
            self.crouching = True
            self.smart_crouching = False
            self.image = load_image('crouch.png', colorkey=-1)
            self.rect.y += 8
            screen.fill((0, 0, 0))
            screen_update()
            pygame.time.wait(70)
            self.image = load_image('crouch_2.png', colorkey=-1)
            self.rect.y += 19
            self.smart_crouching = True
        elif key == pygame.K_LEFT:
            self.running = True
            self.speed = -6
        elif key == pygame.K_RIGHT:
            self.running = True
            self.speed = 6
        elif key == pygame.K_SPACE and not self.jumping:
            self.jumping = True
            self.speed_y = 15

    def flip(self, image):
        self.image = pygame.transform.flip(image, True, False)


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
    camera = Camera()

    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    ground_group = pygame.sprite.Group()

    start_screen()

    try:
        player, level_x, level_y = generate_level(load_level('level.txt'))
    except FileNotFoundError:
        print('error')
        terminate()
    sonic_spin = False
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                player.move(event.key)
            if event.type == pygame.KEYUP:
                player.running = False
                if player.crouching:
                    player.rect.y -= 27
                player.crouching = False
                player.smart_crouching = False
                if timer_spindash > 0:
                    if timer_spindash > 60:
                        sonic_spin = True
                        flag_spindash = 0
                        spin_speed = 0
                    else:
                        pass
                timer_spindash = 0
                if player.spindashing and event.key == pygame.K_SPACE:
                    player.spindashing = False
                if is_running_left:
                    player.flip(player_image)
                else:
                    player.image = player_image

        screen.fill((0, 0, 0))

        is_running_left = False
        if player.spindashing and player.smart_crouching:
            image = next(spindash_cycle)
            player.image = image
            timer_spindash += 1
        if sonic_spin:
            if flag_spindash == 0:
                player.rect.y += 24
            if player.speed > 0 and spin_speed == 0:
                spin_speed = 40
            if player.speed < 0 and spin_speed == 0:
                spin_speed = -40
            player.rect.x += spin_speed
            j_image = next(jump_cycle)
            player.image = j_image
            flag_spindash += 1
            if flag_spindash % 3 == 0:
                if spin_speed > 0:
                    spin_speed -= 1
                else:
                    spin_speed += 1

            if spin_speed == 0:
                sonic_spin = False
                player.rect.y -= 24


        if player.running and not player.jumping:
            player.rect.x += player.speed
            image = next(run_cycle)
            player.image = image
            if player.speed == -6:
                player.flip(image)
                is_running_left = True
            else:
                is_running_left = False

        if player.jumping or not pygame.sprite.spritecollideany(player, ground_group):
            player.rect.y -= player.speed_y
            player.speed_y -= player.gravity
            j_image = next(jump_cycle)
            player.image = j_image
            if player.speed_y < -15:
                player.speed_y = -15
            if pygame.sprite.spritecollideany(player, ground_group):
                player.speed_y = 0
                player.jumping = False
                player.image = player_image

        screen_update()
        clock.tick(FPS)
    pygame.quit()

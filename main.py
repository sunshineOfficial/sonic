import os
import sys

import pygame

pygame.init()
pygame.display.set_caption('Sonic')
size = WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode(size)

FPS = 60
clock = pygame.time.Clock()


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
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
    return new_player, x, y


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    max_width = max(map(len, level_map))

    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


tile_images = {}
player_image = load_image('sonic.png')

tile_width = tile_height = 60


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)

    def move(self, key):
        if key == pygame.K_UP:
            self.rect.y -= tile_height
        elif key == pygame.K_DOWN:
            self.rect.y += tile_height
        elif key == pygame.K_LEFT:
            self.rect.x -= tile_width
        elif key == pygame.K_RIGHT:
            self.rect.x += tile_width


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

    start_screen()

    try:
        player, level_x, level_y = generate_level(load_level('level.txt'))
    except FileNotFoundError:
        print('error')
        terminate()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                player.move(event.key)

        screen.fill((0, 0, 0))

        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)

        all_sprites.update()
        all_sprites.draw(screen)
        player_group.draw(screen)

        pygame.display.flip()
    pygame.quit()

import os
import sys
import itertools
import pygame
import random

# инициализация программы
pygame.init()
pygame.display.set_caption('Sonic')
size = WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode(size)
icon = pygame.image.load('data/images/sonic_ico.ico')
pygame.display.set_icon(icon)


FPS = 60
clock = pygame.time.Clock()
timer_spindash = 0
y_field = -250
x_field = -1000


# функция для закрытия игры
def terminate():
    pygame.quit()
    sys.exit()


# функция для поиска уровней в директории игры
def find_text_levels():
    global lost_files
    for i in range(3):
        if os.path.isfile(f'data/levels/level_{i + 1}.txt'):
            (sectors[i]).image = levels_image[i]
        else:
            (sectors[i]).image = none_table
            lost_files.append(i + 1)


# функция для загрузки изображений
def load_image(name, colorkey=None):
    fullname = os.path.join('data/images/', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    if name == 'background_main.png' or name == 'load_screen.png':
        image = pygame.image.load(fullname).convert()
    else:
        image = pygame.image.load(fullname)

    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


# функция для генерации уровня
def generate_level(level):
    new_player, x, y, flag, left_wall = None, None, None, None, None
    new_rings = []
    new_enemies = {
        'rhino': [],
        'buzzers': []
    }
    new_spikes = []

    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '*':
                new_spikes.append(Tile('spikes', x, y, tiles_group, all_sprites, spikes_group))
            elif level[y][x] == '#':
                Tile('ground', x, y, tiles_group, all_sprites, ground_group)
            elif level[y][x] == '%':
                Tile('underground', x, y, tiles_group, all_sprites, ground_group)
            elif level[y][x] == '5':
                flag = Flag(x)
            elif level[y][x] == '1':
                new_enemies['rhino'].append(Rhino(x, y))
            elif level[y][x] == '&':
                new_rings.append(Ring(x, y))
            elif level[y][x] == '@':
                new_player = Player(x, y)
            elif level[y][x] == '!':
                left_wall = BigLeftWall(x)
            elif level[y][x] == '^':
                new_enemies['buzzers'].append(Buzzer(x, y))

    return new_player, flag, left_wall, new_rings, new_enemies, new_spikes, x, y


# функция для загрузки уровня из файла
def load_level(filename):
    filename = "data/levels/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    max_width = max(map(len, level_map))

    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


# функция для обновления кадра
def screen_update(key):  # key используется по ситуации
    # ключ для уровня
    if key == 'level':
        if not next_way_close and player.lifes > 0 and not end_camera and not left_blocked:
            camera.update(player)
            for sprite in all_sprites:
                camera.apply(sprite)
        all_sprites.update()
        all_sprites.draw(screen)
        player_group.draw(screen)
        screen.blit(lifes_images[player.lifes], (20, 670))
        screen.blit(ring_text_image, (20, 50))
        pygame.display.flip()

    # ключ для вступительного меню
    if key == 'overlay':
        player_group.update()
        player_group.draw(screen)
        pygame.display.flip()

    # ключ для главного меню
    if key == 'save_menu':
        saves_group.update()
        saves_group.draw(screen)
        pygame.display.flip()

    # ключ для паузы
    if key == 'pause':
        all_sprites.draw(screen)
        screen.blit(black_rect_image, (0, 0))
        black_rect_image.set_alpha(150)
        pause_group.update()
        pause_group.draw(screen)
        screen.blit(text_pause, (525, 50))
        pygame.display.flip()

    # ключ для смерти и победы
    if key == 'death':
        all_sprites.draw(screen)
        black_rect_image.set_alpha(blackened)
        screen.blit(black_rect_image, (0, 0))

        if blackened >= 150 and end_camera:
            death_group.update()
            death_group.draw(screen)
            screen.blit(text_win, (425, 50))
        elif blackened > 255:
            death_group.update()
            death_group.draw(screen)
            screen.blit(text_game_over, (370, 50))

        button_select_red.rect.y = 320 + selection_death * 120
        pygame.display.flip()


# функция для синхронного вращения изображений с большим количеством носителей
def image_mainer(count, list):
    images = []
    for elem in list:
        for other in range(count * 5):
            images.append(elem)
    return images


# функция для проверки столкновений у rhino
def rhino_collision(enemy):
    for spike in spikes:
        if enemy.rect.x == spike.rect.x + 68:
            return 1

        if enemy.rect.x + 97 == spike.rect.x:
            return 2
    return 0


# загрузка изображений
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
sonic_main = load_image('main_title.png')
any_key = load_image('press_any_key.png')
load_segment = load_image('window_load.png')
load_segment_2 = load_image('window_load_menu_4.png')
load_segment_3 = load_image('window_load_menu_5.png')
red_load_segment = load_image('red_window_load.png')
red_square = load_image('red_square.png')
red_exit_square = load_image('red_square_exit.png')
data_select = load_image('data_select.png')
resume_button_image = load_image('resume_button.png')
restart_button_image = load_image('restart_button.png')
red_select_pause_image = load_image('red_select.png')
menu_button_image = load_image('menu_pause.png')
exit_button_image = load_image('exit_button_pause.png')
none_table = load_image('table_level_none.png')
back_image = load_image('back_image.png')
exit_image = load_image('exit_load_button.png')
black_rect_image = load_image('black_image_pause.png')
level_1_image = load_image('table_level_1.png')
level_2_image = load_image('table_level_2.png')
level_3_image = load_image('table_level_3.png')
left_wall_image = load_image('left_bold_wall.png', colorkey=-1)
levels_image = [level_1_image, level_2_image, level_3_image]
lifes_images = [load_image('lifes_1.png'), load_image('lifes_1.png'), load_image('lifes_2.png'),
                load_image('lifes_3.png')]
ring_text_image = load_image('rings_image.png')
death_image = load_image('death.png', colorkey=-1)
start_flag_image = load_image('flag.png')
finish_flag_image = load_image('flag_5.png')
ff = []
flags_other_images = [load_image('flag_2.png'), load_image('flag_3.png'), load_image('flag_4.png')]
for i in flags_other_images:
    for u in range(2):
        ff.append(i)
flags_cycle = itertools.cycle(ff)

buzzer_image = load_image('buzzer_1.png')
buzzer_image_2 = load_image('buzzer_2.png')
buzzer_image_3 = load_image('buzzer_3.png')
buzzer_image_4 = load_image('buzzer_4.png')
buzzer_main_list = [buzzer_image, buzzer_image_2, buzzer_image_3]

burn_image = load_image('burn_buzzer.png')
burn_image_2 = load_image('burn_buzzer_2.png')
burn_list = [burn_image, burn_image_2]
burn_cycle = itertools.cycle(burn_list)


hands = []
hand_images = [load_image('main_hand.png'), load_image('main_hand_2.png'),
               load_image('main_hand_3.png')]

face = []
half_face_images = [load_image('main_face.png'), load_image('main_face_2.png'),
                    load_image('main_face_3.png')]

button_list = []
buttons_images = [load_image('press_any_key_2.png'), load_image('press_any_key_3.png'),
                  load_image('press_any_key_4.png'), load_image('press_any_key_5.png'),
                  load_image('press_any_key_6.png'), load_image('press_any_key.png'),
                  load_image('press_any_key_6.png'), load_image('press_any_key_5.png'),
                  load_image('press_any_key_4.png'), load_image('press_any_key_3.png'),
                  load_image('press_any_key_2.png')]

for i in hand_images:
    for u in range(12):
        hands.append(i)
for i in half_face_images:
    for u in range(12):
        face.append(i)
for i in buttons_images:
    for u in range(12):
        button_list.append(i)

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

local_wall = load_image('the_wall.png')
local_overlay = load_image('background_main.png')
local_menu = load_image('load_screen.png')

rings = [load_image('ring.png', colorkey=-1), load_image('ring_2.png', colorkey=-1),
         load_image('ring_3.png', colorkey=-1), load_image('ring_4.png', colorkey=-1)]

rings_sunshine = [load_image('ring_shine.png', colorkey=-1), load_image('ring_shine_2.png', colorkey=-1),
                  load_image('ring_shine_3.png', colorkey=-1), load_image('ring_shine_4.png', colorkey=-1)]

rhino_image = load_image('rhino.png', colorkey=-1)

rhino_turn_images = [load_image('rhino_2.png', colorkey=-1), load_image('rhino_3.png', colorkey=-1),
                     load_image('rhino_4.png', colorkey=-1), load_image('rhino_5.png', colorkey=-1)]

# создание циклов для анимации изображений
jump_cycle = itertools.cycle(jumping_player_images)
spindash_cycle = itertools.cycle(spindash_player_images)
walking_cycle = itertools.cycle(walking_player_images)
dust_cycle = itertools.cycle(dust_spindash_player_images)
run_cycle = itertools.cycle(running_player_images)
hand_cycle = itertools.cycle(hands)
face_cycle = itertools.cycle(face)
button_cycle = itertools.cycle(button_list)

# загрузка звуковых файлов
sound_ring = pygame.mixer.Sound("data/music/ring.wav")
sound_ring.set_volume(0.2)

sound_theme = pygame.mixer.Sound("data/music/mushroom_hill_act_1.flac")
sound_theme.set_volume(0.1)

sound_jump = pygame.mixer.Sound("data/music/jump.wav")
sound_jump.set_volume(0.2)

sound_crouch = pygame.mixer.Sound("data/music/crouch.wav")
sound_crouch.set_volume(0.2)

sound_lost_of_ring = pygame.mixer.Sound("data/music/lost_ring.wav")
sound_lost_of_ring.set_volume(0.2)

sound_spindash = pygame.mixer.Sound("data/music/sonic_spindash.mp3")
sound_spindash.set_volume(0.2)

sound_overlay = pygame.mixer.Sound("data/music/title_screen.flac")
sound_overlay.set_volume(0.05)

sound_load_level_menu = pygame.mixer.Sound("data/music/theme.flac")
sound_load_level_menu.set_volume(0.2)

sound_death = pygame.mixer.Sound("data/music/death.mp3")
sound_death.set_volume(0.2)

sound_game_over = pygame.mixer.Sound("data/music/game_over.mp3")
sound_game_over.set_volume(0.2)

sound_stage_clear = pygame.mixer.Sound("data/music/stage_cleared.mp3")
sound_stage_clear.set_volume(0.2)

tile_width = tile_height = 60


# класс плитки
class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, *args):
        super().__init__(*args)
        self.image = tile_images[tile_type]
        self.width = self.image.get_rect().width
        self.height = self.image.get_rect().height
        if tile_type == 'spikes':
            self.rect = self.image.get_rect().move(
                35 * pos_x, self.height * pos_y + 20)
        else:
            self.rect = self.image.get_rect().move(
                self.width * pos_x, self.height * pos_y)


# класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.width = self.image.get_rect().width
        self.height = self.image.get_rect().height
        self.rect = self.image.get_rect().move(
            35 * pos_x, (self.height * pos_y) + 80)

        self.speed = 1
        self.speed_y = 0
        self.gravity = 1
        self.counter = 0
        self.lifes = 3

        self.bullet = []
        self.completely_buzz = []
        self.buzz_timer = 0
        self.damaged_from_fire = False

        self.crouching = False
        self.running = False
        self.main_crouching = False
        self.jumping = False
        self.damaged = False
        self.spindashing = False
        self.smart_crouching = False

    # функция для обработки нажатий
    def move(self, key):
        global x_field, y_field, pause, pause_timer, button_select_red, rotate, running, selection_death
        global rings_cycle, level_loaded_menu, player, rings_plain, enemies, spikes, level_x, level_y
        global num_of_rings, complete_ring, shine_list, timer_shine, next_way_close, one_shift
        global two_shift, rest, game_overlay, flag_exit, alpha_flag, exit_overlay, rest_timer, timer_spindash
        global camera, all_sprites, tiles_group, player_group, ground_group, spikes_group, rings_group, enemy_group
        global sector, sector_2, sector_3, sectors, lost_files, window_load_menu, window_load_menu_2
        global window_load_menu_3, back_segment, window_load_menu_4, window_load_menu_red, rotating, blackened
        global exited_data_select, overlay_flag, saves_flag, saves_group, saves_flag_2, segment_select, parameter
        global window_load_menu_5, exit_segment, flag_group, flag_of_end, end_camera, sonic_spin, left_wall
        global left_blocked, x_normale, y_normale, buzzers_group, buzzer_cycle, fire_group
        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN] and keys[pygame.K_SPACE] and not self.jumping and not sonic_spin and \
                not pygame.sprite.spritecollideany(ghost_right, spikes_group) \
                and not pygame.sprite.spritecollideany(ghost_left, spikes_group) and not pause:
            self.spindashing = True
        elif (keys[pygame.K_DOWN] and keys[pygame.K_RIGHT]) or (keys[pygame.K_DOWN] and keys[pygame.K_LEFT]):
            pass
        elif key == pygame.K_ESCAPE and pause:
            pause = False
            pygame.mixer.unpause()
            self.running = False
            self.rotate_pause = False
        elif key == pygame.K_ESCAPE:
            pause = True
            pause_timer = 0
            rotate = ''
            self.rotate_pause = False
            button_select_red.rect.y = 200
            self.selection_pause = 0
            pygame.mixer.pause()
        elif key == pygame.K_RETURN and pause:
            # продолжить игру
            if self.selection_pause == 0:
                pause = False
                pygame.mixer.unpause()
                self.running = False
                self.rotate_pause = False
            # выход из игры
            elif self.selection_pause == 3:
                running = False
            # рестарт уровня или выход в меню
            elif self.selection_pause == 1 or self.selection_pause == 2:
                pygame.mixer.unpause()
                sound_theme.stop()
                player = None
                rings_plain = None
                enemies = None
                spikes = None
                pause = False
                end_camera = False
                next_way_close = False
                sonic_spin = False
                left_blocked = False
                camera = Camera()
                all_sprites = pygame.sprite.Group()
                tiles_group = pygame.sprite.Group()
                player_group = pygame.sprite.Group()
                ground_group = pygame.sprite.Group()
                spikes_group = pygame.sprite.Group()
                rings_group = pygame.sprite.Group()
                enemy_group = pygame.sprite.Group()
                flag_group = pygame.sprite.Group()
                buzzers_group = pygame.sprite.Group()
                fire_group = pygame.sprite.Group()
                # если делаем рестарт
                if self.selection_pause == 1:
                    try:
                        player, flag_of_end, left_wall, rings_plain, enemies, spikes, level_x, level_y = generate_level(
                            load_level(file))
                    except FileNotFoundError:
                        print('error')
                        terminate()
                    rings_cycle = itertools.cycle(image_mainer(len(rings_plain), rings))
                    buzzer_cycle = itertools.cycle(image_mainer(len(enemies['buzzers']), buzzer_main_list))
                    level_loaded_menu = False
                    sound_load_level_menu.stop()
                    sound_theme.play()
                num_of_rings = 0
                rotate = 0
                timer_spindash = 0
                blackened = 0
                selection_death = 0
                y_field = -250
                x_field = -1000
                # если выходим в меню
                if self.selection_pause == 2:
                    saves_group = pygame.sprite.Group()
                    sound_load_level_menu.play()
                    game_overlay = False
                    level_loaded_menu = True
                    sector = Ghost(300, 72, saves_group)
                    sector_2 = Ghost(630, 72, saves_group)
                    sector_3 = Ghost(960, 72, saves_group)
                    sectors = [sector, sector_2, sector_3]
                    lost_files = []
                    find_text_levels()
                    window_load_menu = Ghost(300, 70, saves_group)
                    window_load_menu.image = load_segment
                    window_load_menu_2 = Ghost(630, 70, saves_group)
                    window_load_menu_2.image = load_segment
                    window_load_menu_3 = Ghost(960, 70, saves_group)
                    window_load_menu_3.image = load_segment
                    back_segment = Ghost(20, 70, saves_group)
                    back_segment.image = back_image
                    window_load_menu_4 = Ghost(10, 70, saves_group)
                    window_load_menu_4.image = load_segment_2
                    window_load_menu_5 = Ghost(10, 400, saves_group)
                    window_load_menu_5.image = load_segment_3
                    exit_segment = Ghost(0, 400, saves_group)
                    exit_segment.image = exit_image

                    window_load_menu_red = Ghost(320, 70, saves_group)
                    window_load_menu_red.image = red_load_segment

                    rotating = False
                    exited_data_select = False
                    overlay_flag = 0
                    saves_flag = 0
                    saves_flag_2 = 0
                    segment_select = 1
                    parameter = ''
                else:
                    level_loaded_menu = False
        elif key == pygame.K_DOWN and pause and self.selection_pause != 3:
            self.rotate_pause, rotate = True, 'down'
            self.selection_pause += 1
        elif key == pygame.K_UP and pause and self.selection_pause != 0:
            self.rotate_pause, rotate = True, 'up'
            self.selection_pause -= 1
        # приседанаие
        elif key == pygame.K_DOWN and not self.jumping and not sonic_spin and \
                not pause and not next_way_close:
            sound_crouch.play()
            image_timer = 0
            self.main_crouching = True
            self.crouching = True
            self.smart_crouching = False
            self.image = load_image('crouch.png', colorkey=-1)
            self.rect.y += 8
            if self.speed < 0:
                self.flip(self.image)
            screen.fill((0, 0, 0))
            if not left_blocked:
                screen.blit(local_wall, (x_field, y_field - 8))
            else:
                screen.blit(local_wall, (x_normale, y_normale))
            screen.blit(text2, (200, 38))
            screen_update('level')
            while image_timer < 1000000:
                image_timer += 1
            self.image = load_image('crouch_2.png', colorkey=-1)
            self.rect.y += 19
            if self.speed < 0:
                self.flip(self.image)
            self.smart_crouching = True
            y_field -= 19
        # бег влево
        elif key == pygame.K_LEFT and not self.damaged and not pause:
            self.running = True
            self.speed = -1
        # бег вправо
        elif key == pygame.K_RIGHT and not self.damaged and not pause:
            self.running = True
            self.speed = 1
        # прыжок
        if key == pygame.K_SPACE and not self.jumping and not self.crouching and \
                not stop_jump and not pause and not end_camera:
            self.jumping = True
            sound_jump.play()
            self.speed_y = 18

    # функция для отзеркаливания изображения
    def flip(self, image):
        self.image = pygame.transform.flip(image, True, False)


# класс колец
class Ring(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(all_sprites, rings_group)
        self.image = ring_image
        self.width = self.image.get_rect().width
        self.height = self.image.get_rect().height
        self.rect = self.image.get_rect().move(
            self.width * pos_x, (self.height * pos_y) + 60)


# летающие противники
class Buzzer(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(all_sprites, buzzers_group)
        self.image = buzzer_image
        self.width = self.image.get_rect().width
        self.height = self.image.get_rect().height
        self.rect = self.image.get_rect().move(
            35 * pos_x, -70)
        self.is_right = random.choice([True, False])
        self.speed_shoot = random.choice([i for i in range(50, 150)])
        self.ready_shoot = False
        self.ready_timer = 0

    def flip(self, image):
        self.image = pygame.transform.flip(image, True, False)


class FireBuzzer(pygame.sprite.Sprite):
    def __init__(self, pos_x, rotate):
        super().__init__(all_sprites, fire_group)
        self.image = burn_image
        if rotate:
            self.rect = self.image.get_rect().move(pos_x - 17, 210)
        else:
            self.rect = self.image.get_rect().move(pos_x + 55, 217)
        self.is_right = rotate

    def flip(self, image):
        self.image = pygame.transform.flip(image, True, False)


# класс финишной таблички
class Flag(pygame.sprite.Sprite):
    def __init__(self, pos_x):
        super().__init__(flag_group, all_sprites)
        self.image = start_flag_image
        self.rect = self.image.get_rect().move(pos_x * 35, 53)


# класс стены, котороя не дает пройти за пределы карты
class BigLeftWall(pygame.sprite.Sprite):
    def __init__(self, pos_x):
        super().__init__(flag_group, all_sprites)
        self.image = left_wall_image
        self.rect = self.image.get_rect().move(pos_x * 35, 53)


# универсальный невидимый класс без коллизии
class Ghost(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, *group):
        super().__init__(*group)
        self.image = ghost_image
        self.width = self.image.get_rect().width
        self.height = self.image.get_rect().height
        self.rect = self.image.get_rect().move(pos_x, pos_y)


# класс врага (rhino)
class Rhino(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(all_sprites, enemy_group)
        self.image = rhino_image
        self.width = self.image.get_rect().width
        self.height = self.image.get_rect().height
        self.rect = self.image.get_rect().move(35 * pos_x, self.height * pos_y + 40)

        self.x_offset = 0
        self.is_right = random.choice([True, False])
        self.is_turning = False
        self.turn_frame = 0

    def flip(self, image):
        self.image = pygame.transform.flip(image, True, False)


# класс камеры
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
    # подготовка к игре
    player = None
    rings_plain = None
    enemies = None
    spikes = None
    pause = False
    camera = Camera()

    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    ground_group = pygame.sprite.Group()
    spikes_group = pygame.sprite.Group()
    rings_group = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()
    saves_group = pygame.sprite.Group()
    flag_group = pygame.sprite.Group()
    pause_group = pygame.sprite.Group()
    death_group = pygame.sprite.Group()
    buzzers_group = pygame.sprite.Group()
    fire_group = pygame.sprite.Group()

    ghost_right = Ghost(615, 310, player_group)
    ghost_left = Ghost(600, 310, player_group)
    ghost_down = Ghost(608, 318, player_group)

    overlay_flag = 0
    sonic = Ghost(400, 100, player_group)
    hand = Ghost(664, 218, player_group)
    half_face = Ghost(520, 186, player_group)
    button = Ghost(450, 500, player_group)
    local_overlay = local_overlay.convert_alpha()
    sonic.image = sonic_main
    button.image = any_key
    hand.image = hand_images[0]
    half_face.image = half_face_images[0]

    local_menu = local_menu.convert_alpha()

    sonic_spin = False
    stop_jump = False
    black_flag = False
    complete_ring = []
    shine_list = []
    timer_shine = []
    clock = pygame.time.Clock()
    f2 = pygame.font.Font('data/fonts/Pixel_font_sonic.ttf', 29)
    f1 = pygame.font.Font('data/fonts/andes.ttf', 70)
    f3 = pygame.font.Font('data/fonts/andes.ttf', 150)
    running = True
    left_blocked = False
    next_way_close = False
    one_shift = False
    two_shift = False
    rest = False
    end_camera = False
    game_overlay = True
    exit_overlay = False
    flag_exit = 0
    alpha_flag = 0

    level_loaded_menu = False

    """pause parameters ------------------------------------"""
    button_resume = Ghost(500, 200, pause_group)
    button_resume.image = resume_button_image
    button_restart = Ghost(500, 320, pause_group, death_group)
    button_restart.image = restart_button_image
    button_menu = Ghost(500, 440, pause_group, death_group)
    button_menu.image = menu_button_image
    button_exit = Ghost(500, 560, pause_group, death_group)
    button_exit.image = exit_button_image
    button_select_red = Ghost(500, 200, pause_group, death_group)
    button_select_red.image = red_select_pause_image
    """end pause parameters --------------------------------"""

    color = 'yellow'
    rest_timer = 0
    timer_dust = 0
    timer_walk = 0
    num_of_rings = 0
    rotate = 0
    blackened = 0
    selection_death = 0
    death_timer = 0
    text_game_over = f3.render("game over", False, (200, 28, 28))
    text_win = f3.render("you win", False, (200, 28, 28))
    sound_overlay.play()

    # игровой цикл
    while running:
        for event in pygame.event.get():
            # вступительный экран
            if game_overlay:
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and alpha_flag >= 255:
                    exit_overlay = True

            # меню выбора уровня
            if level_loaded_menu:
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT and not rotating and segment_select != 3 and segment_select != -1 and \
                            segment_select != -2:
                        rotating = True
                        segment_select += 1
                        route = 'right'
                    if event.key == pygame.K_LEFT and not rotating and segment_select != 1 and segment_select != -1 and \
                            segment_select != -2:
                        rotating = True
                        segment_select -= 1
                        route = 'left'
                    if event.key == pygame.K_LEFT and not rotating and segment_select == 1:
                        rotating = True
                        segment_select -= 1
                        route = 'right_back'
                    if event.key == pygame.K_RIGHT and not rotating and segment_select == -1:
                        rotating = True
                        segment_select += 1
                        route = 'right_undo'
                    if event.key == pygame.K_DOWN and not rotating and segment_select == -1:
                        rotating = True
                        segment_select -= 1
                        route = 'down'
                    if event.key == pygame.K_UP and not rotating and segment_select == -2:
                        rotating = True
                        segment_select += 1
                        route = 'up'
                    if event.key == pygame.K_RIGHT and not rotating and segment_select == -2:
                        rotating = True
                        segment_select = 1
                        route = 'right_on_first'
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE and not rotating:
                        if lost_files:
                            for i in lost_files:
                                if i == segment_select:
                                    close = True
                                    break
                                else:
                                    close = False
                        else:
                            close = False
                        if not close:
                            if segment_select == -1:
                                exited_data_select = True
                            elif segment_select == -2:
                                running = False
                            else:
                                if segment_select == 1:
                                    file = 'level_1' + '.txt'
                                elif segment_select == 2:
                                    file = 'level_2' + '.txt'
                                elif segment_select == 3:
                                    file = 'level_3' + '.txt'
                                try:
                                    player, flag_of_end, left_wall, rings_plain, enemies, spikes, level_x, level_y = generate_level(
                                        load_level(file))
                                except FileNotFoundError:
                                    print('error')
                                    terminate()
                                rings_cycle = itertools.cycle(image_mainer(len(rings_plain), rings))
                                buzzer_cycle = itertools.cycle(image_mainer(len(enemies['buzzers']), buzzer_main_list))
                                level_loaded_menu = False
                                sound_load_level_menu.stop()
                                sound_theme.play()
            # игра
            elif not level_loaded_menu and not game_overlay:
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    # если игра не завершена
                    if player.lifes > 0 and not end_camera:
                        player.move(event.key)
                    else:
                        # выбор кнопки
                        if event.key == pygame.K_DOWN and selection_death < 2:
                            selection_death += 1
                        elif event.key == pygame.K_UP and selection_death > 0:
                            selection_death -= 1
                        elif event.key == pygame.K_RETURN:
                            # рестарт уровня или выход в меню
                            if selection_death == 0 or selection_death == 1:
                                sound_game_over.stop()
                                pygame.mixer.unpause()
                                sound_theme.stop()
                                player = None
                                rings_plain = None
                                enemies = None
                                spikes = None
                                pause = False

                                end_camera = False
                                left_blocked = False
                                next_way_close = False
                                camera = Camera()
                                all_sprites = pygame.sprite.Group()
                                tiles_group = pygame.sprite.Group()
                                player_group = pygame.sprite.Group()
                                ground_group = pygame.sprite.Group()
                                spikes_group = pygame.sprite.Group()
                                rings_group = pygame.sprite.Group()
                                enemy_group = pygame.sprite.Group()
                                flag_group = pygame.sprite.Group()
                                buzzers_group = pygame.sprite.Group()
                                fire_group = pygame.sprite.Group()
                                # если делаем рестарт
                                if selection_death == 0:
                                    try:
                                        player, flag_of_end, left_wall, rings_plain, enemies, spikes, level_x, level_y = generate_level(
                                            load_level(file))
                                    except FileNotFoundError:
                                        print('error')
                                        terminate()
                                    next_way_close = False
                                    end_camera = False
                                    rings_cycle = itertools.cycle(image_mainer(len(rings_plain), rings))
                                    buzzer_cycle = itertools.cycle(image_mainer(len(enemies['buzzers']), buzzer_main_list))
                                    level_loaded_menu = False
                                    sound_load_level_menu.stop()
                                    sound_theme.play()
                                num_of_rings = 0
                                rotate = 0
                                timer_spindash = 0
                                blackened = 0
                                y_field = -250
                                x_field = -1000
                                # если выходим в меню
                                if selection_death == 1:
                                    selection_death = 0
                                    saves_group = pygame.sprite.Group()
                                    sound_load_level_menu.play()
                                    game_overlay = False
                                    level_loaded_menu = True
                                    sector = Ghost(300, 72, saves_group)
                                    sector_2 = Ghost(630, 72, saves_group)
                                    sector_3 = Ghost(960, 72, saves_group)
                                    sectors = [sector, sector_2, sector_3]
                                    lost_files = []
                                    find_text_levels()
                                    window_load_menu = Ghost(300, 70, saves_group)
                                    window_load_menu.image = load_segment
                                    window_load_menu_2 = Ghost(630, 70, saves_group)
                                    window_load_menu_2.image = load_segment
                                    window_load_menu_3 = Ghost(960, 70, saves_group)
                                    window_load_menu_3.image = load_segment
                                    back_segment = Ghost(20, 70, saves_group)
                                    back_segment.image = back_image
                                    window_load_menu_4 = Ghost(10, 70, saves_group)
                                    window_load_menu_4.image = load_segment_2

                                    window_load_menu_5 = Ghost(10, 400, saves_group)
                                    window_load_menu_5.image = load_segment_3
                                    exit_segment = Ghost(0, 400, saves_group)
                                    exit_segment.image = exit_image

                                    window_load_menu_red = Ghost(320, 70, saves_group)
                                    window_load_menu_red.image = red_load_segment
                                    rotating = False
                                    exited_data_select = False
                                    overlay_flag = 0
                                    saves_flag = 0
                                    saves_flag_2 = 0
                                    segment_select = 1
                                    parameter = ''
                            else:
                                running = False
                if event.type == pygame.KEYUP and not pause and not end_camera:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT and \
                            not sonic_spin and not next_way_close and player.lifes > 0:
                        player.running = False
                    # приседанаие
                    if event.key == pygame.K_DOWN and not sonic_spin and \
                            not player.jumping and player.lifes > 0 and not player.running:
                        player.main_crouching = False
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
                    if not player.spindashing and event.key == pygame.K_SPACE and \
                            player.main_crouching and not sonic_spin and player.lifes > 0:
                        player.rect.y -= 20
                    # прыжок во время спиндеша
                    if player.spindashing and event.key == pygame.K_SPACE and \
                            not sonic_spin and player.lifes > 0:
                        if not next_way_close:
                            player.spindashing = False
                        else:
                            two_shift = True

                    # поворот игрока в ту сторону, в которую бежал
                    if player.speed < 0 and player.lifes > 0:
                        player.flip(player_image)
                    elif player.speed >= 0 and player.lifes > 0:
                        player.image = player_image

        # вступительный экран
        if game_overlay:
            overlay_flag += 1
            if 38 > overlay_flag > 0:
                half_face.image = next(face_cycle)
            if 158 > overlay_flag > 50:
                hand.image = next(hand_cycle)
            if overlay_flag == 200:
                overlay_flag = 0
            if overlay_flag % 5 == 0 and overlay_flag < 100 and not exit_overlay:
                button.rect.y += 1
            if overlay_flag % 5 == 0 and overlay_flag > 100 and not exit_overlay:
                button.rect.y -= 1
            if exit_overlay:
                flag_exit += 1
                button.rect.y += 15
                half_face.rect.y += 15
                hand.rect.y += 15
                sonic.rect.y += 15
            if flag_exit == 0 and alpha_flag < 255:
                local_overlay.set_alpha(alpha_flag)
                alpha_flag += 6
            elif flag_exit > 0:
                alpha_flag -= 6
                local_overlay.set_alpha(alpha_flag)
                if alpha_flag < 0:
                    sound_overlay.stop()
                    sound_load_level_menu.play()
                    button.image = ghost_image
                    sonic.image = ghost_image
                    hand.image = ghost_image
                    half_face.image = ghost_image
                    game_overlay = False
                    level_loaded_menu = True
                    sector = Ghost(300, 72, saves_group)
                    sector_2 = Ghost(630, 72, saves_group)
                    sector_3 = Ghost(960, 72, saves_group)
                    sectors = [sector, sector_2, sector_3]
                    lost_files = []
                    find_text_levels()
                    window_load_menu = Ghost(300, 70, saves_group)
                    window_load_menu.image = load_segment
                    window_load_menu_2 = Ghost(630, 70, saves_group)
                    window_load_menu_2.image = load_segment
                    window_load_menu_3 = Ghost(960, 70, saves_group)
                    window_load_menu_3.image = load_segment
                    back_segment = Ghost(20, 70, saves_group)
                    back_segment.image = back_image
                    window_load_menu_4 = Ghost(10, 70, saves_group)
                    window_load_menu_4.image = load_segment_2

                    window_load_menu_5 = Ghost(10, 400, saves_group)
                    window_load_menu_5.image = load_segment_3
                    exit_segment = Ghost(0, 400, saves_group)
                    exit_segment.image = exit_image

                    window_load_menu_red = Ghost(320, 70, saves_group)
                    window_load_menu_red.image = red_load_segment
                    rotating = False
                    exited_data_select = False
                    overlay_flag = 0
                    saves_flag = 0
                    saves_flag_2 = 0
                    segment_select = 1
                    parameter = ''

            screen.fill((0, 0, 0))
            button.image = next(button_cycle)
            screen.blit(local_overlay, (0, 0))
            screen_update('overlay')

        # меню выбора уровня
        if level_loaded_menu:
            saves_flag += 1
            saves_flag_2 += 1
            if saves_flag_2 == 104:
                saves_flag_2 = 0
            if saves_flag * 3 < 255:
                local_menu.set_alpha(saves_flag * 3)
            if saves_flag_2 % 8 == 0:
                window_load_menu_red.image = ghost_image
            elif saves_flag_2 % 4 == 0:
                if parameter == 'square':
                    window_load_menu_red.image = red_square
                elif parameter == 'exit_square':
                    window_load_menu_red.image = red_exit_square
                else:
                    window_load_menu_red.image = red_load_segment

            if rotating:
                if segment_select == 1:
                    x_task = 300
                elif segment_select == 2:
                    x_task = 630
                elif segment_select == 3:
                    x_task = 960
                elif segment_select == 0:
                    x_task = 290
                elif segment_select == -1:
                    x_task = 10
                elif segment_select == -2:
                    y_task = 400

            if rotating and route == 'right':
                if window_load_menu_red.rect.x != x_task + 20:
                    window_load_menu_red.rect.x += 10
                else:
                    rotating = False

            if rotating and route == 'left':
                if window_load_menu_red.rect.x != x_task + 20:
                    window_load_menu_red.rect.x -= 10
                else:
                    rotating = False

            if rotating and route == 'right_back':
                if window_load_menu_red.rect.x != x_task - 100 and x_task != 10:
                    window_load_menu_red.rect.x -= 10
                elif window_load_menu_red.rect.x == x_task - 100 and x_task != 10:
                    window_load_menu_red.image = red_square
                    parameter = 'square'
                    x_task = 10
                    segment_select = -1
                if window_load_menu_red.rect.x != x_task and x_task == 10:
                    window_load_menu_red.rect.x -= 10
                if window_load_menu_red.rect.x == x_task and x_task == 10:
                    rotating = False

            if rotating and route == 'right_undo':
                if window_load_menu_red.rect.x != x_task - 100 and x_task != 300:
                    window_load_menu_red.rect.x += 10
                elif window_load_menu_red.rect.x == x_task - 100 and x_task != 300:
                    window_load_menu_red.image = red_load_segment
                    parameter = ''
                    x_task = 300
                    segment_select = 1
                if window_load_menu_red.rect.x != x_task + 20 and x_task == 300:
                    window_load_menu_red.rect.x += 10
                if window_load_menu_red.rect.x == x_task + 20 and x_task == 300:
                    rotating = False

            if rotating and route == 'down':
                if window_load_menu_red.rect.y != y_task - 50 and parameter != 'exit_square':
                    window_load_menu_red.rect.y += 10
                elif window_load_menu_red.rect.y == y_task - 50 and parameter != 'exit_square':
                    window_load_menu_red.image = red_square
                    parameter = 'exit_square'
                    segment_select = -2
                if window_load_menu_red.rect.y != y_task and parameter == 'exit_square':
                    window_load_menu_red.rect.y += 10
                if window_load_menu_red.rect.y == y_task and parameter == 'exit_square':
                    rotating = False

            if rotating and route == 'up':
                if window_load_menu_red.rect.y != 120 and parameter != 'square':
                    window_load_menu_red.rect.y -= 10
                elif window_load_menu_red.rect.y == 120 and parameter != 'square':
                    window_load_menu_red.image = red_square
                    parameter = 'square'
                    segment_select = -1
                if window_load_menu_red.rect.y != 70 and parameter == 'square':
                    window_load_menu_red.rect.y -= 10
                if window_load_menu_red.rect.y == 70 and parameter == 'square':
                    rotating = False

            if rotating and route == 'right_on_first':
                if window_load_menu_red.rect.x != x_task + 20 and parameter != '':
                    window_load_menu_red.rect.x += 10
                elif window_load_menu_red.rect.x == x_task + 20 and parameter != '':
                    window_load_menu_red.image = red_square
                    parameter = ''
                    segment_select = 1
                if window_load_menu_red.rect.y != 70:
                    window_load_menu_red.rect.y -= 10
                if window_load_menu_red.rect.y == 70 and parameter == '':
                    rotating = False

            if exited_data_select:
                window_load_menu_red.image = ghost_image
                game_overlay = True
                exit_overlay = False
                pause = False
                flag_exit = 0
                alpha_flag = 0
                overlay_flag = 0
                sonic = Ghost(400, 100, player_group)
                hand = Ghost(664, 218, player_group)
                half_face = Ghost(520, 186, player_group)
                button = Ghost(450, 500, player_group)
                local_overlay = local_overlay.convert_alpha()
                sonic.image = sonic_main
                button.image = any_key
                hand.image = hand_images[0]
                half_face.image = half_face_images[0]
                level_loaded_menu = False
                sound_load_level_menu.stop()
                sound_overlay.play()

            screen.fill((0, 0, 0))
            screen.blit(local_menu, (0, 0))
            text2 = f1.render("data select", False, 'black')
            screen.blit(text2, (665, 660))
            screen_update('save_menu')
        # игра
        elif not game_overlay and not level_loaded_menu:
            if not pause:
                if not left_blocked:
                    screen.blit(local_wall, (x_field, y_field))
                else:
                    screen.blit(local_wall, (x_normale, y_normale))
                text2 = f2.render(str(num_of_rings), False, color)

                # собирание колец
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

                if player.lifes > 0:
                    # движение врага ('rhino')
                    for rhino in enemies['rhino']:
                        collision = rhino_collision(rhino)
                        if rhino.is_right:
                            if not rhino.is_turning:
                                rhino.flip(rhino_image)

                            if rhino.is_turning:
                                if rhino.turn_frame == 15:
                                    rhino.turn_frame = 0
                                    rhino.is_turning = False
                                else:
                                    rhino.turn_frame += 1
                                    r_image = rhino_turn_images[rhino.turn_frame // 5]
                                    rhino.image = r_image
                            elif rhino.x_offset < 200 and collision != 2:
                                rhino.rect.x += 1
                                rhino.x_offset += 1
                            elif (rhino.x_offset >= 200 and collision != 1) or collision == 2:
                                rhino.is_turning = True
                                rhino.is_right = False
                                rhino.rect.x -= 1
                                rhino.x_offset -= 1
                        else:
                            if not rhino.is_turning:
                                rhino.image = rhino_image

                            if rhino.is_turning:
                                if rhino.turn_frame == 15:
                                    rhino.turn_frame = 0
                                    rhino.is_turning = False
                                else:
                                    rhino.turn_frame += 1
                                    r_image = rhino_turn_images[rhino.turn_frame // 5]
                                    rhino.flip(r_image)
                            elif rhino.x_offset > -200 and collision != 1:
                                rhino.rect.x -= 1
                                rhino.x_offset -= 1
                            elif (rhino.x_offset <= -200 and collision != 2) or collision == 1:
                                rhino.is_right = True
                                rhino.is_turning = True
                                rhino.rect.x += 1
                                rhino.x_offset += 1

                changes_buzz = False
                player.buzz_timer += 1
                if player.lifes > 0:
                    for index, buzz in enumerate(enemies['buzzers']):
                        image_buzz = next(buzzer_cycle)
                        if buzz.is_right:
                            buzz.flip(image_buzz)
                            if player.buzz_timer < 500:
                                buzz.rect.x += 1
                        else:
                            buzz.image = image_buzz
                            if player.buzz_timer < 500:
                                buzz.rect.x -= 1
                        if player.buzz_timer == 500:
                            player.buzz_timer = 0
                            if buzz.is_right:
                                buzz.is_right = False
                            else:
                                buzz.is_right = True

                        if player.buzz_timer % buzz.speed_shoot == 0 and not buzz.ready_shoot:
                            buzz.ready_shoot = True
                            buzz.ready_timer = 0
                        if buzz.ready_shoot and buzz.ready_timer != 130:
                            image_buzz = buzzer_image_4
                            if buzz.is_right:
                                buzz.flip(image_buzz)
                            else:
                                buzz.image = image_buzz
                            buzz.ready_timer += 1
                        if buzz.ready_timer == 130:
                            buzz.ready_shoot = False
                            buzz.ready_timer = 0
                        if buzz.ready_timer == 100 and not player.jumping:
                            player.bullet.append(FireBuzzer(buzz.rect.x, buzz.is_right))

                        if 540 < buzz.rect.x < 660 and 320 < buzz.rect.y < 360:
                            buzz.image = ghost_image
                            sound_lost_of_ring.play()
                            player.speed_y = 10
                            player.completely_buzz.append(buzz)
                            del enemies['buzzers'][index]
                            changes_buzz = True

                    if changes_buzz:
                        buzzer_cycle = itertools.cycle(image_mainer(len(enemies['buzzers']), buzzer_main_list))

                    if player.damaged_from_fire:
                        player.damaged_from_fire = False

                    for index, fire in enumerate(player.bullet):
                        if pygame.sprite.spritecollideany(fire, player_group) and not player.damaged:
                            player.damaged = True
                            sound_lost_of_ring.play()
                            player.damaged_from_fire = True
                            player.jumping = True
                            player.speed_y = 15

                            if num_of_rings == 0 and player.lifes > 0:
                                player.lifes -= 1

                            if player.lifes == 0:
                                sound_theme.stop()
                                sound_death.play()
                                sound_game_over.play()
                                player.speed_y = 18
                                player.image = death_image

                            num_of_rings = 0

                            del player.bullet[index]

                        if fire.is_right:
                            fire.rect.x += 1
                            fire.rect.y += 1
                            if fire.rect.x % 8 == 0:
                                image_burn = next(burn_cycle)
                                fire.flip(image_burn)
                        else:
                            fire.rect.x -= 1
                            fire.rect.y += 1
                            if fire.rect.x % 8 == 0:
                                fire.image = next(burn_cycle)
                        if fire not in player.bullet:
                            fire.image = ghost_image
                        else:
                            if pygame.sprite.spritecollideany(fire, ground_group):
                                del player.bullet[index]
                                fire.image = ghost_image

                # если касаемся финишной таблички, то мы побеждаем
                if flag_of_end.rect.x < 610 and not end_camera:
                    sound_theme.stop()
                    sound_stage_clear.play()
                    end_camera = True
                    if sonic_spin:
                        player.rect.y -= 14
                        sonic_spin = False
                    next_way_close = True
                    num_flag = 0
                if end_camera and next_way_close:
                    if player.jumping or not pygame.sprite.spritecollideany(player, ground_group):
                        player.rect.y += 10
                        player.jumping = False


                    player.running = True
                    player.rect.x += 10
                    player.image = next(run_cycle)
                    if num_flag == 0:
                        flag_of_end.rect.x += 15
                    num_flag += 1
                    if num_flag < 100:
                        flag_of_end.image = next(flags_cycle)
                    if num_flag == 100:
                        black_flag = True
                        flag_of_end.rect.x -= 18
                        flag_of_end.image = finish_flag_image
                    if blackened < 150 and end_camera and black_flag:
                        blackened += 2

                # если собрали хотя бы одно кольцо
                if changes_ring:
                    shine_list.append(itertools.cycle(image_mainer(1, rings_sunshine)))
                    rings_cycle = itertools.cycle(image_mainer(len(rings_plain), rings))

                # удаление колец
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

                # разгон
                if player.spindashing and player.smart_crouching and \
                        not next_way_close and player.lifes > 0:
                    if timer_spindash > 60:
                        next_way_close = True
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
                elif player.spindashing and player.smart_crouching and \
                        next_way_close and player.lifes > 0:
                    if one_shift and two_shift:
                        sound_spindash.play()
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
                    # игрок катится
                    if sonic_spin and not pygame.sprite.spritecollideany(ghost_right, spikes_group) \
                            and not pygame.sprite.spritecollideany(ghost_left, spikes_group) and \
                            not pygame.sprite.spritecollideany(ghost_down, spikes_group) and \
                            player.lifes > 0:
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

                        if player.jumping and not stop_jump and player.lifes > 0:
                            if not walk_key:
                                player.rect.y -= 16
                                y_field += 16
                                walk_key = True

                        if not player.jumping and walk_key is True and \
                                pygame.sprite.spritecollideany(player, ground_group) and player.lifes > 0:
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
                    # столновение во время катания
                    elif sonic_spin and (pygame.sprite.spritecollideany(ghost_right, spikes_group)
                                         or pygame.sprite.spritecollideany(ghost_left, spikes_group)) \
                            and pygame.sprite.spritecollideany(player, ground_group) and player.lifes > 0:
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
                        screen_update('level')
                    elif sonic_spin and pygame.sprite.spritecollideany(ghost_down, spikes_group) and \
                            not pygame.sprite.spritecollideany(ghost_left, spikes_group) and \
                            not pygame.sprite.spritecollideany(ghost_right, spikes_group) and \
                            not pygame.sprite.spritecollideany(player, ground_group) and player.lifes > 0:
                        sonic_spin = False

                    # бег
                    if player.running and not player.jumping and not sonic_spin and player.lifes > 0:
                        if rest_timer == 1:
                            if player.speed > 0:
                                player.speed = 1
                            else:
                                player.speed = -1

                        color = 'yellow'
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
                        if not pygame.sprite.spritecollideany(ghost_left, spikes_group) and \
                                not pygame.sprite.spritecollideany(ghost_right, spikes_group):
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

                    # прыжок во время бега
                    elif player.running and player.jumping and not sonic_spin and \
                            not player.damaged and player.lifes > 0:
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

                    # прыжок
                    if player.jumping or not pygame.sprite.spritecollideany(player, ground_group):
                        player.rect.y -= player.speed_y
                        player.speed_y -= player.gravity
                        if player.lifes > 0:
                            y_field += player.speed_y
                            y_field += player.gravity
                            j_image = next(jump_cycle)
                            player.image = j_image
                        if player.speed < 0:
                            player.flip(j_image)
                        if player.speed_y < -18:
                            player.speed_y = -18

                        if pygame.sprite.spritecollideany(player, ground_group) and player.lifes > 0:
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
                            y_field = -250

                    # уничтожение врагов
                    if (player.jumping and pygame.sprite.spritecollideany(ghost_down, enemy_group) and
                        not player.damaged) or \
                            (sonic_spin and
                             (pygame.sprite.spritecollideany(ghost_left, enemy_group) or
                              pygame.sprite.spritecollideany(ghost_right, enemy_group))) and \
                            not player.damaged and player.lifes > 0:
                        for elem in enemies['rhino']:
                            if 650 > elem.rect.x > 520:
                                enemies['rhino'].remove(elem)
                                enemy_group.remove(elem)
                                elem.image = ghost_image
                                sound_lost_of_ring.play()
                                if player.jumping:
                                    player.speed_y = 18
                                break



                    # падение на шипы

                    if (player.jumping and pygame.sprite.spritecollideany(ghost_down, spikes_group) and
                        not player.damaged) or \
                            (not player.jumping and
                             pygame.sprite.spritecollideany(ghost_right, enemy_group) and
                             not player.damaged) and player.lifes > 0 and not player.damaged:
                        if not sonic_spin:
                            player.jumping = True
                            player.speed_y = 18
                            player.damaged = True

                            color = 'red'
                            sound_lost_of_ring.play()

                            if num_of_rings == 0 and player.lifes > 0:
                                player.lifes -= 1

                            if player.lifes == 0:
                                sound_theme.stop()
                                sound_death.play()
                                sound_game_over.play()
                                player.speed_y = 18
                                player.image = death_image

                            num_of_rings = 0

                    # игроку нанесён урон
                    if player.damaged and player.lifes > 0:
                        if pygame.sprite.spritecollideany(ghost_down, spikes_group):
                            player.speed_y = 15
                        if player.speed > 0:
                            player.rect.x -= 5
                            x_field += 1
                        else:
                            player.rect.x += 5
                            x_field -= 1
                        player.image = hurt_image

                    # выравнивание игрока по y
                    if not player.jumping and pygame.sprite.spritecollideany(ghost_down, ground_group) and \
                            not player.spindashing and not player.crouching and not sonic_spin and player.lifes > 0:
                        player.rect.y -= 1

                # если игрок жив
                if player.lifes > 0 and not end_camera:
                    screen.blit(text2, (200, 38))
                    screen_update('level')
                    screen.fill((0, 0, 0))
                else:
                    player.running = False
                    player.speed = 0

                    death_timer += 1
                    if death_timer % 16 == 0:
                        button_select_red.image = ghost_image
                    elif death_timer % 8 == 0:
                        button_select_red.image = red_select_pause_image

                    if blackened < 255 and not end_camera:
                        blackened += 2
                    screen_update('death')

                # остновка камеры, если рядом граница
                if left_wall.rect.x > 0 and not end_camera and not left_blocked and player.speed < 0:
                    left_blocked = True
                    x_normale = x_field
                    y_normale = y_field
                    if sonic_spin:
                        sonic_spin = False
                        player.speed = -1
                        image = player_image
                        player.flip(image)
                        player.image = image
                        player.rect.y -= 24
                        player.rect.x += 10

                # заблокировано
                if left_blocked:
                    if player.rect.x < 116:
                        if sonic_spin:
                            sonic_spin = False
                            player.rect.y -= 14
                            player.rect.x += 20
                            player.speed = 1
                            player.image = player_image
                        player.rect.x = 116
                    if player.rect.x > 608:
                        left_blocked = False
            else:
                pause_timer += 1
                if pause_timer % 16 == 0:
                    button_select_red.image = ghost_image
                elif pause_timer % 8 == 0:
                    button_select_red.image = red_select_pause_image

                if player.rotate_pause and rotate == 'down':
                    if button_select_red.rect.y != 200 + (player.selection_pause * 120):
                        button_select_red.rect.y += 20
                    else:
                        player.rotate_pause = False

                if player.rotate_pause and rotate == 'up':
                    if button_select_red.rect.y != 200 + (player.selection_pause * 120):
                        button_select_red.rect.y -= 20
                    else:
                        player.rotate_pause = False

                screen.blit(local_wall, (x_field, y_field))
                text_pause = f3.render("pause", False, (200, 28, 28))
                screen_update('pause')

        clock.tick(FPS)
    pygame.quit()

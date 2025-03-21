import pygame
import random
import math
import hashlib
import os

pygame.init()

# Получаем разрешение экрана
screen_info = pygame.display.Info()
GAME_CONFIG = {
    'WIDTH': screen_info.current_w,
    'HEIGHT': screen_info.current_h,
    'GRID_SIZE': 40,
    'INITIAL_RESOURCES': 50,
    'INITIAL_POPULATION': 100,
    'ARMY_COST': {'Infantry': {'resources': 10, 'population': 5},
                  'Cavalry': {'resources': 15, 'population': 7},
                  'Archers': {'resources': 12, 'population': 6}},
    'UPGRADE_COST': {'resources': 20, 'population': 0},
    'ATTACK_COST': 5,
    'RESOURCE_BASE': 1,
    'RESOURCE_PER_LEVEL': 1,
    'POPULATION_GROWTH': 2,
    'BOT_INTELLIGENCE': 0.9,
    'MAX_TROOPS': 50,
    'MAX_LEVEL': 5,
    'FORT_COST': {'resources': 30, 'population': 10},
    'FORT_DEFENSE_BONUS': 1.5,
    'CITY_COST': {'resources': 40, 'population': 15},
    'CITY_RESOURCE_BONUS': 2,
    'CITY_DEFENSE_BONUS': 1.2,
    'TOWER_COST': {'resources': 35, 'population': 12},
    'TOWER_DEFENSE_BONUS': 2.0,
    'EVENT_CHANCE': 0.15,
    'WALL_DENSITY': 0.1,
    'ATTACKS_PER_TURN_LIMIT': 3,
}

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 100, 100)
BLUE = (100, 100, 255)
GRAY = (200, 200, 220)
DARK_GRAY = (80, 80, 100)
LIGHT_GRAY = (230, 230, 250)
BROWN = (140, 90, 60)
PURPLE = (200, 120, 200)
ORANGE = (255, 180, 100)
CYAN = (100, 220, 220)
DARK_BLUE = (30, 30, 60)
YELLOW = (255, 240, 120)
GOLD = (255, 200, 0)
PINK = (255, 160, 160)

screen = pygame.display.set_mode((GAME_CONFIG['WIDTH'], GAME_CONFIG['HEIGHT']), pygame.FULLSCREEN)
pygame.display.set_caption("Война за территории")
font = pygame.font.Font(None, 32)
title_font = pygame.font.Font(None, 72)
small_font = pygame.font.Font(None, 24)
tiny_font = pygame.font.Font(None, 20)
button_font = pygame.font.Font(None, 28)

# Класс для территории
class Territory:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.owner = 0
        self.troops = {'Infantry': 0, 'Cavalry': 0, 'Archers': 0}
        self.resources = GAME_CONFIG['RESOURCE_BASE']
        self.population = 0
        self.level = 1
        self.buildings = []
        self.is_resource_boosted = False
        self.is_wall = False
        self.buff_debuff = None
        self.effect_timer = 0

# Создание карты
grid_width = GAME_CONFIG['WIDTH'] // GAME_CONFIG['GRID_SIZE'] - 6
grid_height = GAME_CONFIG['HEIGHT'] // GAME_CONFIG['GRID_SIZE']
territories = None

# Игровые состояния и переменные
MENU, SETTINGS, SEED_INPUT, PLAYING, GAME_OVER = 0, 1, 2, 3, 4
game_state = MENU
player_resources = GAME_CONFIG['INITIAL_RESOURCES']
player_population = GAME_CONFIG['INITIAL_POPULATION']
bot_resources = GAME_CONFIG['INITIAL_RESOURCES']
bot_population = GAME_CONFIG['INITIAL_POPULATION']
selected = None
event_message = ""
event_timer = 0
seed_input = ""
current_seed = None
hover_button = None
attacks = []
used_in_turn = set()
attacks_this_turn = 0
settings_input = None
turn_count = 0
effect_pulse = 0
cursor_blink = 0

BUFFS_DEBUFFS = {
    "resource_bonus": {"name": "Ресурсный бонус", "effect": lambda t: min(t.resources * 1.5, GAME_CONFIG['MAX_TROOPS']), "color": GOLD},
    "troop_bonus": {"name": "Бонус войск", "effect": lambda t: min(sum(t.troops.values()) * 1.2, GAME_CONFIG['MAX_TROOPS']), "color": YELLOW},
    "defense_bonus": {"name": "Бонус защиты", "effect": lambda t: min(sum(t.troops.values()) * 1.3 if t.owner else sum(t.troops.values()), GAME_CONFIG['MAX_TROOPS']), "color": CYAN},
    "resource_penalty": {"name": "Штраф ресурсов", "effect": lambda t: max(t.resources * 0.5, 0), "color": DARK_GRAY},
    "troop_penalty": {"name": "Штраф войск", "effect": lambda t: max(sum(t.troops.values()) * 0.8, 0), "color": BLACK},
    "population_bonus": {"name": "Рост населения", "effect": lambda t: t.population + 10, "color": PINK},
    "speed_boost": {"name": "Ускорение атак", "effect": lambda t: t, "color": ORANGE},
    "plague": {"name": "Чума", "effect": lambda t: max(t.population - 15, 0), "color": PURPLE}
}

def generate_map(seed):
    global territories, current_seed
    current_seed = seed
    territories = [[Territory(x, y) for y in range(grid_height)] for x in range(grid_width)]

    # Проверка, является ли сид именем файла в папке maps
    txt_seed = seed
    if not seed.endswith('.txt') and not os.path.exists(seed):
        txt_seed = os.path.join('maps/', seed + '.txt')
        if not os.path.exists(txt_seed):
            txt_seed = seed  # Если файла нет, используем как обычный сид
    if txt_seed.endswith('.txt') and os.path.exists(txt_seed):
        load_map_from_txt(txt_seed)
    else:
        random.seed(int(hashlib.sha256(seed.encode()).hexdigest(), 16))
        for x in range(grid_width):
            for y in range(grid_height):
                if random.random() < GAME_CONFIG['WALL_DENSITY'] and (x, y) not in [(0, 0), (grid_width - 1, grid_height - 1)]:
                    territories[x][y].is_wall = True
                if not territories[x][y].is_wall and random.random() < GAME_CONFIG['EVENT_CHANCE']:
                    territories[x][y].buff_debuff = random.choice(list(BUFFS_DEBUFFS.keys()))
                    territories[x][y].effect_timer = 180
        territories[0][0].owner = 1
        territories[0][0].troops['Infantry'] = 10
        territories[0][0].population = 20
        territories[0][0].is_wall = False
        territories[0][0].buff_debuff = None
        territories[grid_width - 1][grid_height - 1].owner = 2
        territories[grid_width - 1][grid_height - 1].troops['Infantry'] = 10
        territories[grid_width - 1][grid_height - 1].population = 20
        territories[grid_width - 1][grid_height - 1].is_wall = False
        territories[grid_width - 1][grid_height - 1].buff_debuff = None

def generate_preview_map(seed):
    random.seed(int(hashlib.sha256(seed.encode()).hexdigest(), 16))
    preview = [[Territory(x, y) for y in range(grid_height)] for x in range(grid_width)]
    txt_seed = seed
    if not seed.endswith('.txt') and not os.path.exists(seed):
        txt_seed = os.path.join('maps', seed + '.txt')
        if not os.path.exists(txt_seed):
            txt_seed = seed  # Если файла нет, используем как обычный сид
    if txt_seed.endswith('.txt') and os.path.exists(txt_seed):
        with open(txt_seed, 'r') as file:
            lines = file.readlines()
            for y, line in enumerate(lines[:grid_height]):
                for x, char in enumerate(line.strip()[:grid_width]):
                    if char == 'W':
                        preview[x][y].is_wall = True
                    elif char == 'P':
                        preview[x][y].owner = 1
                        preview[x][y].troops['Infantry'] = 10
                    elif char == 'B':
                        preview[x][y].owner = 2
                        preview[x][y].troops['Infantry'] = 10
    else:
        for x in range(grid_width):
            for y in range(grid_height):
                if random.random() < GAME_CONFIG['WALL_DENSITY'] and (x, y) not in [(0, 0), (grid_width - 1, grid_height - 1)]:
                    preview[x][y].is_wall = True
                if not preview[x][y].is_wall and random.random() < GAME_CONFIG['EVENT_CHANCE']:
                    preview[x][y].buff_debuff = random.choice(list(BUFFS_DEBUFFS.keys()))
        preview[0][0].owner = 1
        preview[0][0].troops['Infantry'] = 10
        preview[grid_width - 1][grid_height - 1].owner = 2
        preview[grid_width - 1][grid_height - 1].troops['Infantry'] = 10
    return preview

def load_map_from_txt(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
        for y, line in enumerate(lines[:grid_height]):
            for x, char in enumerate(line.strip()[:grid_width]):
                if char == 'W':
                    territories[x][y].is_wall = True
                elif char == 'P':
                    territories[x][y].owner = 1
                    territories[x][y].troops['Infantry'] = 10
                    territories[x][y].population = 20
                elif char == 'B':
                    territories[x][y].owner = 2
                    territories[x][y].troops['Infantry'] = 10
                    territories[x][y].population = 20
                elif char == 'F':
                    territories[x][y].buildings.append('fort')
                elif char == 'C':
                    territories[x][y].buildings.append('city')
                elif char == 'T':
                    territories[x][y].buildings.append('tower')
                elif char == 'R':
                    territories[x][y].buff_debuff = "resource_bonus"
                    territories[x][y].effect_timer = 180

def generate_preview_map(seed):
    random.seed(int(hashlib.sha256(seed.encode()).hexdigest(), 16))
    preview = [[Territory(x, y) for y in range(grid_height)] for x in range(grid_width)]
    txt_seed = "maps/" + seed + '.txt' if not seed.endswith('.txt') and os.path.exists(seed + '.txt') else seed
    if txt_seed.endswith('.txt') and os.path.exists(txt_seed):
        with open(txt_seed, 'r') as file:
            lines = file.readlines()
            for y, line in enumerate(lines[:grid_height]):
                for x, char in enumerate(line.strip()[:grid_width]):
                    if char == 'W':
                        preview[x][y].is_wall = True
                    elif char == 'P':
                        preview[x][y].owner = 1
                        preview[x][y].troops['Infantry'] = 10
                    elif char == 'B':
                        preview[x][y].owner = 2
                        preview[x][y].troops['Infantry'] = 10
    else:
        for x in range(grid_width):
            for y in range(grid_height):
                if random.random() < GAME_CONFIG['WALL_DENSITY'] and (x, y) not in [(0, 0), (grid_width - 1, grid_height - 1)]:
                    preview[x][y].is_wall = True
                if not preview[x][y].is_wall and random.random() < GAME_CONFIG['EVENT_CHANCE']:
                    preview[x][y].buff_debuff = random.choice(list(BUFFS_DEBUFFS.keys()))
        preview[0][0].owner = 1
        preview[0][0].troops['Infantry'] = 10
        preview[grid_width - 1][grid_height - 1].owner = 2
        preview[grid_width - 1][grid_height - 1].troops['Infantry'] = 10
    return preview

def draw_gradient(surface, rect, color1, color2):
    for y in range(rect.height):
        ratio = y / rect.height
        color = tuple(int(color1[i] + (color2[i] - color1[i]) * ratio) for i in range(3))
        pygame.draw.line(surface, color, (rect.x, rect.y + y), (rect.x + rect.width, rect.y + y))

def draw_map():
    global effect_pulse
    effect_pulse = (effect_pulse + 0.05) % (2 * math.pi)
    screen.fill(BLACK)  # Заполняем весь экран черным, убираем белое пространство
    for x in range(grid_width):
        for y in range(grid_height):
            rect = pygame.Rect(x * GAME_CONFIG['GRID_SIZE'], y * GAME_CONFIG['GRID_SIZE'],
                               GAME_CONFIG['GRID_SIZE'], GAME_CONFIG['GRID_SIZE'])
            if territories[x][y].is_wall:
                pygame.draw.rect(screen, BROWN, rect)
                pygame.draw.line(screen, DARK_GRAY, (rect.left + 5, rect.top + 5), (rect.right - 5, rect.bottom - 5), 2)
                pygame.draw.line(screen, DARK_GRAY, (rect.right - 5, rect.top + 5), (rect.left + 5, rect.bottom - 5), 2)
            else:
                base_color = GRAY if territories[x][y].owner == 0 else RED if territories[x][y].owner == 1 else BLUE
                end_color = [int(c * 0.7) for c in base_color]
                draw_gradient(screen, rect, base_color, end_color)
                pygame.draw.rect(screen, LIGHT_GRAY, rect, 1)

            for i, building in enumerate(territories[x][y].buildings):
                if building == 'fort':
                    pygame.draw.rect(screen, PURPLE, rect.inflate(-10 - i * 5, -10 - i * 5), 3)
                elif building == 'city':
                    pygame.draw.circle(screen, ORANGE, rect.center, 10 - i * 2, 3)
                elif building == 'tower':
                    pygame.draw.polygon(screen, CYAN,
                                        [(rect.centerx, rect.top + 5 + i * 5),
                                         (rect.left + 5 + i * 2, rect.bottom - 5 - i * 2),
                                         (rect.right - 5 - i * 2, rect.bottom - 5 - i * 2)], 3)

            if territories[x][y].buff_debuff and territories[x][y].effect_timer > 0:
                effect_color = BUFFS_DEBUFFS[territories[x][y].buff_debuff]["color"]
                alpha = int(100 + 50 * math.sin(effect_pulse))
                effect_surface = pygame.Surface((GAME_CONFIG['GRID_SIZE'], GAME_CONFIG['GRID_SIZE']), pygame.SRCALPHA)
                pygame.draw.circle(effect_surface, (*effect_color, alpha), (rect.width // 2, rect.height // 2), rect.width // 2)
                screen.blit(effect_surface, rect.topleft)
                territories[x][y].effect_timer -= 1

            if not territories[x][y].is_wall:
                total_troops = sum(territories[x][y].troops.values())
                if total_troops > 0:
                    troops_text = small_font.render(str(total_troops), True, YELLOW)
                    screen.blit(troops_text, (rect.centerx - troops_text.get_width() // 2,
                                              rect.centery - troops_text.get_height() // 2))

def draw_seed_preview(preview):
    preview_x = GAME_CONFIG['WIDTH'] // 2 - grid_width * GAME_CONFIG['GRID_SIZE'] // 2
    preview_y = GAME_CONFIG['HEIGHT'] // 2 - grid_height * GAME_CONFIG['GRID_SIZE'] // 2 + 50
    for x in range(grid_width):
        for y in range(grid_height):
            rect = pygame.Rect(preview_x + x * GAME_CONFIG['GRID_SIZE'], preview_y + y * GAME_CONFIG['GRID_SIZE'],
                               GAME_CONFIG['GRID_SIZE'], GAME_CONFIG['GRID_SIZE'])
            if preview[x][y].is_wall:
                pygame.draw.rect(screen, BROWN, rect)
            else:
                color = GRAY if preview[x][y].owner == 0 else RED if preview[x][y].owner == 1 else BLUE
                draw_gradient(screen, rect, color, [int(c * 0.7) for c in color])
            pygame.draw.rect(screen, BLACK, rect, 1)
            if preview[x][y].troops['Infantry'] > 0:
                troops_text = small_font.render(str(preview[x][y].troops['Infantry']), True, YELLOW)
                screen.blit(troops_text, (rect.x + 5, rect.y + 5))

def draw_settings():
    screen.fill(BLACK)
    title = title_font.render("Настройки", True, WHITE)
    screen.blit(title, (GAME_CONFIG['WIDTH'] // 2 - title.get_width() // 2, 50))

    settings_list = [
        ("Нач. ресурсы", 'INITIAL_RESOURCES', GAME_CONFIG['INITIAL_RESOURCES']),
        ("Нач. население", 'INITIAL_POPULATION', GAME_CONFIG['INITIAL_POPULATION']),
        ("Пехота (рес.)", 'ARMY_COST_Infantry_resources', GAME_CONFIG['ARMY_COST']['Infantry']['resources']),
        ("Пехота (нас.)", 'ARMY_COST_Infantry_population', GAME_CONFIG['ARMY_COST']['Infantry']['population']),
        ("Кавалерия (рес.)", 'ARMY_COST_Cavalry_resources', GAME_CONFIG['ARMY_COST']['Cavalry']['resources']),
        ("Кавалерия (нас.)", 'ARMY_COST_Cavalry_population', GAME_CONFIG['ARMY_COST']['Cavalry']['population']),
        ("Лучники (рес.)", 'ARMY_COST_Archers_resources', GAME_CONFIG['ARMY_COST']['Archers']['resources']),
        ("Лучники (нас.)", 'ARMY_COST_Archers_population', GAME_CONFIG['ARMY_COST']['Archers']['population']),
        ("Улучшение (рес.)", 'UPGRADE_COST_resources', GAME_CONFIG['UPGRADE_COST']['resources']),
        ("Стоимость атаки", 'ATTACK_COST', GAME_CONFIG['ATTACK_COST']),
        ("Базовые ресурсы", 'RESOURCE_BASE', GAME_CONFIG['RESOURCE_BASE']),
        ("Ресурсы за ур.", 'RESOURCE_PER_LEVEL', GAME_CONFIG['RESOURCE_PER_LEVEL']),
        ("Рост населения", 'POPULATION_GROWTH', GAME_CONFIG['POPULATION_GROWTH']),
        ("Интеллект бота", 'BOT_INTELLIGENCE', GAME_CONFIG['BOT_INTELLIGENCE']),
        ("Макс. войск", 'MAX_TROOPS', GAME_CONFIG['MAX_TROOPS']),
        ("Макс. уровень", 'MAX_LEVEL', GAME_CONFIG['MAX_LEVEL']),
        ("Форт (рес.)", 'FORT_COST_resources', GAME_CONFIG['FORT_COST']['resources']),
        ("Форт (нас.)", 'FORT_COST_population', GAME_CONFIG['FORT_COST']['population']),
        ("Бонус форта", 'FORT_DEFENSE_BONUS', GAME_CONFIG['FORT_DEFENSE_BONUS']),
        ("Город (рес.)", 'CITY_COST_resources', GAME_CONFIG['CITY_COST']['resources']),
        ("Город (нас.)", 'CITY_COST_population', GAME_CONFIG['CITY_COST']['population']),
        ("Ресурсы города", 'CITY_RESOURCE_BONUS', GAME_CONFIG['CITY_RESOURCE_BONUS']),
        ("Бонус города", 'CITY_DEFENSE_BONUS', GAME_CONFIG['CITY_DEFENSE_BONUS']),
        ("Башня (рес.)", 'TOWER_COST_resources', GAME_CONFIG['TOWER_COST']['resources']),
        ("Башня (нас.)", 'TOWER_COST_population', GAME_CONFIG['TOWER_COST']['population']),
        ("Бонус башни", 'TOWER_DEFENSE_BONUS', GAME_CONFIG['TOWER_DEFENSE_BONUS']),
        ("Шанс события", 'EVENT_CHANCE', GAME_CONFIG['EVENT_CHANCE']),
        ("Плотность стен", 'WALL_DENSITY', GAME_CONFIG['WALL_DENSITY']),
        ("Лимит атак", 'ATTACKS_PER_TURN_LIMIT', GAME_CONFIG['ATTACKS_PER_TURN_LIMIT']),
    ]

    y_offset = 120
    mouse_pos = pygame.mouse.get_pos()
    global hover_button, settings_input
    hover_button = None
    for i, (label, key, value) in enumerate(settings_list):
        text = tiny_font.render(f"{label}: {value}", True, WHITE)
        col = i % 2
        row = i // 2
        rect = pygame.Rect(GAME_CONFIG['WIDTH'] // 4 - 150 + col * 400, y_offset + row * 40, 300, 30)
        pygame.draw.rect(screen, GRAY if rect.collidepoint(mouse_pos) else DARK_GRAY, rect, border_radius=5)
        screen.blit(text, (rect.x + 10, rect.y + 5))
        if rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
            settings_input = key
    start_text = font.render("Нажмите ENTER для продолжения", True, YELLOW)
    screen.blit(start_text, (GAME_CONFIG['WIDTH'] // 2 - start_text.get_width() // 2, GAME_CONFIG['HEIGHT'] - 100))
    if settings_input:
        input_text = font.render(f"Введите новое значение для {settings_input}: {seed_input}", True, WHITE)
        screen.blit(input_text, (GAME_CONFIG['WIDTH'] // 2 - input_text.get_width() // 2, GAME_CONFIG['HEIGHT'] - 150))

def draw_ui():
    global hover_button
    ui_width = GAME_CONFIG['WIDTH'] - grid_width * GAME_CONFIG['GRID_SIZE']
    ui_rect = pygame.Rect(grid_width * GAME_CONFIG['GRID_SIZE'], 0, ui_width, GAME_CONFIG['HEIGHT'])
    draw_gradient(screen, ui_rect, DARK_BLUE, DARK_GRAY)

    total_income = sum(t.resources + (GAME_CONFIG['CITY_RESOURCE_BONUS'] if 'city' in t.buildings else 0)
                       for row in territories for t in row if t.owner == 1 and not t.is_wall)
    total_troops = sum(sum(t.troops.values()) for row in territories for t in row if t.owner == 1)
    total_territories = sum(1 for row in territories for t in row if t.owner == 1)
    total_population = sum(t.population for row in territories for t in row if t.owner == 1 and not t.is_wall)

    general_info = [
        ("Общая информация", font, WHITE),
        (f"Ресурсы: {player_resources}", small_font, WHITE),
        (f"Население: {player_population}", small_font, WHITE),
        (f"Доход: {total_income}/ход", small_font, WHITE),
        (f"Армия: {total_troops}", small_font, WHITE),
        (f"Территории: {total_territories}", small_font, WHITE),
        (f"Бот ресурсы: {bot_resources}", small_font, WHITE),
        (f"Бот население: {bot_population}", small_font, WHITE),
        (f"Сид: {current_seed}", small_font, WHITE),
        (f"Атак осталось: {GAME_CONFIG['ATTACKS_PER_TURN_LIMIT'] - attacks_this_turn}", small_font, WHITE),
        (f"Ходов: {turn_count}", small_font, WHITE),
        ("SPACE - завершить ход", small_font, YELLOW),
    ]
    y_offset = 10
    for text, text_font, color in general_info:
        surface = text_font.render(text, True, color)
        screen.blit(surface, (grid_width * GAME_CONFIG['GRID_SIZE'] + 10, y_offset))
        y_offset += text_font.get_height() + 5
    pygame.draw.line(screen, WHITE, (grid_width * GAME_CONFIG['GRID_SIZE'], y_offset),
                     (GAME_CONFIG['WIDTH'], y_offset), 2)

    if selected:
        x, y = selected
        terr = territories[x][y]
        owner_text = "Игрок" if terr.owner == 1 else "Бот" if terr.owner == 2 else "Нейтрально" if not terr.is_wall else "Стена"
        buff_debuff_text = BUFFS_DEBUFFS[terr.buff_debuff]["name"] if terr.buff_debuff else "Нет"

        info_texts = [
            ("Выбранная территория", font, WHITE),
            (f"Владелец: {owner_text}", small_font, WHITE),
            (f"Пехота: {terr.troops['Infantry']}", small_font, WHITE),
            (f"Кавалерия: {terr.troops['Cavalry']}", small_font, WHITE),
            (f"Лучники: {terr.troops['Archers']}", small_font, WHITE),
            (f"Ресурсы: {terr.resources}", small_font, WHITE),
            (f"Население: {terr.population}", small_font, WHITE),
            (f"Уровень: {terr.level}", small_font, WHITE),
            (f"Постройки: {', '.join(terr.buildings) if terr.buildings else 'Нет'}", small_font, WHITE),
            (f"Эффект: {buff_debuff_text}", small_font, WHITE),
        ]
        y_offset += 10
        for text, text_font, color in info_texts:
            surface = text_font.render(text, True, color)
            screen.blit(surface, (grid_width * GAME_CONFIG['GRID_SIZE'] + 10, y_offset))
            y_offset += text_font.get_height() + 5
        pygame.draw.line(screen, WHITE, (grid_width * GAME_CONFIG['GRID_SIZE'], y_offset),
                         (GAME_CONFIG['WIDTH'], y_offset), 2)

        buttons = [
            {"text": "Пехота (1)", "cost_res": GAME_CONFIG['ARMY_COST']['Infantry']['resources'], "cost_pop": GAME_CONFIG['ARMY_COST']['Infantry']['population'], "action": lambda: create_army(x, y, 'Infantry')},
            {"text": "Кавалерия (2)", "cost_res": GAME_CONFIG['ARMY_COST']['Cavalry']['resources'], "cost_pop": GAME_CONFIG['ARMY_COST']['Cavalry']['population'], "action": lambda: create_army(x, y, 'Cavalry')},
            {"text": "Лучники (3)", "cost_res": GAME_CONFIG['ARMY_COST']['Archers']['resources'], "cost_pop": GAME_CONFIG['ARMY_COST']['Archers']['population'], "action": lambda: create_army(x, y, 'Archers')},
            {"text": "Прокачать (4)", "cost_res": GAME_CONFIG['UPGRADE_COST']['resources'], "cost_pop": GAME_CONFIG['UPGRADE_COST']['population'], "action": lambda: upgrade_territory(x, y)},
            {"text": "Форт (5)", "cost_res": GAME_CONFIG['FORT_COST']['resources'], "cost_pop": GAME_CONFIG['FORT_COST']['population'], "action": lambda: build_structure(x, y, 'fort')},
            {"text": "Город (6)", "cost_res": GAME_CONFIG['CITY_COST']['resources'], "cost_pop": GAME_CONFIG['CITY_COST']['population'], "action": lambda: build_structure(x, y, 'city')},
            {"text": "Башня (7)", "cost_res": GAME_CONFIG['TOWER_COST']['resources'], "cost_pop": GAME_CONFIG['TOWER_COST']['population'], "action": lambda: build_structure(x, y, 'tower')},
        ]
        y_offset += 10
        mouse_pos = pygame.mouse.get_pos()
        hover_button = None
        for i, btn in enumerate(buttons):
            col = i % 2
            row = i // 2
            btn_rect = pygame.Rect(grid_width * GAME_CONFIG['GRID_SIZE'] + 10 + col * (ui_width // 2 - 10), y_offset + row * 45, ui_width // 2 - 20, 40)
            color = LIGHT_GRAY if btn_rect.collidepoint(mouse_pos) else GRAY
            pygame.draw.rect(screen, color, btn_rect, border_radius=5)
            pygame.draw.rect(screen, WHITE, btn_rect, 1, border_radius=5)
            text_surface = button_font.render(f"{btn['text']} - {btn['cost_res']}р/{btn['cost_pop']}н", True, WHITE)
            screen.blit(text_surface, (btn_rect.x + 10, btn_rect.y + 10))
            if btn_rect.collidepoint(mouse_pos):
                hover_button = btn['action']

    if event_message and event_timer > 0:
        alpha = min(255, event_timer * 4)
        event_surface = pygame.Surface((GAME_CONFIG['WIDTH'] // 2, 100), pygame.SRCALPHA)
        event_surface.fill((0, 0, 0, 100))
        event_text = font.render(event_message, True, YELLOW)
        event_text.set_alpha(alpha)
        event_surface.blit(event_text, (event_surface.get_width() // 2 - event_text.get_width() // 2, 50 - event_text.get_height() // 2))
        screen.blit(event_surface, (GAME_CONFIG['WIDTH'] // 4, GAME_CONFIG['HEIGHT'] // 2 - 50))

def simple_battle(attacker_troops, defender_troops, defender_buildings):
    atk_total = sum(attacker_troops.values()) * 1.5  # Увеличиваем силу атаки для баланса
    def_total = sum(defender_troops.values())
    if 'fort' in defender_buildings:
        def_total *= GAME_CONFIG['FORT_DEFENSE_BONUS']
    if 'city' in defender_buildings:
        def_total *= GAME_CONFIG['CITY_DEFENSE_BONUS']
    if 'tower' in defender_buildings:
        def_total *= GAME_CONFIG['TOWER_DEFENSE_BONUS']

    if atk_total > def_total:
        remaining = max(1, math.ceil(atk_total * 0.7))
        ratio = remaining / atk_total
        return True, {k: math.ceil(v * ratio) for k, v in attacker_troops.items()}
    else:
        return False, {'Infantry': 0, 'Cavalry': 0, 'Archers': 0}

def move_troops(from_x, from_y, to_x, to_y):
    if (abs(from_x - to_x) + abs(from_y - to_y) == 1 and
            territories[from_x][from_y].owner == 1 and
            territories[to_x][to_y].owner == 1 and
            not territories[to_x][to_y].is_wall and
            sum(territories[from_x][from_y].troops.values()) > 0):
        total_target = sum(territories[to_x][to_y].troops.values())
        if total_target + sum(territories[from_x][from_y].troops.values()) <= GAME_CONFIG['MAX_TROOPS']:
            territories[to_x][to_y].troops = {k: territories[to_x][to_y].troops[k] + territories[from_x][from_y].troops[k]
                                              for k in territories[from_x][from_y].troops}
            territories[to_x][to_y].population += territories[from_x][from_y].population
            territories[from_x][from_y].troops = {'Infantry': 0, 'Cavalry': 0, 'Archers': 0}
            territories[from_x][from_y].population = 0
            used_in_turn.add((from_x, from_y))
            return True
    return False

def attack(from_x, from_y, to_x, to_y, is_player=True):
    global player_resources, bot_resources, player_population, bot_population, attacks_this_turn
    resources = player_resources if is_player else bot_resources
    population = player_population if is_player else bot_population
    attack_limit = (GAME_CONFIG['ATTACKS_PER_TURN_LIMIT'] + 2 if territories[from_x][from_y].buff_debuff == "speed_boost" else GAME_CONFIG['ATTACKS_PER_TURN_LIMIT'])
    if (abs(from_x - to_x) + abs(from_y - to_y) == 1 and
            sum(territories[from_x][from_y].troops.values()) > 1 and
            not territories[to_x][to_y].is_wall and
            (from_x, from_y) not in used_in_turn):
        if is_player and territories[from_x][from_y].owner == 1 and territories[to_x][to_y].owner == 1:
            return move_troops(from_x, from_y, to_x, to_y)

        if (resources >= GAME_CONFIG['ATTACK_COST'] and
                attacks_this_turn < attack_limit):
            attacker_troops = {k: v for k, v in territories[from_x][from_y].troops.items()}
            defender_troops = territories[to_x][to_y].troops
            success, remaining_troops = simple_battle(attacker_troops, defender_troops, territories[to_x][to_y].buildings)
            if success:
                territories[to_x][to_y].owner = territories[from_x][from_y].owner
                territories[to_x][to_y].troops = remaining_troops
                territories[to_x][to_y].population = territories[from_x][from_y].population // 2
                territories[from_x][from_y].troops = {'Infantry': 0, 'Cavalry': 0, 'Archers': 0}
                territories[from_x][from_y].population = territories[from_x][from_y].population // 2
                # Постройки НЕ разрушаются при захвате
            else:
                territories[from_x][from_y].troops = {'Infantry': 0, 'Cavalry': 0, 'Archers': 0}
                territories[from_x][from_y].population = max(0, territories[from_x][from_y].population - 10)
            if is_player:
                player_resources -= GAME_CONFIG['ATTACK_COST']
            else:
                bot_resources -= GAME_CONFIG['ATTACK_COST']
            used_in_turn.add((from_x, from_y))
            attacks_this_turn += 1
            return True
    return False

def add_attack(from_x, from_y, to_x, to_y):
    if attack(from_x, from_y, to_x, to_y):
        if territories[from_x][from_y].owner != territories[to_x][to_y].owner:
            attacks.append((from_x, from_y, to_x, to_y))

def execute_turn():
    global attacks, used_in_turn, attacks_this_turn, turn_count
    attacks = []
    smart_bot_turn()
    collect_resources()
    used_in_turn.clear()
    attacks_this_turn = 0
    turn_count += 1

def create_army(x, y, army_type, is_player=True):
    global player_resources, bot_resources, player_population, bot_population
    resources = player_resources if is_player else bot_resources
    population = player_population if is_player else bot_population
    cost_res = GAME_CONFIG['ARMY_COST'][army_type]['resources']
    cost_pop = GAME_CONFIG['ARMY_COST'][army_type]['population']
    if (territories[x][y].owner == (1 if is_player else 2) and
            resources >= cost_res and population >= cost_pop and
            sum(territories[x][y].troops.values()) < GAME_CONFIG['MAX_TROOPS'] and
            territories[x][y].population >= cost_pop):
        territories[x][y].troops[army_type] = min(
            GAME_CONFIG['MAX_TROOPS'] - sum(territories[x][y].troops.values()) + territories[x][y].troops[army_type],
            territories[x][y].troops[army_type] + 5)
        if territories[x][y].buff_debuff:
            if territories[x][y].buff_debuff in ["resource_bonus", "troop_bonus", "defense_bonus", "resource_penalty", "troop_penalty"]:
                total = sum(territories[x][y].troops.values())
                new_total = int(BUFFS_DEBUFFS[territories[x][y].buff_debuff]["effect"](territories[x][y]))
                ratio = new_total / total if total > 0 else 0
                territories[x][y].troops = {k: min(int(v * ratio), GAME_CONFIG['MAX_TROOPS']) for k, v in territories[x][y].troops.items()}
            elif territories[x][y].buff_debuff == "population_bonus":
                territories[x][y].population = BUFFS_DEBUFFS[territories[x][y].buff_debuff]["effect"](territories[x][y])
        if is_player:
            player_resources -= cost_res
            player_population -= cost_pop
            territories[x][y].population -= cost_pop
        else:
            bot_resources -= cost_res
            bot_population -= cost_pop
            territories[x][y].population -= cost_pop

def upgrade_territory(x, y):
    global player_resources
    cost_res = GAME_CONFIG['UPGRADE_COST']['resources']
    if (territories[x][y].owner == 1 and
            player_resources >= cost_res and
            territories[x][y].level < GAME_CONFIG['MAX_LEVEL']):
        territories[x][y].level += 1
        territories[x][y].resources = (GAME_CONFIG['RESOURCE_BASE'] +
                                       GAME_CONFIG['RESOURCE_PER_LEVEL'] * (territories[x][y].level - 1))
        if territories[x][y].buff_debuff:
            if territories[x][y].buff_debuff in ["resource_bonus", "resource_penalty"]:
                territories[x][y].resources = int(BUFFS_DEBUFFS[territories[x][y].buff_debuff]["effect"](territories[x][y]))
        player_resources -= cost_res

def build_structure(x, y, structure_type):
    global player_resources, player_population
    cost_map = {'fort': GAME_CONFIG['FORT_COST'], 'city': GAME_CONFIG['CITY_COST'], 'tower': GAME_CONFIG['TOWER_COST']}
    cost_res = cost_map[structure_type]['resources']
    cost_pop = cost_map[structure_type]['population']
    if (territories[x][y].owner == 1 and
            structure_type not in territories[x][y].buildings and
            len(territories[x][y].buildings) < 2 and
            player_resources >= cost_res and player_population >= cost_pop and
            territories[x][y].population >= cost_pop):
        territories[x][y].buildings.append(structure_type)
        player_resources -= cost_res
        player_population -= cost_pop
        territories[x][y].population -= cost_pop
        if structure_type == 'city':
            territories[x][y].resources += GAME_CONFIG['CITY_RESOURCE_BONUS']

def smart_bot_turn():
    global bot_resources, bot_population, attacks_this_turn
    bot_resources += sum(t.resources + (GAME_CONFIG['CITY_RESOURCE_BONUS'] if 'city' in t.buildings else 0)
                         for row in territories for t in row if t.owner == 2 and not t.is_wall)
    bot_population += sum(GAME_CONFIG['POPULATION_GROWTH'] for row in territories for t in row if t.owner == 2 and not t.is_wall)
    for row in territories:
        for t in row:
            if t.owner == 2 and not t.is_wall:
                t.population += GAME_CONFIG['POPULATION_GROWTH']
                if t.buff_debuff == "population_bonus":
                    t.population = BUFFS_DEBUFFS["population_bonus"]["effect"](t)
                elif t.buff_debuff == "plague":
                    t.population = BUFFS_DEBUFFS["plague"]["effect"](t)
    bot_used_in_turn = set()
    bot_attacks = 0

    for x in range(grid_width):
        for y in range(grid_height):
            if territories[x][y].owner == 2:
                total_troops = sum(territories[x][y].troops.values())
                is_border = any(territories[nx][ny].owner == 1 for nx, ny in [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
                                if 0 <= nx < grid_width and 0 <= ny < grid_height)

                if (bot_resources >= min(c['resources'] for c in GAME_CONFIG['ARMY_COST'].values()) and
                        bot_population >= min(c['population'] for c in GAME_CONFIG['ARMY_COST'].values()) and
                        total_troops < GAME_CONFIG['MAX_TROOPS'] and
                        random.random() < GAME_CONFIG['BOT_INTELLIGENCE'] * 1.2):
                    army_type = random.choice(['Infantry', 'Cavalry', 'Archers'])
                    create_army(x, y, army_type, False)
                elif (territories[x][y].level < GAME_CONFIG['MAX_LEVEL'] and
                      bot_resources >= GAME_CONFIG['UPGRADE_COST']['resources'] and
                      random.random() < GAME_CONFIG['BOT_INTELLIGENCE'] * 0.8):
                    territories[x][y].level += 1
                    territories[x][y].resources = (GAME_CONFIG['RESOURCE_BASE'] +
                                                   GAME_CONFIG['RESOURCE_PER_LEVEL'] * (territories[x][y].level - 1))
                    if territories[x][y].buff_debuff:
                        if territories[x][y].buff_debuff in ["resource_bonus", "resource_penalty"]:
                            territories[x][y].resources = int(BUFFS_DEBUFFS[territories[x][y].buff_debuff]["effect"](territories[x][y]))
                    bot_resources -= GAME_CONFIG['UPGRADE_COST']['resources']
                elif (len(territories[x][y].buildings) < 2 and
                      bot_resources >= GAME_CONFIG['CITY_COST']['resources'] and bot_population >= GAME_CONFIG['CITY_COST']['population'] and
                      territories[x][y].population >= GAME_CONFIG['CITY_COST']['population'] and
                      'city' not in territories[x][y].buildings and
                      random.random() < GAME_CONFIG['BOT_INTELLIGENCE'] * 0.5):
                    territories[x][y].buildings.append('city')
                    territories[x][y].resources += GAME_CONFIG['CITY_RESOURCE_BONUS']
                    bot_resources -= GAME_CONFIG['CITY_COST']['resources']
                    bot_population -= GAME_CONFIG['CITY_COST']['population']
                    territories[x][y].population -= GAME_CONFIG['CITY_COST']['population']
                elif (len(territories[x][y].buildings) < 2 and
                      bot_resources >= GAME_CONFIG['TOWER_COST']['resources'] and bot_population >= GAME_CONFIG['TOWER_COST']['population'] and
                      territories[x][y].population >= GAME_CONFIG['TOWER_COST']['population'] and
                      'tower' not in territories[x][y].buildings and
                      is_border and random.random() < GAME_CONFIG['BOT_INTELLIGENCE'] * 0.7):
                    territories[x][y].buildings.append('tower')
                    bot_resources -= GAME_CONFIG['TOWER_COST']['resources']
                    bot_population -= GAME_CONFIG['TOWER_COST']['population']
                    territories[x][y].population -= GAME_CONFIG['TOWER_COST']['population']
                elif (len(territories[x][y].buildings) < 2 and
                      bot_resources >= GAME_CONFIG['FORT_COST']['resources'] and bot_population >= GAME_CONFIG['FORT_COST']['population'] and
                      territories[x][y].population >= GAME_CONFIG['FORT_COST']['population'] and
                      'fort' not in territories[x][y].buildings and
                      random.random() < GAME_CONFIG['BOT_INTELLIGENCE'] * 0.6):
                    territories[x][y].buildings.append('fort')
                    bot_resources -= GAME_CONFIG['FORT_COST']['resources']
                    bot_population -= GAME_CONFIG['FORT_COST']['population']
                    territories[x][y].population -= GAME_CONFIG['FORT_COST']['population']

    attack_options = []
    for x in range(grid_width):
        for y in range(grid_height):
            if territories[x][y].owner == 2 and sum(territories[x][y].troops.values()) > 1 and (x, y) not in bot_used_in_turn:
                directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    if (0 <= nx < grid_width and 0 <= ny < grid_height and
                            territories[nx][ny].owner != 2 and not territories[nx][ny].is_wall):
                        atk_total = sum(territories[x][y].troops.values())
                        def_total = sum(territories[nx][ny].troops.values())
                        if 'fort' in territories[nx][ny].buildings:
                            def_total *= GAME_CONFIG['FORT_DEFENSE_BONUS']
                        if 'city' in territories[nx][ny].buildings:
                            def_total *= GAME_CONFIG['CITY_DEFENSE_BONUS']
                        if 'tower' in territories[nx][ny].buildings:
                            def_total *= GAME_CONFIG['TOWER_DEFENSE_BONUS']
                        if atk_total > def_total * 1.2:
                            priority = (territories[nx][ny].resources * 2 +
                                        (10 if territories[nx][ny].owner == 1 else 0) +
                                        (3 if territories[nx][ny].buff_debuff in ["resource_bonus", "troop_bonus"] else 0))
                            attack_options.append((x, y, nx, ny, priority))
    attack_options.sort(key=lambda x: x[4], reverse=True)
    attack_limit = (GAME_CONFIG['ATTACKS_PER_TURN_LIMIT'] + 2 if any(t.buff_debuff == "speed_boost" for row in territories for t in row if t.owner == 2) else GAME_CONFIG['ATTACKS_PER_TURN_LIMIT'])
    while attack_options and bot_attacks < attack_limit and attacks_this_turn < attack_limit:
        from_x, from_y, to_x, to_y, _ = attack_options.pop(0)
        if attack(from_x, from_y, to_x, to_y, False):
            bot_used_in_turn.add((from_x, from_y))
            bot_attacks += 1
            attacks_this_turn += 1

def collect_resources():
    global player_resources, player_population
    player_resources += sum(t.resources + (GAME_CONFIG['CITY_RESOURCE_BONUS'] if 'city' in t.buildings else 0)
                            for row in territories for t in row if t.owner == 1 and not t.is_wall)
    player_population += sum(GAME_CONFIG['POPULATION_GROWTH'] for row in territories for t in row if t.owner == 1 and not t.is_wall)
    for row in territories:
        for t in row:
            if t.owner == 1 and not t.is_wall:
                t.population += GAME_CONFIG['POPULATION_GROWTH']
                if t.buff_debuff == "population_bonus":
                    t.population = BUFFS_DEBUFFS["population_bonus"]["effect"](t)
                elif t.buff_debuff == "plague":
                    t.population = BUFFS_DEBUFFS["plague"]["effect"](t)

def random_event():
    global player_resources, bot_resources, player_population, bot_population, event_message, event_timer
    if random.random() < GAME_CONFIG['EVENT_CHANCE']:
        event_type = random.randint(1, 10)
        if event_type == 1:
            x, y = random.randint(0, grid_width - 1), random.randint(0, grid_height - 1)
            if not territories[x][y].is_wall:
                territories[x][y].is_resource_boosted = True
                territories[x][y].resources = min(territories[x][y].resources * 2, GAME_CONFIG['MAX_TROOPS'])
                territories[x][y].buff_debuff = "resource_bonus"
                territories[x][y].effect_timer = 180
                event_message = f"Ресурсный бум на ({x}, {y})!"
        elif event_type == 2:
            x, y = random.randint(0, grid_width - 1), random.randint(0, grid_height - 1)
            if territories[x][y].owner != 0 and not territories[x][y].is_wall:
                total = sum(territories[x][y].troops.values())
                new_total = max(0, total // 2)
                ratio = new_total / total if total > 0 else 0
                territories[x][y].troops = {k: math.ceil(v * ratio) for k, v in territories[x][y].troops.items()}
                event_message = f"Восстание на ({x}, {y})!"
        elif event_type == 3:
            if random.random() < 0.5:
                player_resources += 20
                event_message = "Игрок получил подкрепление: +20 ресурсов!"
            else:
                bot_resources += 20
                event_message = "Бот получил подкрепление: +20 ресурсов!"
        elif event_type == 4:
            x, y = random.randint(0, grid_width - 1), random.randint(0, grid_height - 1)
            if territories[x][y].buildings:
                territories[x][y].buildings = []
                event_message = f"Постройка на ({x}, {y}) разрушена землетрясением!"
        elif event_type == 5:
            if random.random() < 0.5:
                player_population += 30
                event_message = "Прирост населения у игрока: +30!"
            else:
                bot_population += 30
                event_message = "Прирост населения у бота: +30!"
        elif event_type == 6:
            x, y = random.randint(0, grid_width - 1), random.randint(0, grid_height - 1)
            if not territories[x][y].is_wall:
                territories[x][y].buff_debuff = "speed_boost"
                territories[x][y].effect_timer = 180
                event_message = f"Молния ударила в ({x}, {y}) - ускорение атак!"
        elif event_type == 7:
            x, y = random.randint(0, grid_width - 1), random.randint(0, grid_height - 1)
            if not territories[x][y].is_wall and territories[x][y].owner != 0:
                territories[x][y].buff_debuff = "plague"
                territories[x][y].population = BUFFS_DEBUFFS["plague"]["effect"](territories[x][y])
                territories[x][y].effect_timer = 180
                event_message = f"Чума поразила ({x}, {y})!"
        elif event_type == 8:
            if random.random() < 0.5:
                player_resources -= 15
                event_message = "Игрок потерял ресурсы из-за наводнения: -15!"
            else:
                bot_resources -= 15
                event_message = "Бот потерял ресурсы из-за наводнения: -15!"
        elif event_type == 9:
            x, y = random.randint(0, grid_width - 1), random.randint(0, grid_height - 1)
            if not territories[x][y].is_wall and territories[x][y].owner == 0:
                territories[x][y].troops['Infantry'] = 10
                event_message = f"Дикие воины появились на ({x}, {y})!"
        elif event_type == 10:
            x, y = random.randint(0, grid_width - 1), random.randint(0, grid_height - 1)
            if not territories[x][y].is_wall:
                territories[x][y].level = min(territories[x][y].level + 1, GAME_CONFIG['MAX_LEVEL'])
                territories[x][y].resources = (GAME_CONFIG['RESOURCE_BASE'] +
                                               GAME_CONFIG['RESOURCE_PER_LEVEL'] * (territories[x][y].level - 1))
                event_message = f"Таинственная сила улучшила ({x}, {y})!"
        event_timer = 120

def check_game_over():
    player_territories = sum(1 for row in territories for t in row if t.owner == 1)
    bot_territories = sum(1 for row in territories for t in row if t.owner == 2)
    if player_territories == 0:
        return "Бота"
    elif bot_territories == 0:
        return "Игрока"
    return None

# Основной цикл
running = True
clock = pygame.time.Clock()
selection_pulse = 0
preview_map = None

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
        elif event.type == pygame.KEYDOWN:
            if game_state == MENU and event.key == pygame.K_SPACE:
                game_state = SETTINGS
            elif game_state == SETTINGS:
                if event.key == pygame.K_RETURN and not settings_input:
                    game_state = SEED_INPUT
                elif settings_input:
                    if event.key == pygame.K_RETURN and seed_input:
                        try:
                            value = float(seed_input)
                            if settings_input.startswith('ARMY_COST_'):
                                parts = settings_input.split('_')
                                unit, res_type = parts[2], parts[3]
                                GAME_CONFIG['ARMY_COST'][unit][res_type] = int(value)
                            elif settings_input in ['FORT_COST_resources', 'FORT_COST_population', 'CITY_COST_resources', 'CITY_COST_population', 'TOWER_COST_resources', 'TOWER_COST_population', 'UPGRADE_COST_resources']:
                                key, res_type = settings_input.rsplit('_', 1)
                                GAME_CONFIG[key][res_type] = int(value)
                            else:
                                GAME_CONFIG[settings_input] = value if 'INTELLIGENCE' in settings_input or 'CHANCE' in settings_input or 'DENSITY' in settings_input else int(value)
                        except ValueError:
                            pass
                        seed_input = ""
                        settings_input = None
                    elif event.key == pygame.K_BACKSPACE:
                        seed_input = seed_input[:-1]
                    elif event.unicode.isalnum() or event.unicode == '.' or event.unicode == '/':
                        seed_input += event.unicode
            elif game_state == SEED_INPUT:
                if event.key == pygame.K_RETURN and seed_input:
                    generate_map(seed_input)
                    game_state = PLAYING
                    attacks.clear()
                    used_in_turn.clear()
                    attacks_this_turn = 0
                    player_resources = GAME_CONFIG['INITIAL_RESOURCES']
                    player_population = GAME_CONFIG['INITIAL_POPULATION']
                    bot_resources = GAME_CONFIG['INITIAL_RESOURCES']
                    bot_population = GAME_CONFIG['INITIAL_POPULATION']
                    turn_count = 0
                elif event.key == pygame.K_BACKSPACE:
                    seed_input = seed_input[:-1]
                    if seed_input:
                        preview_map = generate_preview_map(seed_input)
                    else:
                        preview_map = None
                elif event.unicode.isalnum() or event.unicode == '.' or event.unicode == '/':
                    seed_input += event.unicode
                    preview_map = generate_preview_map(seed_input)
            elif game_state == GAME_OVER and event.key == pygame.K_r:
                generate_map(current_seed)
                player_resources = GAME_CONFIG['INITIAL_RESOURCES']
                player_population = GAME_CONFIG['INITIAL_POPULATION']
                bot_resources = GAME_CONFIG['INITIAL_RESOURCES']
                bot_population = GAME_CONFIG['INITIAL_POPULATION']
                game_state = PLAYING
                selected = None
                attacks.clear()
                used_in_turn.clear()
                attacks_this_turn = 0
                turn_count = 0
            elif game_state == PLAYING:
                if event.key == pygame.K_SPACE:
                    execute_turn()
                    random_event()
                elif selected:
                    if event.key == pygame.K_1:
                        create_army(selected[0], selected[1], 'Infantry')
                    elif event.key == pygame.K_2:
                        create_army(selected[0], selected[1], 'Cavalry')
                    elif event.key == pygame.K_3:
                        create_army(selected[0], selected[1], 'Archers')
                    elif event.key == pygame.K_4:
                        upgrade_territory(selected[0], selected[1])
                    elif event.key == pygame.K_5:
                        build_structure(selected[0], selected[1], 'fort')
                    elif event.key == pygame.K_6:
                        build_structure(selected[0], selected[1], 'city')
                    elif event.key == pygame.K_7:
                        build_structure(selected[0], selected[1], 'tower')
        elif event.type == pygame.MOUSEBUTTONDOWN and game_state == PLAYING:
            x, y = event.pos
            grid_x, grid_y = x // GAME_CONFIG['GRID_SIZE'], y // GAME_CONFIG['GRID_SIZE']
            if 0 <= grid_x < grid_width and 0 <= grid_y < grid_height:  # Проверка клика в пределах карты
                if event.button == 1:
                    selected = (grid_x, grid_y)
                elif event.button == 3 and selected:
                    add_attack(selected[0], selected[1], grid_x, grid_y)
            elif x >= grid_width * GAME_CONFIG['GRID_SIZE'] and event.button == 1 and hover_button:  # Клик по UI
                hover_button()

    cursor_blink = (cursor_blink + 1) % 60  # Для мигания курсора

    if game_state == MENU:
        screen.fill(BLACK)
        title = title_font.render("Война за территории", True, WHITE)
        shadow = title_font.render("Война за территории", True, GRAY)
        start_text = font.render("Нажмите SPACE для настроек", True, WHITE)
        screen.blit(shadow, (GAME_CONFIG['WIDTH'] // 2 - title.get_width() // 2 + 2, GAME_CONFIG['HEIGHT'] // 3 + 2))
        screen.blit(title, (GAME_CONFIG['WIDTH'] // 2 - title.get_width() // 2, GAME_CONFIG['HEIGHT'] // 3))
        screen.blit(start_text, (GAME_CONFIG['WIDTH'] // 2 - start_text.get_width() // 2, GAME_CONFIG['HEIGHT'] // 2))
    elif game_state == SETTINGS:
        draw_settings()
    elif game_state == SEED_INPUT:
        screen.fill(BLACK)
        prompt = font.render("Введите сид или имя файла и нажмите ENTER:", True, WHITE)
        seed_text = font.render(seed_input, True, WHITE)
        # Сдвигаем текст выше, чтобы он не перекрывался картой
        screen.blit(prompt, (GAME_CONFIG['WIDTH'] // 2 - prompt.get_width() // 2, GAME_CONFIG['HEIGHT'] // 4 - 50))
        screen.blit(seed_text, (GAME_CONFIG['WIDTH'] // 2 - seed_text.get_width() // 2, GAME_CONFIG['HEIGHT'] // 4))
        if cursor_blink < 30:  # Мигание курсора
            cursor_x = GAME_CONFIG['WIDTH'] // 2 - seed_text.get_width() // 2 + seed_text.get_width()
            pygame.draw.line(screen, WHITE, (cursor_x, GAME_CONFIG['HEIGHT'] // 4 - 10),
                             (cursor_x, GAME_CONFIG['HEIGHT'] // 4 + 10), 2)
        if preview_map:
            draw_seed_preview(preview_map)
            if preview_map:
                draw_seed_preview(preview_map)
    elif game_state == PLAYING:
        draw_map()
        draw_ui()
        if selected:
            selection_pulse = (selection_pulse + 0.1) % (2 * math.pi)
            thickness = 3 + int(math.sin(selection_pulse) * 2)
            pygame.draw.rect(screen, YELLOW,
                             (selected[0] * GAME_CONFIG['GRID_SIZE'],
                              selected[1] * GAME_CONFIG['GRID_SIZE'],
                              GAME_CONFIG['GRID_SIZE'], GAME_CONFIG['GRID_SIZE']), thickness)
        for from_x, from_y, to_x, to_y in attacks:
            pygame.draw.rect(screen, RED,
                             (to_x * GAME_CONFIG['GRID_SIZE'],
                              to_y * GAME_CONFIG['GRID_SIZE'],
                              GAME_CONFIG['GRID_SIZE'], GAME_CONFIG['GRID_SIZE']), 2)
        if event_timer > 0:
            event_timer -= 1
        winner = check_game_over()
        if winner:
            game_state = GAME_OVER
    elif game_state == GAME_OVER:
        screen.fill(BLACK)
        result = title_font.render(f"Победа {winner}!", True, WHITE)
        restart_text = font.render("Нажмите R для рестарта с тем же сидом", True, WHITE)
        screen.blit(result, (GAME_CONFIG['WIDTH'] // 2 - result.get_width() // 2, GAME_CONFIG['HEIGHT'] // 3))
        screen.blit(restart_text,
                    (GAME_CONFIG['WIDTH'] // 2 - restart_text.get_width() // 2, GAME_CONFIG['HEIGHT'] // 2))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

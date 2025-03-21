import pygame
import os

pygame.init()

# Настройки
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
GRID_SIZE = 40
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Редактор карт")
font = pygame.font.Font(None, 32)
small_font = pygame.font.Font(None, 24)

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 100, 100)
BLUE = (100, 100, 255)
GRAY = (200, 200, 220)
BROWN = (140, 90, 60)
PURPLE = (200, 120, 200)
ORANGE = (255, 180, 100)
CYAN = (100, 220, 220)
YELLOW = (255, 240, 120)
GOLD = (255, 200, 0)

# Символы и их отображение
ELEMENTS = {
    '.': {'color': GRAY, 'desc': 'Пусто'},
    'W': {'color': BROWN, 'desc': 'Стена'},
    'P': {'color': RED, 'desc': 'Игрок'},
    'B': {'color': BLUE, 'desc': 'Бот'},
    'F': {'color': PURPLE, 'desc': 'Форт'},
    'C': {'color': ORANGE, 'desc': 'Город'},
    'T': {'color': CYAN, 'desc': 'Башня'},
    'R': {'color': GOLD, 'desc': 'Ресурсы'}
}

# Изначальная пустая карта
grid = [['.' for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
current_element = '.'
filename = ""
message = ""
message_timer = 0


def draw_grid():
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            color = ELEMENTS[grid[y][x]]['color']
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)


def draw_ui():
    global message, message_timer
    ui_rect = pygame.Rect(0, SCREEN_HEIGHT - 150, SCREEN_WIDTH, 150)
    pygame.draw.rect(screen, BLACK, ui_rect)
    y_offset = SCREEN_HEIGHT - 140
    for i, (symbol, data) in enumerate(ELEMENTS.items()):
        text = small_font.render(f"{i + 1}: {data['desc']} ({symbol})", True, WHITE)
        screen.blit(text, (10 + (i % 4) * 300, y_offset + (i // 4) * 30))
    current_text = font.render(f"Выбран: {ELEMENTS[current_element]['desc']} ({current_element})", True, YELLOW)
    screen.blit(current_text, (SCREEN_WIDTH - current_text.get_width() - 10, SCREEN_HEIGHT - 40))
    filename_text = font.render(f"Имя файла: {filename}", True, WHITE)
    screen.blit(filename_text, (10, SCREEN_HEIGHT - 40))

    # Список доступных карт
    maps_dir = 'maps'
    if os.path.exists(maps_dir):
        maps = [f[:-4] for f in os.listdir(maps_dir) if f.endswith('.txt')]
        maps_text = small_font.render("Доступные карты: " + ", ".join(maps[:10]), True, WHITE)  # Показываем до 10 карт
        screen.blit(maps_text, (10, SCREEN_HEIGHT - 70))

    if message and message_timer > 0:
        msg_text = font.render(message, True, YELLOW)
        screen.blit(msg_text, (SCREEN_WIDTH // 2 - msg_text.get_width() // 2, SCREEN_HEIGHT // 2))
        message_timer -= 1


def save_map():
    global message, message_timer
    if not filename:
        message = "Введите имя файла!"
        message_timer = 60
        return
    if not os.path.exists('maps'):
        os.makedirs('maps')
    with open(f"maps/{filename}.txt", 'w') as f:
        for row in grid:
            f.write(''.join(row) + '\n')
    message = f"Карта сохранена как maps/{filename}.txt"
    message_timer = 60


def load_map():
    global grid, message, message_timer
    if not filename or not os.path.exists(f"maps/{filename}.txt"):
        message = "Файл не найден!"
        message_timer = 60
        return
    with open(f"maps/{filename}.txt", 'r') as f:
        lines = f.readlines()
        grid = [['.' for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        for y, line in enumerate(lines[:GRID_HEIGHT]):
            for x, char in enumerate(line.strip()[:GRID_WIDTH]):
                if char in ELEMENTS:
                    grid[y][x] = char
    message = f"Карта загружена: maps/{filename}.txt"
    message_timer = 60


# Основной цикл
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            grid_x, grid_y = x // GRID_SIZE, y // GRID_SIZE
            if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                if event.button == 1:  # ЛКМ - установка элемента
                    grid[grid_y][grid_x] = current_element
                elif event.button == 3:  # ПКМ - очистка
                    grid[grid_y][grid_x] = '.'
        elif event.type == pygame.KEYDOWN:
            if event.key in (
            pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8):
                current_element = list(ELEMENTS.keys())[event.key - pygame.K_1]
            elif event.key == pygame.K_s:  # S - сохранить
                save_map()
            elif event.key == pygame.K_l:  # L - загрузить
                load_map()
            elif event.key == pygame.K_BACKSPACE:
                filename = filename[:-1]
            elif event.unicode.isalnum() or event.unicode == '_':
                filename += event.unicode

    screen.fill(BLACK)
    draw_grid()
    draw_ui()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
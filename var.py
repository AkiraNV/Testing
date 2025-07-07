# import pygame
# import random

# # --- Initialization ---
# pygame.init()

# # --- Screen Settings ---
# SCREEN_WIDTH = 640
# SCREEN_HEIGHT = 480
# screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# pygame.display.set_caption("Space Max Background Test")

# # --- Colors (from mycolors.py in Space Max) ---
# RED = (255, 0, 0)
# GREEN = (0, 255, 0)
# BLUE = (0, 0, 255)
# YELLOW = (255, 255, 0)
# PINK = (255, 105, 180)
# BLACK = (0, 0, 0)

# # --- Background Class ---
# class Background(pygame.sprite.Sprite):
#     def __init__(self):
#         super().__init__()
#         self.image = pygame.image.load("scroll.png").convert()  # Thay bằng đường dẫn đến hình ảnh của bạn
#         self.rect = self.image.get_rect()
#         self.rect2 = self.image.get_rect()
#         self.rect2.y = -self.rect.height
#         self.speed = 2

#     def update(self):
#         self.rect.y += self.speed
#         self.rect2.y += self.speed
#         if self.rect.y > self.rect.height:
#             self.rect.y = -self.rect.height
#         if self.rect2.y > self.rect.height:
#             self.rect2.y = -self.rect.height

# # --- Polygon Class ---
# class Polygon(pygame.sprite.Sprite):
#     def __init__(self):
#         super().__init__()
#         n = random.randint(3, 12)
#         r = random.randint(10, 50)
#         self.points = [(random.randint(-r, r), random.randint(-r, r)) for _ in range(n)]
#         self.rect = pygame.Rect(random.randint(0, SCREEN_WIDTH), random.randint(-100, -10), r * 2, r * 2)
#         self.image = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
#         color = random.choice([RED, GREEN, BLUE, YELLOW, PINK])
#         pygame.draw.polygon(self.image, color, [(x + r, y + r) for x, y in self.points], random.randint(1, 2))
#         self.speed = random.randint(1, 5)

#     def update(self):
#         self.rect.y += self.speed
#         if self.rect.y > SCREEN_HEIGHT:
#             self.rect.y = random.randint(-100, -10)
#             self.rect.x = random.randint(0, SCREEN_WIDTH)

# # --- Create Polygons Function ---
# def create_polygons(all_polygons):
#     all_polygons.empty()
#     for i in range(20):
#         all_polygons.add(Polygon())

# # --- Main Loop ---
# clock = pygame.time.Clock()
# bg = Background()
# all_polygons = pygame.sprite.RenderUpdates()
# create_polygons(all_polygons)
# option_scroll = 0  # 0: Image background, 1: Polygons
# running = True

# while running:
#     # --- Event Handling ---
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#         if event.type == pygame.KEYDOWN:
#             if event.key == pygame.K_ESCAPE:
#                 running = False
#             if event.key == pygame.K_s:  # Press 'S' to toggle background
#                 option_scroll = 1 - option_scroll
#                 if option_scroll == 1:
#                     create_polygons(all_polygons)

#     # --- Drawing and Updating ---
#     if option_scroll == 0:
#         screen.blit(bg.image, bg.rect)
#         screen.blit(bg.image, bg.rect2)
#         bg.update()
#     else:
#         screen.fill(BLACK)
#         all_polygons.update()
#         all_polygons.draw(screen)

#     pygame.display.flip()
#     clock.tick(60)

# pygame.quit()

import pygame, sys, random

# --- Initialization ---
pygame.init()

# --- Screen Settings ---
SCREEN_WIDTH = 720
SCREEN_HEIGHT = 640
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Max")

# --- Load Assets ---
try:
    background_image = pygame.image.load('bg2.jpg').convert()
    background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    font_path = './Orbitron/static/Orbitron-Medium.ttf'
except pygame.error as e:
    print(f"Lỗi tải ảnh hoặc font: {e}")
    sys.exit()

# --- Font Settings ---
font_size = 25
font = pygame.font.Font(font_path, font_size)
line_height = int(font.get_height() * 1.2)
padding_from_bottom = int(line_height * 0.5)

# --- Colors ---
COLOR_NORMAL_TEXT = (255, 80, 0)
COLOR_NORMAL_OUTLINE = (40, 40, 40)
COLOR_HOVER_TEXT = (255, 255, 255)
COLOR_HOVER_OUTLINE = (255, 200, 0)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PINK = (255, 105, 180)

outline_thickness_normal = max(1, font_size // 20)
outline_thickness_hover = max(2, font_size // 15)

# --- Classes from var.py ---
class Background(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("scroll.png").convert()
        self.rect = self.image.get_rect()
        self.rect2 = self.image.get_rect()
        self.rect2.y = -self.rect.height
        self.speed = 2

    def update(self):
        self.rect.y += self.speed
        self.rect2.y += self.speed
        if self.rect.y > self.rect.height:
            self.rect.y = -self.rect.height
        if self.rect2.y > self.rect.height:
            self.rect2.y = -self.rect.height

class Polygon(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        n = random.randint(3, 12)
        r = random.randint(10, 50)
        self.points = [(random.randint(-r, r), random.randint(-r, r)) for _ in range(n)]
        self.rect = pygame.Rect(random.randint(0, SCREEN_WIDTH), random.randint(-100, -10), r * 2, r * 2)
        self.image = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        color = random.choice([RED, GREEN, BLUE, YELLOW, PINK])
        pygame.draw.polygon(self.image, color, [(x + r, y + r) for x, y in self.points], random.randint(1, 2))
        self.speed = random.randint(1, 5)

    def update(self):
        self.rect.y += self.speed
        if self.rect.y > SCREEN_HEIGHT:
            self.rect.y = random.randint(-100, -10)
            self.rect.x = random.randint(0, SCREEN_WIDTH)

def create_polygons(group):
    group.empty()
    for _ in range(20):
        group.add(Polygon())

# --- Menu & Game State ---
menu_options = [
    "Chơi",
    "Điểm cao nhất",
    "Tốc độ",
    "Lời cảm ơn",
    "Ngôn ngữ",
    "Scrolling",
    "Thoát"
]
menu_rects = []
current_screen = "menu"
back_button_rect = None
option_scroll = 0

# --- Background setup ---
bg = Background()
all_polygons = pygame.sprite.RenderUpdates()
create_polygons(all_polygons)

# --- Draw Helpers ---
def draw_text_with_outline(text, font, text_color, outline_color, x, y, outline_thickness):
    for dx in range(-outline_thickness, outline_thickness + 1):
        for dy in range(-outline_thickness, outline_thickness + 1):
            if dx != 0 or dy != 0:
                outline_surf = font.render(text, True, outline_color)
                screen.blit(outline_surf, (x + dx, y + dy))
    text_surf = font.render(text, True, text_color)
    screen.blit(text_surf, (x, y))

def draw_screen_with_text(title):
    screen.blit(background_image, (0, 0))
    draw_text_with_outline(title, font, COLOR_NORMAL_TEXT, COLOR_NORMAL_OUTLINE,
                         (SCREEN_WIDTH - font.size(title)[0]) // 2, 50, outline_thickness_normal)
    global back_button_rect
    back_text = "Quay lại"
    back_x = (SCREEN_WIDTH - font.size(back_text)[0]) // 2
    back_y = SCREEN_HEIGHT - line_height - padding_from_bottom
    draw_text_with_outline(back_text, font,
        COLOR_HOVER_TEXT if back_button_rect and back_button_rect.collidepoint(pygame.mouse.get_pos()) else COLOR_NORMAL_TEXT,
        COLOR_HOVER_OUTLINE if back_button_rect and back_button_rect.collidepoint(pygame.mouse.get_pos()) else COLOR_NORMAL_OUTLINE,
        back_x, back_y,
        outline_thickness_hover if back_button_rect and back_button_rect.collidepoint(pygame.mouse.get_pos()) else outline_thickness_normal)
    back_button_rect = font.render(back_text, True, (0, 0, 0)).get_rect(topleft=(back_x, back_y))

def draw_game_screen():
    global back_button_rect, option_scroll
    if option_scroll == 0:
        bg.update()
        screen.blit(bg.image, bg.rect)
        screen.blit(bg.image, bg.rect2)
    else:
        screen.fill(BLACK)
        all_polygons.update()
        all_polygons.draw(screen)

    # text = "Đang chơi trò chơi... (Nhấn S để đổi nền)"
    # draw_text_with_outline(text, font, COLOR_NORMAL_TEXT, COLOR_NORMAL_OUTLINE,
    #     (SCREEN_WIDTH - font.size(text)[0]) // 2, 50, outline_thickness_normal)

    # back_text = "Quay lại"
    # back_x = (SCREEN_WIDTH - font.size(back_text)[0]) // 2
    # back_y = SCREEN_HEIGHT - line_height - padding_from_bottom
    # draw_text_with_outline(back_text, font,
    #     COLOR_HOVER_TEXT if back_button_rect and back_button_rect.collidepoint(pygame.mouse.get_pos()) else COLOR_NORMAL_TEXT,
    #     COLOR_HOVER_OUTLINE if back_button_rect and back_button_rect.collidepoint(pygame.mouse.get_pos()) else COLOR_NORMAL_OUTLINE,
    #     back_x, back_y,
    #     outline_thickness_hover if back_button_rect and back_button_rect.collidepoint(pygame.mouse.get_pos()) else outline_thickness_normal)
    # back_button_rect = font.render(back_text, True, (0, 0, 0)).get_rect(topleft=(back_x, back_y))

# --- Main Loop ---
clock = pygame.time.Clock()
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if current_screen == "menu":
                    for i, rect in enumerate(menu_rects):
                        if rect.collidepoint(mouse_pos):
                            if menu_options[i] == "Thoát":
                                running = False
                            elif menu_options[i] == "Chơi":
                                current_screen = "game"
                            elif menu_options[i] == "Điểm cao nhất":
                                current_screen = "high_score"
                            elif menu_options[i] == "Tốc độ":
                                current_screen = "speed"
                            elif menu_options[i] == "Lời cảm ơn":
                                current_screen = "thanks"
                            elif menu_options[i] == "Ngôn ngữ":
                                current_screen = "language"
                            elif menu_options[i] == "Scrolling":
                                current_screen = "scrolling"
                else:
                    if back_button_rect and back_button_rect.collidepoint(mouse_pos):
                        current_screen = "menu"

        if event.type == pygame.KEYDOWN:
            if current_screen == "game":
                if event.key == pygame.K_s:
                    option_scroll = 1 - option_scroll
                    if option_scroll == 1:
                        create_polygons(all_polygons)
                elif event.key == pygame.K_ESCAPE:
                    current_screen = "menu"

    if current_screen == "menu":
        screen.blit(background_image, (0, 0))
        menu_rects.clear()
        total_menu_height = len(menu_options) * line_height
        start_y = SCREEN_HEIGHT - total_menu_height - padding_from_bottom
        for i, option in enumerate(menu_options):
            text_surface = font.render(option, True, (0, 0, 0))
            x = (SCREEN_WIDTH - text_surface.get_width()) // 2
            y = start_y + (i * line_height)
            rect = text_surface.get_rect(topleft=(x, y))
            menu_rects.append(rect)
            if rect.collidepoint(mouse_pos):
                draw_text_with_outline(option, font, COLOR_HOVER_TEXT, COLOR_HOVER_OUTLINE, x, y, outline_thickness_hover)
            else:
                draw_text_with_outline(option, font, COLOR_NORMAL_TEXT, COLOR_NORMAL_OUTLINE, x, y, outline_thickness_normal)
    elif current_screen == "high_score":
        draw_screen_with_text("Điểm cao nhất: 1000")
    elif current_screen == "speed":
        draw_screen_with_text("Tốc độ: 60 FPS")
    elif current_screen == "thanks":
        draw_screen_with_text("Cảm ơn bạn đã chơi!")
    elif current_screen == "language":
        draw_screen_with_text("Ngôn ngữ: Tiếng Việt")
    elif current_screen == "scrolling":
        draw_screen_with_text("Scrolling: Không gian")
    elif current_screen == "game":
        draw_game_screen()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

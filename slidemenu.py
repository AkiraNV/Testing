import pygame, sys, random, os
from platform import system

# --- Initialization ---
pygame.init()

# --- Screen Settings ---
SCREEN_WIDTH = 720
SCREEN_HEIGHT = 640
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Max")

# --- Asset Loading ---
try:
    background_image = pygame.image.load('better1.png').convert()
    background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    
    # font_path = './Orbitron/static/Orbitron-Medium.ttf'
    font_path = './Audiowide,Orbitron,Press_Start_2P,VT323/VT323/VT323-Regular.ttf'
except pygame.error as e:
    print(f"Error loading assets: {e}")
    print("\nMake sure 'bg2.jpg' and your font file are in the correct folders.")
    sys.exit()

#################################################################
### --- DYNAMIC LAYOUT SETTINGS (THE "CONTROL KNOB") --- ###
#################################################################
#
# You only need to change the font size here
font_size = 30
#
#################################################################

# --- Automatic Calculations ---
font = pygame.font.Font(font_path, font_size)

line_height = int(font.get_height() * 1.2)

### THIS IS THE MODIFIED LINE ###
# To move the menu closer to the bottom, we reduce the padding.
# Here, we're setting the gap to be just half the height of one line.
padding_from_bottom = int(line_height * 0.5)

outline_thickness_normal = max(1, font_size // 20)
outline_thickness_hover = max(2, font_size // 15)

# --- Colors (RGB) ---
COLOR_NORMAL_TEXT = (255, 255, 255)
COLOR_NORMAL_OUTLINE = (40, 40, 40)
COLOR_HOVER_TEXT = (169, 169, 169)
COLOR_HOVER_OUTLINE = (255, 255, 0)

# --- Menu Options ---
menu_options = [
    "Chơi",
    "Điểm cao nhất",
    "Tốc độ",
    "Màn hướng dẫn",
    "Hướng dẫn",
    "Ngôn ngữ",
    "Thoát"
]
menu_rects = []

# NEW: Track current screen state
current_screen = "menu"  # Start at main menu
back_button_rect = None  # Rectangle for "Back" button

# NEW: Helper functions for each screen (no changes to original code)
def draw_high_score_screen():
    screen.blit(background_image, (0, 0))
    # Sample high scores (replace with file reading if needed)
    scores = [("Player1", 1000), ("Player2", 800), ("Player3", 600)]
    y = 50
    for name, score in scores:
        text = f"{name}: {score}"
        draw_text_with_outline(text, font, COLOR_NORMAL_TEXT, COLOR_NORMAL_OUTLINE, 
                             (SCREEN_WIDTH - font.size(text)[0]) // 2, y, outline_thickness_normal)
        y += line_height
    # Draw "Back" button
    global back_button_rect
    back_text = "Quay lại"
    back_x = (SCREEN_WIDTH - font.size(back_text)[0]) // 2
    back_y = SCREEN_HEIGHT - line_height - padding_from_bottom
    draw_text_with_outline(back_text, font, COLOR_HOVER_TEXT if back_button_rect and back_button_rect.collidepoint(pygame.mouse.get_pos()) else COLOR_NORMAL_TEXT,
                         COLOR_HOVER_OUTLINE if back_button_rect and back_button_rect.collidepoint(pygame.mouse.get_pos()) else COLOR_NORMAL_OUTLINE,
                         back_x, back_y, outline_thickness_hover if back_button_rect and back_button_rect.collidepoint(pygame.mouse.get_pos()) else outline_thickness_normal)
    back_button_rect = font.render(back_text, True, (0, 0, 0)).get_rect(topleft=(back_x, back_y))

def draw_speed_screen():
    screen.blit(background_image, (0, 0))
    text = "Tốc độ: 60 FPS"  # Sample text
    draw_text_with_outline(text, font, COLOR_NORMAL_TEXT, COLOR_NORMAL_OUTLINE,
                         (SCREEN_WIDTH - font.size(text)[0]) // 2, 50, outline_thickness_normal)
    # Draw "Back" button
    global back_button_rect
    back_text = "Quay lại"
    back_x = (SCREEN_WIDTH - font.size(back_text)[0]) // 2
    back_y = SCREEN_HEIGHT - line_height - padding_from_bottom
    draw_text_with_outline(back_text, font, COLOR_HOVER_TEXT if back_button_rect and back_button_rect.collidepoint(pygame.mouse.get_pos()) else COLOR_NORMAL_TEXT,
                         COLOR_HOVER_OUTLINE if back_button_rect and back_button_rect.collidepoint(pygame.mouse.get_pos()) else COLOR_NORMAL_OUTLINE,
                         back_x, back_y, outline_thickness_hover if back_button_rect and back_button_rect.collidepoint(pygame.mouse.get_pos()) else outline_thickness_normal)
    back_button_rect = font.render(back_text, True, (0, 0, 0)).get_rect(topleft=(back_x, back_y))

def draw_thanks_screen():
    screen.blit(background_image, (0, 0))
    text = "Cảm ơn bạn đã chơi!"
    draw_text_with_outline(text, font, COLOR_NORMAL_TEXT, COLOR_NORMAL_OUTLINE,
                         (SCREEN_WIDTH - font.size(text)[0]) // 2, 50, outline_thickness_normal)
    # Draw "Back" button
    global back_button_rect
    back_text = "Quay lại"
    back_x = (SCREEN_WIDTH - font.size(back_text)[0]) // 2
    back_y = SCREEN_HEIGHT - line_height - padding_from_bottom
    draw_text_with_outline(back_text, font, COLOR_HOVER_TEXT if back_button_rect and back_button_rect.collidepoint(pygame.mouse.get_pos()) else COLOR_NORMAL_TEXT,
                         COLOR_HOVER_OUTLINE if back_button_rect and back_button_rect.collidepoint(pygame.mouse.get_pos()) else COLOR_NORMAL_OUTLINE,
                         back_x, back_y, outline_thickness_hover if back_button_rect and back_button_rect.collidepoint(pygame.mouse.get_pos()) else outline_thickness_normal)
    back_button_rect = font.render(back_text, True, (0, 0, 0)).get_rect(topleft=(back_x, back_y))

def draw_language_screen():
    screen.blit(background_image, (0, 0))
    text = "Ngôn ngữ: Tiếng Việt"
    draw_text_with_outline(text, font, COLOR_NORMAL_TEXT, COLOR_NORMAL_OUTLINE,
                         (SCREEN_WIDTH - font.size(text)[0]) // 2, 50, outline_thickness_normal)
    # Draw "Back" button
    global back_button_rect
    back_text = "Quay lại"
    back_x = (SCREEN_WIDTH - font.size(back_text)[0]) // 2
    back_y = SCREEN_HEIGHT - line_height - padding_from_bottom
    draw_text_with_outline(back_text, font, COLOR_HOVER_TEXT if back_button_rect and back_button_rect.collidepoint(pygame.mouse.get_pos()) else COLOR_NORMAL_TEXT,
                         COLOR_HOVER_OUTLINE if back_button_rect and back_button_rect.collidepoint(pygame.mouse.get_pos()) else COLOR_NORMAL_OUTLINE,
                         back_x, back_y, outline_thickness_hover if back_button_rect and back_button_rect.collidepoint(pygame.mouse.get_pos()) else outline_thickness_normal)
    back_button_rect = font.render(back_text, True, (0, 0, 0)).get_rect(topleft=(back_x, back_y))

def draw_scrolling_screen():
    screen.blit(background_image, (0, 0))
    text = "Scrolling: Không gian"
    draw_text_with_outline(text, font, COLOR_NORMAL_TEXT, COLOR_NORMAL_OUTLINE,
                         (SCREEN_WIDTH - font.size(text)[0]) // 2, 50, outline_thickness_normal)
    # Draw "Back" button
    global back_button_rect
    back_text = "Quay lại"
    back_x = (SCREEN_WIDTH - font.size(back_text)[0]) // 2
    back_y = SCREEN_HEIGHT - line_height - padding_from_bottom
    draw_text_with_outline(back_text, font, COLOR_HOVER_TEXT if back_button_rect and back_button_rect.collidepoint(pygame.mouse.get_pos()) else COLOR_NORMAL_TEXT,
                         COLOR_HOVER_OUTLINE if back_button_rect and back_button_rect.collidepoint(pygame.mouse.get_pos()) else COLOR_NORMAL_OUTLINE,
                         back_x, back_y, outline_thickness_hover if back_button_rect and back_button_rect.collidepoint(pygame.mouse.get_pos()) else outline_thickness_normal)
    back_button_rect = font.render(back_text, True, (0, 0, 0)).get_rect(topleft=(back_x, back_y))

def draw_game_screen():
    screen.blit(background_image, (0, 0))
    text = "Đang chơi trò chơi..."
    draw_text_with_outline(text, font, COLOR_NORMAL_TEXT, COLOR_NORMAL_OUTLINE,
                         (SCREEN_WIDTH - font.size(text)[0]) // 2, 50, outline_thickness_normal)
    # Draw "Back" button
    global back_button_rect
    back_text = "Quay lại"
    back_x = (SCREEN_WIDTH - font.size(back_text)[0]) // 2
    back_y = SCREEN_HEIGHT - line_height - padding_from_bottom
    draw_text_with_outline(back_text, font, COLOR_HOVER_TEXT if back_button_rect and back_button_rect.collidepoint(pygame.mouse.get_pos()) else COLOR_NORMAL_TEXT,
                         COLOR_HOVER_OUTLINE if back_button_rect and back_button_rect.collidepoint(pygame.mouse.get_pos()) else COLOR_NORMAL_OUTLINE,
                         back_x, back_y, outline_thickness_hover if back_button_rect and back_button_rect.collidepoint(pygame.mouse.get_pos()) else outline_thickness_normal)
    back_button_rect = font.render(back_text, True, (0, 0, 0)).get_rect(topleft=(back_x, back_y))

# --- Helper Function to Draw Outlined Text (no changes) ---
def draw_text_with_outline(text, font, text_color, outline_color, x, y, outline_thickness):
    for dx in range(-outline_thickness, outline_thickness + 1):
        for dy in range(-outline_thickness, outline_thickness + 1):
            if dx != 0 or dy != 0:
                outline_surf = font.render(text, True, outline_color)
                screen.blit(outline_surf, (x + dx, y + dy))

    text_surf = font.render(text, True, text_color)
    screen.blit(text_surf, (x, y))

# --- Main Game Loop ---
clock = pygame.time.Clock()
running = True
while running:
    # --- Event Handling ---
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if current_screen == "menu":  # NEW: Handle clicks on menu
                    for i, rect in enumerate(menu_rects):
                        if rect.collidepoint(mouse_pos):
                            print(f"Clicked on: {menu_options[i]}")
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
                else:  # NEW: Handle clicks on other screens (Back button)
                    if back_button_rect and back_button_rect.collidepoint(mouse_pos):
                        current_screen = "menu"

    # --- Drawing ---
    if current_screen == "menu":  # NEW: Draw menu only if on menu screen
        screen.blit(background_image, (0, 0))
        
        menu_rects.clear() 
        
        # The drawing logic uses the new, smaller padding value automatically
        total_menu_height = len(menu_options) * line_height
        start_y = SCREEN_HEIGHT - total_menu_height - padding_from_bottom

        for i, option in enumerate(menu_options):
            text_surface = font.render(option, True, (0,0,0))
            x = (SCREEN_WIDTH - text_surface.get_width()) // 2
            y = start_y + (i * line_height)
            
            rect = text_surface.get_rect(topleft=(x, y))
            menu_rects.append(rect)

            if rect.collidepoint(mouse_pos):
                draw_text_with_outline(option, font, COLOR_HOVER_TEXT, COLOR_HOVER_OUTLINE, x, y, outline_thickness_hover)
            else:
                draw_text_with_outline(option, font, COLOR_NORMAL_TEXT, COLOR_NORMAL_OUTLINE, x, y, outline_thickness_normal)
    else:  # NEW: Draw other screens
        if current_screen == "high_score":
            draw_high_score_screen()
        elif current_screen == "speed":
            draw_speed_screen()
        elif current_screen == "thanks":
            draw_thanks_screen()
        elif current_screen == "language":
            draw_language_screen()
        elif current_screen == "scrolling":
            draw_scrolling_screen()
        elif current_screen == "game":
            draw_game_screen()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
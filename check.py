import pygame, random, sys
from kivy.utils import platform
movement_mode = ["mode1"]
# === Screen and Settings ===
WIDTH, HEIGHT = 720, 640
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PINK = (255, 105, 180)

# === Font & Menu ===
font_path = './Audiowide,Orbitron,Press_Start_2P,VT323/VT323/VT323-Regular.ttf'
font_size = 35
pygame.init()
if platform == "android":
    screen_size = pygame.display.Info()
    size = width, height = (screen_size.current_w, screen_size.current_h)
else:
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Max")
font = pygame.font.Font(font_path, font_size)
font_large = pygame.font.Font(font_path, font_size + 10)
line_height = int(font.get_height() * 1.2)
padding_from_bottom = int(line_height * 0.5)
COLOR_NORMAL_TEXT = (255, 255, 255)
COLOR_NORMAL_OUTLINE = (40, 40, 40)
COLOR_HOVER_TEXT = (169, 169, 169)
COLOR_HOVER_OUTLINE = (255, 255, 0)
outline_thickness_normal = max(1, font_size // 20)
outline_thickness_hover = max(2, font_size // 15)

# === Helper function to load guide ===
def load_guide(filepath, lines_per_page=12):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    sections = []
    current_section = {"title": None, "lines": []}
    for line in lines:
        if line.startswith("#"):
            if current_section["title"]:
                sections.append(current_section)
            current_section = {"title": line[1:].strip(), "lines": []}
        else:
            current_section["lines"].append(line)
    if current_section["title"]:
        sections.append(current_section)

    pages = []
    for section in sections:
        lines = section["lines"]
        for i in range(0, len(lines), lines_per_page):
            page = {
                "title": section["title"],
                "lines": lines[i:i+lines_per_page]
            }
            pages.append(page)
    return pages


def input_player_name(screen, font, background_surface):
    name = ""
    active = True
    clock = pygame.time.Clock()

    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 10:
                        name += event.unicode

        # Dừng background động — chỉ vẽ background tĩnh đã có sẵn
        screen.blit(background_surface, (0, 0))

        # Render nội dung
        prompt_text = "Nhập tên (Enter để xác nhận):"
        prompt_surf = font.render(prompt_text, True, (255, 255, 255))
        name_surf = font.render(name, True, (255, 255, 0))

        # Vị trí hiển thị — cùng hàng
        base_x = 50
        base_y = HEIGHT // 2
        screen.blit(prompt_surf, (base_x, base_y))
        screen.blit(name_surf, (base_x + prompt_surf.get_width() + 10, base_y))

        pygame.display.flip()
        clock.tick(30)

    return name if name else "NoName"
def save_score(name, score, filename="score.txt"):
    new_line = f"{name}: {score}\n"

    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = ["#Điểm cao nhất\n"]

    if not lines or not lines[0].startswith("#"):
        lines.insert(0, "#Điểm cao nhất\n")

    lines.insert(1, new_line)

    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(lines)

def generate_display_scores(input_file="score.txt", output_file="score_display.txt"):
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if ":" in line]
    except FileNotFoundError:
        lines = []

    scores = sorted(lines, key=lambda x: int(x.split(":")[1]), reverse=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("#Điểm cao nhất\n")
        if scores:
            for line in scores:
                f.write(line + "\n")
        else:
            f.write("Chưa có điểm nào.\n")

def clear_scores_but_keep_header(filename="score.txt"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if lines and lines[0].startswith("#"):
            header = lines[0]
        else:
            header = "#Điểm cao nhất\n"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(header)
    except FileNotFoundError:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("#Điểm cao nhất\n")



# === Backgrounds ===
def load_background(path, fallback_color=(30, 30, 30)):
    try:
        img = pygame.image.load(path).convert()
        return pygame.transform.scale(img, (WIDTH, HEIGHT))
    except:
        surface = pygame.Surface((WIDTH, HEIGHT))
        surface.fill(fallback_color)
        return surface
menu_background = load_background('better1.png')
alt_background = load_background('bg2.png')
# === Background Scroll ===
class Background(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("super.png").convert()
        self.image = pygame.transform.scale(self.image, (720, 1080))
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
        self.rect = pygame.Rect(random.randint(0, WIDTH), random.randint(-100, -10), r * 2, r * 2)
        self.image = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        color = random.choice([RED, GREEN, BLUE, YELLOW, PINK])
        pygame.draw.polygon(self.image, color, [(x + r, y + r) for x, y in self.points], random.randint(1, 2))
        self.speed = random.randint(1, 5)

    def update(self):
        self.rect.y += self.speed
        if self.rect.y > HEIGHT:
            self.rect.y = random.randint(-100, -10)
            self.rect.x = random.randint(0, WIDTH)

def create_polygons(group):
    group.empty()
    for _ in range(20):
        group.add(Polygon())

# === Game State ===
def draw_text_with_outline(text, font, text_color, outline_color, x, y, outline_thickness):
    for dx in range(-outline_thickness, outline_thickness + 1):
        for dy in range(-outline_thickness, outline_thickness + 1):
            if dx != 0 or dy != 0:
                outline_surf = font.render(text, True, outline_color)
                screen.blit(outline_surf, (x + dx, y + dy))
    text_surf = font.render(text, True, text_color)
    screen.blit(text_surf, (x, y))

def start_game():
    import classes
    from classes import Ship, Enemy
    screen = pygame.display.set_mode((classes.WIDTH, classes.HEIGHT))
    clock = pygame.time.Clock()

    bg = Background()
    all_polygons = pygame.sprite.RenderUpdates()
    create_polygons(all_polygons)
    option_scroll = 0

    # player = Ship(classes.state())
    player = Ship(classes.state(), movement_mode[0])
    enemies = [Enemy(100, 10, 10, "neutral")]
    all_sprites = pygame.sprite.Group(player, *enemies)
    ship_projectiles = pygame.sprite.Group()
    enemy_proj = pygame.sprite.Group()

    running = True
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_s:
                    option_scroll = 1 - option_scroll
                    if option_scroll == 1:
                        create_polygons(all_polygons)

        if option_scroll == 0:
            bg.update()
            screen.blit(bg.image, bg.rect)
            screen.blit(bg.image, bg.rect2)
        else:
            screen.fill(BLACK)
            all_polygons.update()
            all_polygons.draw(screen)

        all_sprites.update()
        all_sprites.draw(screen)
        pygame.draw.rect(screen, RED, player.hitbox, 1)

        hits = pygame.sprite.groupcollide(ship_projectiles, all_sprites, True, False)
        for projectile, hit_list in hits.items():
            for target in hit_list:
                if isinstance(target, Enemy):
                    target.take_damage(player.strength)

        def player_hitbox_collision(player, projectile):
            if not hasattr(projectile, "mask"):
                return False
            offset = (player.hitbox.left - projectile.rect.left, player.hitbox.top - projectile.rect.top)
            player_mask = pygame.Mask(player.hitbox.size, fill=True)
            return projectile.mask.overlap(player_mask, offset) is not None

        enemy_hits = pygame.sprite.spritecollide(player, enemy_proj, True, collided=player_hitbox_collision)
        for proj in enemy_hits:
            if not player.invincible:
                player.take_damage(enemies[0].strength)
                if not player.alive:
                    death_start = pygame.time.get_ticks()
                    while True:
                        clock.tick(60)
                        for e in pygame.event.get():
                            if e.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()

                        if option_scroll == 0:
                            bg.update()
                            screen.blit(bg.image, bg.rect)
                            screen.blit(bg.image, bg.rect2)
                        else:
                            screen.fill(BLACK)
                            all_polygons.update()
                            all_polygons.draw(screen)

                        all_sprites.update()
                        all_sprites.draw(screen)
                        ship_projectiles.update()
                        ship_projectiles.draw(screen)
                        enemy_proj.update()
                        enemy_proj.draw(screen)

                        pygame.display.flip()

                        # if not player.alive and player not in all_sprites:
                        if not player.alive:
                            try:
                                player_score = getattr(player, "score", 0)
                            except Exception:
                                player_score = 0
                            background_surface = screen.copy()
                            player_name = input_player_name(screen, font, background_surface)
                            save_score(player_name, player_score)
                            # print(f"Đã lưu: {player_name} - {player_score}")
                            break
                    return

        def pe_collision(player, enemy):
            return player.hitbox.colliderect(enemy.rect)

        for sprite in all_sprites:
            if isinstance(sprite, Enemy) and not sprite.alive:
                all_sprites.remove(sprite)

        keys = pygame.key.get_pressed()
        if player.alive and keys[pygame.K_SPACE]:
            player.shoot(ship_projectiles)

        ship_projectiles.update()
        ship_projectiles.draw(screen)
        for proj in ship_projectiles:
            pygame.draw.rect(screen, GREEN, proj.rect, 1)

        player_pos = (player.rect.centerx, player.rect.centery) if player.alive else None
        for enemy in enemies:
            enemy.move_and_shoot(enemy_proj, player_pos)

        enemy_proj.update()
        enemy_proj.draw(screen)
        for proj in enemy_proj:
            if hasattr(proj, "mask"):
                offset = proj.rect.topleft
                outline = proj.mask.outline()
                for point in outline:
                    screen.set_at((point[0] + offset[0], point[1] + offset[1]), RED)

        pygame.display.flip()

# === Load màn hình ===
def load_screen(file):
    guide_pages = load_guide(file)
    if not guide_pages:
        print(f"⚠ File '{file}' không có nội dung hợp lệ.")
        return

    is_score_screen = (file == "score_display.txt")
    total_pages = len(guide_pages)
    current_page = 0
    clock = pygame.time.Clock()

    while True:
        screen.blit(alt_background, (0, 0))
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                elif event.key == pygame.K_RIGHT and current_page < total_pages - 1:
                    current_page += 1
                elif event.key == pygame.K_LEFT and current_page > 0:
                    current_page -= 1
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_click = True

        section_title = guide_pages[current_page]["title"]
        title_surf = font_large.render(section_title, True, YELLOW)
        screen.blit(title_surf, ((WIDTH - title_surf.get_width()) // 2, 30))

        page_lines = guide_pages[current_page]["lines"]
        for i, line in enumerate(page_lines):
            line_surf = font.render(line, True, COLOR_NORMAL_TEXT)
            screen.blit(line_surf, (50, 100 + i * line_height))

        prev_rect = next_rect = delete_rect = None
        if current_page > 0:
            prev_surf = font.render("<", True, COLOR_NORMAL_TEXT)
            prev_rect = prev_surf.get_rect(topleft=(50, HEIGHT - 60))
            screen.blit(prev_surf, prev_rect)
        if current_page < total_pages - 1:
            next_surf = font.render(">", True, COLOR_NORMAL_TEXT)
            next_rect = next_surf.get_rect(topright=(WIDTH - 50, HEIGHT - 60))
            screen.blit(next_surf, next_rect)

        # Vẽ nút Delete nếu là màn điểm số
        if is_score_screen:
            delete_surf = font.render("Delete", True, (255, 0, 0))
            delete_rect = delete_surf.get_rect(center=(WIDTH // 2, HEIGHT - 30))
            screen.blit(delete_surf, delete_rect)

        if mouse_click:
            if prev_rect and prev_rect.collidepoint(mouse_pos):
                current_page -= 1
            if next_rect and next_rect.collidepoint(mouse_pos):
                current_page += 1
            if is_score_screen and delete_rect and delete_rect.collidepoint(mouse_pos):
                clear_scores_but_keep_header("score.txt")
                generate_display_scores()
                guide_pages = load_guide("score_display.txt")
                total_pages = len(guide_pages)
                current_page = 0
                continue

        pygame.display.flip()
        clock.tick(60)


# === Menu ===
def run_menu():
    menu_options = ["Chơi", "Điểm cao nhất", "Tốc độ", "Hướng dẫn tân thủ", "Di chuyển", "Thoát"]
    current_screen = "menu"
    menu_rects = []
    clock = pygame.time.Clock()
    running = True

    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if current_screen == "menu":
                    for i, rect in enumerate(menu_rects):
                        if rect.collidepoint(mouse_pos):
                            option = menu_options[i]
                            if option == "Chơi":
                                start_game()
                            elif option == "Thoát":
                                running = False
                            elif option == "Điểm cao nhất":
                                generate_display_scores()
                                load_screen("score_display.txt")
                            elif option == "Tốc độ":
                                current_screen = "speed"
                            elif option == "Lời cảm ơn":
                                current_screen = "thanks"
                            elif option == "Hướng dẫn tân thủ":
                                load_screen("guide.txt")
                            elif option == "Di chuyển":
                                current_screen = "move"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    current_screen = "menu"

        screen.blit(menu_background if current_screen == "menu" else alt_background, (0, 0))
        if current_screen == "menu":
            menu_rects.clear()
            total_menu_height = len(menu_options) * line_height
            start_y = HEIGHT - total_menu_height - padding_from_bottom
            for i, option in enumerate(menu_options):
                text_surface = font.render(option, True, (0, 0, 0))
                x = (WIDTH - text_surface.get_width()) // 2
                y = start_y + (i * line_height)
                rect = text_surface.get_rect(topleft=(x, y))
                menu_rects.append(rect)
                if rect.collidepoint(mouse_pos):
                    draw_text_with_outline(option, font, COLOR_HOVER_TEXT, COLOR_HOVER_OUTLINE, x, y, outline_thickness_hover)
                else:
                    draw_text_with_outline(option, font, COLOR_NORMAL_TEXT, COLOR_NORMAL_OUTLINE, x, y, outline_thickness_normal)
        else:
            text = ""
            if current_screen == "high_score":
                text = "Điểm cao nhất: 1000"
            elif current_screen == "speed":
                text = "Tốc độ: 60 FPS"
            elif current_screen == "thanks":
                text = "Cảm ơn bạn đã chơi!"
            elif current_screen == "move":
                title_surf = font_large.render("Cách di chuyển", True, YELLOW)
                screen.blit(title_surf, ((WIDTH - title_surf.get_width()) // 2, 50))

                mode1_text = "Tổ hợp awsd :"
                mode2_text = "Tổ hợp mũi tên :"
                spacing = 60
                y_start = 200

                awsd_label = "mode 1"
                arrow_label = "mode 2"

                awsd_surf = font.render(mode1_text, True, COLOR_NORMAL_TEXT)
                arrow_surf = font.render(mode2_text, True, COLOR_NORMAL_TEXT)

                # Tạo rect trước để sử dụng cho kiểm tra hover và click
                awsd_mode_surf = font.render(awsd_label, True, YELLOW)
                arrow_mode_surf = font.render(arrow_label, True, YELLOW)
                awsd_rect = awsd_mode_surf.get_rect(topleft=(awsd_surf.get_width() + 70, y_start))
                arrow_rect = arrow_mode_surf.get_rect(topleft=(arrow_surf.get_width() + 70, y_start + spacing))

                # Lấy vị trí chuột
                mouse_pos = pygame.mouse.get_pos()

                # Xác định màu dựa trên movement_mode
                awsd_mode_color = GREEN if movement_mode[0] == "mode1" else YELLOW
                arrow_mode_color = GREEN if movement_mode[0] == "mode2" else YELLOW

                # Render lại surface với màu đã xác định
                awsd_mode_surf = font.render(awsd_label, True, awsd_mode_color)
                arrow_mode_surf = font.render(arrow_label, True, arrow_mode_color)

                # Cập nhật lại rect với surface mới
                awsd_rect = awsd_mode_surf.get_rect(topleft=(awsd_surf.get_width() + 70, y_start))
                arrow_rect = arrow_mode_surf.get_rect(topleft=(arrow_surf.get_width() + 70, y_start + spacing))

                # Vẽ lên màn hình
                screen.blit(awsd_surf, (50, y_start))
                screen.blit(awsd_mode_surf, awsd_rect)
                screen.blit(arrow_surf, (50, y_start + spacing))
                screen.blit(arrow_mode_surf, arrow_rect)

                # Xử lý sự kiện click
                if pygame.mouse.get_pressed()[0]:
                    if awsd_rect.collidepoint(mouse_pos):
                        movement_mode[0] = "mode1"
                    if arrow_rect.collidepoint(mouse_pos):
                        movement_mode[0] = "mode2"

            if text:
                draw_text_with_outline(text, font, COLOR_NORMAL_TEXT, COLOR_NORMAL_OUTLINE,
                                       (WIDTH - font.size(text)[0]) // 2, 50, outline_thickness_normal)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

# === Run ===
if __name__ == '__main__':
    run_menu()

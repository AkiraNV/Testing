import pygame
import numpy as np
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Rectangle, Color
from kivy.graphics.texture import Texture
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.core.text import LabelBase
from kivy.utils import get_color_from_hex
from kivy.properties import BooleanProperty
from kivy.base import EventLoop
from kivy.core.image import Image as CoreImage
from kivy.config import Config
import random
import sys
import logging
from classes import Ship, Enemy, Projectile, state, enemy_img, enemy_proj
from PIL import Image as PILImage
import io

# Thiết lập cấu hình Kivy để tránh DPI scaling
Config.set('graphics', 'width', '720')
Config.set('graphics', 'height', '640')
Config.set('graphics', 'dpi', '96')

# Thiết lập logging để chỉ xử lý lỗi
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# === INIT ===
pygame.init()
pygame.display.set_mode((1, 1), pygame.HIDDEN)
Window.size = (720, 640)  # Đảm bảo kích thước cửa sổ
texture_cache = {}
movement_mode = ["mode1"]

# Thiết lập font pixel
try:
    LabelBase.register(name='retro', fn_regular='./Audiowide,Orbitron,Press_Start_2P,VT323/VT323/VT323-Regular.ttf')
except Exception as e:
    logger.error(f"Lỗi khi đăng ký font retro: {e}")

# === Utility ===
def surface_to_texture(surface, target_size=None):
    if not surface:
        return None
    surface_id = id(surface)
    if surface_id not in texture_cache:
        try:
            # Lấy kích thước gốc
            width, height = surface.get_size()

            # Nếu target_size được chỉ định, scale surface
            if target_size:
                surface = pygame.transform.smoothscale(surface, target_size)
                width, height = target_size

            buffer = pygame.image.tostring(surface, "RGBA", False)
            texture = Texture.create(size=(width, height), colorfmt='rgba')
            texture.blit_buffer(buffer, colorfmt='rgba', bufferfmt='ubyte')
            texture.flip_vertical()
            texture_cache[surface_id] = texture
        except Exception as e:
            logger.error(f"Lỗi khi chuyển surface sang texture: {e}")
            return None
    return texture_cache[surface_id]

# === Background ===
class Background(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.width = Window.width
        self.image_height = 1080
        self.speed = 2
        self.y1 = 0
        self.y2 = -self.image_height
        self.size_hint = (None, None)
        self.size = (Window.width, Window.height)

        try:
            pil_img = PILImage.open("super.png").convert("RGBA")
            pil_img_resized = pil_img.resize((int(Window.width), self.image_height), PILImage.Resampling.LANCZOS)
            img_array = np.array(pil_img_resized)
        except Exception as e:
            logger.error(f"Lỗi khi tải super.png: {e}")
            img_array = np.zeros((self.image_height, int(Window.width), 4), dtype=np.uint8)
            img_array[:, :, :] = [50, 50, 50, 255]

        texture = Texture.create(size=(int(Window.width), self.image_height), colorfmt='rgba')
        texture.blit_buffer(img_array.flatten(), colorfmt='rgba', bufferfmt='ubyte')
        texture.flip_vertical()
        self.texture = texture

        with self.canvas.before:
            self.bg_rect = Rectangle(pos=(0, 0), size=(Window.width, Window.height))

        with self.canvas:
            self.rect1 = Rectangle(
                texture=self.texture,
                size=(Window.width, self.image_height),
                pos=(0, self.y1)
            )
            self.rect2 = Rectangle(
                texture=self.texture,
                size=(Window.width, self.image_height),
                pos=(0, self.y2)
            )

    def update(self, dt):
        self.y1 += self.speed
        self.y2 += self.speed

        if self.y1 >= self.image_height:
            self.y1 = self.y2 - self.image_height
        if self.y2 >= self.image_height:
            self.y2 = self.y1 - self.image_height

        self.rect1.pos = (0, self.y1)
        self.rect2.pos = (0, self.y2)
        self.bg_rect.size = (Window.width, Window.height)

# === ShipWidget ===
class ShipWidget(Widget):
    def __init__(self, ship, **kwargs):
        super().__init__(**kwargs)
        self.ship = ship
        self.size = (32, 32)
        self.display_y = ship.rect.y
        self.last_image = None
        self.texture = surface_to_texture(self.ship.image) if self.ship.image else None
        self.pos = (self.ship.rect.x, self.display_y)
        with self.canvas:
            self.rect = Rectangle(texture=self.texture, pos=self.pos, size=self.size) if self.texture else None

    def update(self, dt):
        self.ship.update()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.display_y = min(Window.height - self.size[1], self.display_y + self.ship.speed)
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.display_y = max(0, self.display_y - self.ship.speed)
        self.ship.rect.y = self.display_y
        self.pos = (self.ship.rect.x, self.display_y)
        if self.ship.image != self.last_image:
            self.last_image = self.ship.image
            self.texture = surface_to_texture(self.ship.image)
        self.canvas.clear()
        with self.canvas:
            if self.texture:
                self.rect = Rectangle(texture=self.texture, pos=self.pos, size=self.size)

    def on_size(self, instance, value):
        if value != (32, 32):
            self.size = (32, 32)

# === EnemyWidget ===
class EnemyWidget(Widget):
    def __init__(self, enemy, **kwargs):
        super().__init__(**kwargs)
        self.enemy = enemy
        self.size = (32, 32)
        self.size_hint = (None, None)
        self.pos = (enemy.rect.x, enemy.rect.y)
        self.frame_index = 0
        self.animation_speed = 0.1
        self.last_update = 0
        self.textures = []
        for img_path in enemy_img()[0]:
            try:
                surface = pygame.image.load(img_path).convert_alpha()
                texture = surface_to_texture(surface, target_size=(32, 32))
                if texture:
                    self.textures.append(texture)
            except Exception as e:
                logger.error(f"Failed to load enemy image {img_path}: {e}")
        self.texture = self.textures[self.frame_index] if self.textures else None
        with self.canvas:
            self.rect = Rectangle(texture=self.texture, pos=self.pos, size=self.size) if self.texture else None

    def update(self, dt):
        try:
            self.enemy.update()
            self.pos = (self.enemy.rect.x, self.enemy.rect.y)
            if self.size != (32, 32):
                self.size = (32, 32)
            self.last_update += dt
            if self.textures and self.last_update >= self.animation_speed:
                self.last_update = 0
                self.frame_index = (self.frame_index + 1) % len(self.textures)
                self.texture = self.textures[self.frame_index]
            self.canvas.clear()
            with self.canvas:
                if self.texture:
                    self.rect = Rectangle(texture=self.texture, pos=self.pos, size=self.size)
        except Exception as e:
            logger.error(f"Lỗi trong EnemyWidget.update: {e}")

    def on_size(self, instance, value):
        if value != (32, 32):
            self.size = (32, 32)

# === ProjectileWidget ===
class ProjectileWidget(Widget):
    def __init__(self, projectile, **kwargs):
        super().__init__(**kwargs)
        self.projectile = projectile
        self.size = (16, 16)
        self.size_hint = (None, None)
        self.pos = (projectile.rect.x, projectile.rect.y)
        self.texture = surface_to_texture(self.projectile.image, target_size=(16, 16)) if self.projectile.image else None
        with self.canvas:
            self.rect = Rectangle(texture=self.texture, pos=self.pos, size=self.size) if self.texture else None

    def update(self, dt):
        try:
            self.projectile.update()
            self.pos = (self.projectile.rect.x, self.projectile.rect.y)
            if self.size != (16, 16):
                self.size = (16, 16)
            self.canvas.clear()
            with self.canvas:
                if self.texture:
                    self.rect = Rectangle(texture=self.texture, pos=self.pos, size=self.size)
        except Exception as e:
            logger.error(f"Lỗi trong ProjectileWidget.update: {e}")

    def on_size(self, instance, value):
        if value != (16, 16):
            self.size = (16, 16)

# === Game Screen ===
class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bg = Background()
        self.add_widget(self.bg)

        self.player = Ship(state(), movement_mode[0])
        self.player.rect.x = Window.width // 2 - 16
        self.player.rect.y = 50
        self.player_widget = ShipWidget(self.player)
        self.add_widget(self.player_widget)

        self.enemies = [Enemy(100, 10, 10, "neutral")]
        self.enemies[0].rect.x = Window.width // 2 - 16
        self.enemies[0].rect.y = Window.height - 64
        self.enemy_widgets = [EnemyWidget(enemy) for enemy in self.enemies]
        for widget in self.enemy_widgets:
            self.add_widget(widget)

        self.ship_projectiles = pygame.sprite.Group()
        self.enemy_projectiles = pygame.sprite.Group()
        self.projectile_widgets = []

        self.keys = {}
        self.update_event = None

    def on_enter(self):
        Window.bind(on_key_down=self.on_key_down)
        Window.bind(on_key_up=self.on_key_up)
        self.update_event = Clock.schedule_interval(self.update, 1.0 / 60)

    def on_leave(self):
        Window.unbind(on_key_down=self.on_key_down)
        Window.unbind(on_key_up=self.on_key_up)
        if self.update_event:
            self.update_event.cancel()
            self.update_event = None

    def on_key_down(self, window, key, scancode, codepoint, modifier):
        key_map = {
            97: pygame.K_a, 100: pygame.K_d, 119: pygame.K_w, 115: pygame.K_s,
            276: pygame.K_LEFT, 275: pygame.K_RIGHT, 273: pygame.K_UP, 274: pygame.K_DOWN,
            304: pygame.K_LSHIFT, 32: pygame.K_SPACE
        }
        if key in key_map:
            self.keys[key_map[key]] = True
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key_map[key]))

    def on_key_up(self, window, key, *args):
        key_map = {
            97: pygame.K_a, 100: pygame.K_d, 119: pygame.K_w, 115: pygame.K_s,
            276: pygame.K_LEFT, 275: pygame.K_RIGHT, 273: pygame.K_UP, 274: pygame.K_DOWN,
            304: pygame.K_LSHIFT, 32: pygame.K_SPACE
        }
        if key in key_map:
            self.keys[key_map[key]] = False
            pygame.event.post(pygame.event.Event(pygame.KEYUP, key=key_map[key]))

    def update(self, dt):
        try:
            self.bg.update(dt)
            self.player_widget.update(dt)
            if self.player.rect.bottom >= 1080:
                self.player.rect.y = 1080

            if self.keys.get(pygame.K_SPACE):
                self.player.shoot(self.ship_projectiles)
            if self.keys.get(pygame.K_s) or self.keys.get(pygame.K_DOWN):
                self.player.rect.y += self.player.speed

            if self.keys.get(pygame.K_SPACE):
                self.player.shoot(self.ship_projectiles)

            for enemy, widget in zip(self.enemies[:], self.enemy_widgets[:]):
                enemy.move_and_shoot(self.enemy_projectiles, (self.player.rect.centerx, self.player.rect.centery) if self.player.alive else None)
                widget.update(dt)
                if not enemy.alive:
                    self.remove_widget(widget)
                    self.enemy_widgets.remove(widget)
                    self.enemies.remove(enemy)

            for proj in self.ship_projectiles.sprites()[:]:
                if not hasattr(proj, 'widget') and proj.image:
                    proj.widget = ProjectileWidget(proj)
                    self.projectile_widgets.append(proj.widget)
                    self.add_widget(proj.widget)
                if hasattr(proj, 'widget'):
                    proj.widget.update(dt)
                if proj.rect.y < 0:
                    proj.kill()
                    if hasattr(proj, 'widget'):
                        self.remove_widget(proj.widget)
                        self.projectile_widgets.remove(proj.widget)

            for proj in self.enemy_projectiles.sprites()[:]:
                if not hasattr(proj, 'widget') and proj.image:
                    proj.widget = ProjectileWidget(proj)
                    self.projectile_widgets.append(proj.widget)
                    self.add_widget(proj.widget)
                if hasattr(proj, 'widget'):
                    proj.widget.update(dt)
                if proj.rect.y > Window.height:
                    proj.kill()
                    if hasattr(proj, 'widget'):
                        self.remove_widget(proj.widget)
                        self.projectile_widgets.remove(proj.widget)

            for proj in self.ship_projectiles.sprites()[:]:
                for enemy in self.enemies[:]:
                    if proj.rect.colliderect(enemy.rect):
                        enemy.take_damage(self.player.strength)
                        proj.kill()
                        if hasattr(proj, 'widget'):
                            self.remove_widget(proj.widget)
                            self.projectile_widgets.remove(proj.widget)

            for proj in self.enemy_projectiles.sprites()[:]:
                if proj.rect.colliderect(self.player.hitbox) and not self.player.invincible:
                    self.player.take_damage(10)
                    proj.kill()
                    if hasattr(proj, 'widget'):
                        self.remove_widget(proj.widget)
                        self.projectile_widgets.remove(proj.widget)

            if not self.player.alive:
                if self.manager.has_screen("game_over"):
                    game_over_screen = self.manager.get_screen("game_over")
                    game_over_screen.name_input.text = ""
                    game_over_screen.score = getattr(self.player, "score", 0)
                    self.manager.current = "game_over"
                else:
                    logger.error("game_over screen not found in ScreenManager")
        except Exception as e:
            logger.error(f"Lỗi trong GameScreen.update: {e}")

# === Game Over Screen ===
class GameOverScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint=(1, None), height=400)
        with self.layout.canvas.before:
            Color(0, 0, 0, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.layout.bind(size=self._update_rect, pos=self._update_rect)
        self.title = Label(text="Game Over", font_name='retro', font_size=40, color=(1, 0, 0, 1))
        self.name_input = TextInput(hint_text="Nhập tên của bạn", multiline=False, font_name='retro', font_size=20,
                                    background_color=(0, 0, 0, 1), foreground_color=(1, 1, 0, 1))
        self.submit_button = Button(text="Gửi", font_name='retro', font_size=20, background_color=(0, 0, 1, 1),
                                    color=(1, 1, 1, 1), size_hint=(1, None), height=50)
        self.submit_button.bind(on_press=self.submit_score)
        self.layout.add_widget(self.title)
        self.layout.add_widget(self.name_input)
        self.layout.add_widget(self.submit_button)
        self.add_widget(self.layout)
        try:
            self.background = Image(source="bg2.png", fit_mode="fill", size=Window.size)
            self.add_widget(self.background, index=0)
        except Exception as e:
            logger.error(f"Lỗi khi tải background bg2.png: {e}")

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def submit_score(self, *args):
        try:
            name = self.name_input.text if self.name_input.text else "NoName"
            score = getattr(self, "score", 0)
            with open("score.txt", "a", encoding="utf-8") as f:
                f.write(f"{name} {score}\n")
            if self.manager.has_screen("menu"):
                self.manager.current = "menu"
            else:
                logger.error("menu screen not found in ScreenManager")
        except Exception as e:
            logger.error(f"Lỗi trong submit_score: {e}")

# === Info Screen ===
class InfoScreen(Screen):
    def __init__(self, title, content, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        try:
            self.background = Image(source="bg2.png", fit_mode="fill", size=Window.size)
            self.add_widget(self.background)
        except Exception as e:
            logger.error(f"Lỗi khi tải background bg2.png: {e}")
        self.title_label = Label(text=title, font_name='retro', font_size=40, color=(1, 1, 0, 1))
        self.content_label = Label(text=content, font_name='retro', font_size=20, color=(1, 1, 1, 1))
        self.back_button = Button(text="Quay lại", font_name='retro', font_size=20, color=(1, 1, 0, 1),
                                  size_hint=(1, None), height=50)
        self.back_button.bind(on_press=self.back_to_menu)
        self.layout.add_widget(self.title_label)
        self.layout.add_widget(self.content_label)
        self.layout.add_widget(self.back_button)
        self.add_widget(self.layout)

    def back_to_menu(self, instance):
        if self.manager.has_screen("menu"):
            self.manager.current = "menu"
        else:
            logger.error("menu screen not found in ScreenManager")

# === Hover Behavior ===
class HoverBehavior(object):
    hovered = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_enter')
        self.register_event_type('on_leave')
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return
        pos = args[1]
        inside = self.collide_point(*self.to_widget(*pos))
        if self.hovered != inside:
            self.hovered = inside
            if inside:
                self.dispatch('on_enter')
            else:
                self.dispatch('on_leave')

    def on_enter(self):
        pass

    def on_leave(self):
        pass

class HoverButton(Button, HoverBehavior):
    def on_pos(self, instance, value):
        pass

    def on_size(self, instance, value):
        pass

# === Guide Screen ===
class GuideScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.page = 0
        self.sections = self.load_sections()
        self.total_pages = len(self.sections)

        try:
            self.background = Image(source="bg2.png", fit_mode="fill", size=Window.size)
            self.add_widget(self.background)
        except Exception as e:
            logger.error(f"Lỗi khi tải background bg2.png: {e}")

        self.text_layout_container = BoxLayout(orientation='vertical', size_hint=(1, None), height=400,
                                               padding=(50, 50, 100, 300))
        self.text_layout = BoxLayout(orientation='vertical', spacing=30, size_hint_y=None)
        self.text_layout_container.add_widget(self.text_layout)
        self.add_widget(self.text_layout_container)

        self.back_btn = Button(
            text="< Quay lại",
            font_name='retro',
            font_size=20,
            size_hint=(None, None),
            size=(140, 40),
            pos_hint={'x': 0, 'top': 1},
            background_normal='',
            background_down='',
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1)
        )
        self.back_btn.bind(on_press=self.back_to_menu)
        self.add_widget(self.back_btn)

        self.title_label = Label(text="", font_name='retro', font_size=34, color=(1, 1, 0, 1), size_hint_y=None,
                                 height=50, halign='center', pos_hint={'top': 1})
        self.add_widget(self.title_label)

        self.main_layout = BoxLayout(orientation='horizontal', padding=[0, 0, 0, 0], spacing=10)
        self.content_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_x=0.5,
                                        pos_hint={'center_x': 0.25})

        self.nav_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=50, spacing=20)
        self.prev_btn = Button(
            text="<",
            font_name='retro',
            font_size=28,
            size_hint=(None, None),
            size=(50, 50),
            background_normal='',
            background_down='',
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1)
        )
        self.prev_btn.bind(on_press=self.prev_page)
        self.next_btn = Button(
            text=">",
            font_name='retro',
            font_size=28,
            size_hint=(None, None),
            size=(50, 50),
            background_normal='',
            background_down='',
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1)
        )
        self.next_btn.bind(on_press=self.next_page)
        self.page_label = Label(text="", font_name='retro', font_size=20, color=(1, 1, 1, 1), size_hint=(1, None),
                                height=50, halign='center')
        self.nav_layout.add_widget(self.prev_btn)
        self.nav_layout.add_widget(self.page_label)
        self.nav_layout.add_widget(self.next_btn)
        self.content_layout.add_widget(self.nav_layout)

        self.main_layout.add_widget(self.content_layout)
        self.add_widget(self.main_layout)

        self.update_page()

    def load_sections(self):
        try:
            with open("guide.txt", "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip() != ""]
        except FileNotFoundError:
            logger.error("Lỗi: Không tìm thấy file guide.txt!")
            lines = ["# Lỗi", "Không thể đọc file hướng dẫn."]
        except Exception as e:
            logger.error(f"Lỗi khi đọc guide.txt: {e}")
            lines = ["# Lỗi", "Không thể đọc file hướng dẫn."]

        sections = []
        current_title = ""
        current_lines = []
        for line in lines:
            if line.startswith("#"):
                if current_title:
                    sections.append((current_title, current_lines))
                current_title = line[1:].strip()
                current_lines = []
            else:
                current_lines.append(line)
        if current_title:
            sections.append((current_title, current_lines))
        return sections

    def back_to_menu(self, instance):
        if self.manager.has_screen("menu"):
            self.manager.current = "menu"
        else:
            logger.error("menu screen not found in ScreenManager")

    def prev_page(self, instance):
        if self.page > 0:
            self.page -= 1
            self.update_page()

    def next_page(self, instance):
        if self.page < self.total_pages - 1:
            self.page += 1
            self.update_page()

    def update_page(self):
        try:
            self.text_layout.clear_widgets()
            title, lines = self.sections[self.page]
            self.title_label.text = title

            for line in lines:
                lbl = Label(text=line, font_name='retro', font_size=40, color=(1, 1, 1, 1), size_hint_y=None, height=40,
                            halign='left')
                lbl.text_size = (None, None)
                lbl.bind(size=lbl.setter('text_size'))
                self.text_layout.add_widget(lbl)

            num_lines = len(lines)
            if num_lines > 0:
                total_height = (num_lines * 40) + ((num_lines - 1) * 10)
                self.text_layout_container.height = total_height

            self.prev_btn.opacity = 1 if self.page > 0 else 0
            self.prev_btn.disabled = self.page == 0
            self.next_btn.opacity = 1 if self.page < self.total_pages - 1 else 0
            self.next_btn.disabled = self.page >= self.total_pages - 1
            self.page_label.text = f"Trang {self.page + 1}/{self.total_pages}"
            self.page_label.texture_update()
        except Exception as e:
            logger.error(f"Lỗi trong GuideScreen.update_page: {e}")

# === Score Screen ===
class ScoreScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.page = 0
        self.scores_per_page = 5
        self.scores = self.load_scores()
        self.total_pages = max(1, (len(self.scores) + self.scores_per_page - 1) // self.scores_per_page)

        try:
            self.background = Image(source="bg2.png", fit_mode="fill", size=Window.size)
            self.add_widget(self.background)
        except Exception as e:
            logger.error(f"Lỗi khi tải background bg2.png: {e}")

        self.text_layout_container = BoxLayout(orientation='vertical', size_hint=(1, None), height=400,
                                               padding=(50, 50, 100, 300))
        self.text_layout = BoxLayout(orientation='vertical', spacing=30, size_hint_y=None)
        self.text_layout_container.add_widget(self.text_layout)
        self.add_widget(self.text_layout_container)

        self.back_btn = Button(
            text="< Quay lại",
            font_name='retro',
            font_size=20,
            size_hint=(None, None),
            size=(140, 40),
            pos_hint={'x': 0, 'top': 1},
            background_normal='',
            background_down='',
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1)
        )
        self.back_btn.bind(on_press=self.back_to_menu)
        self.add_widget(self.back_btn)

        self.title_label = Label(
            text="Điểm Cao Nhất",
            font_name='retro',
            font_size=34,
            color=(1, 1, 0, 1),
            size_hint_y=None,
            height=50,
            halign='center',
            pos_hint={'top': 1}
        )
        self.add_widget(self.title_label)

        self.main_layout = BoxLayout(orientation='horizontal', padding=[0, 0, 0, 0], spacing=10)
        self.content_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_x=0.5,
                                        pos_hint={'center_x': 0.25})

        self.nav_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=50, spacing=20)
        self.prev_btn = Button(
            text="<",
            font_name='retro',
            font_size=28,
            size_hint=(None, None),
            size=(50, 50),
            background_normal='',
            background_down='',
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1)
        )
        self.prev_btn.bind(on_press=self.prev_page)
        self.page_label = Label(
            text="",
            font_name='retro',
            font_size=20,
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=50,
            halign='center'
        )
        self.next_btn = Button(
            text=">",
            font_name='retro',
            font_size=28,
            size_hint=(None, None),
            size=(50, 50),
            background_normal='',
            background_down='',
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1)
        )
        self.next_btn.bind(on_press=self.next_page)
        self.nav_layout.add_widget(self.prev_btn)
        self.nav_layout.add_widget(self.page_label)
        self.nav_layout.add_widget(self.next_btn)
        self.content_layout.add_widget(self.nav_layout)

        self.main_layout.add_widget(self.content_layout)
        self.add_widget(self.main_layout)

        self.update_page()

    def load_scores(self):
        try:
            with open("score.txt", "r", encoding="utf-8") as f:
                scores = []
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        try:
                            last_space_idx = line.rfind(" ")
                            if last_space_idx == -1:
                                raise ValueError("Không tìm thấy khoảng trắng để tách tên và điểm")
                            name = line[:last_space_idx].strip()
                            score = line[last_space_idx + 1:].strip()
                            scores.append((name, int(score)))
                        except ValueError as e:
                            logger.error(f"Dòng không hợp lệ trong score.txt: {line} ({str(e)})")
                scores.sort(key=lambda x: x[1], reverse=True)
                return scores
        except FileNotFoundError:
            logger.error("Lỗi: Không tìm thấy file score.txt!")
            return [("Không có dữ liệu", 0)]
        except Exception as e:
            logger.error(f"Lỗi khi đọc score.txt: {e}")
            return [("Lỗi khi đọc file", 0)]

    def back_to_menu(self, instance):
        if self.manager.has_screen("menu"):
            self.manager.current = "menu"
        else:
            logger.error("menu screen not found in ScreenManager")

    def prev_page(self, instance):
        if self.page > 0:
            self.page -= 1
            self.update_page()

    def next_page(self, instance):
        if self.page < self.total_pages - 1:
            self.page += 1
            self.update_page()

    def update_page(self):
        try:
            self.text_layout.clear_widgets()
            start_idx = self.page * self.scores_per_page
            end_idx = min(start_idx + self.scores_per_page, len(self.scores))
            page_scores = self.scores[start_idx:end_idx]

            for name, score in page_scores:
                lbl = Label(
                    text=f"{name:<20} {score}",
                    font_name='retro',
                    font_size=40,
                    color=(1, 1, 1, 1),
                    size_hint_y=None,
                    height=40,
                    halign='left'
                )
                lbl.text_size = (None, None)
                lbl.bind(size=lbl.setter('text_size'))
                self.text_layout.add_widget(lbl)

            num_lines = len(page_scores)
            if num_lines > 0:
                total_height = (num_lines * 40) + ((num_lines - 1) * 10)
                self.text_layout_container.height = total_height

            self.prev_btn.opacity = 1 if self.page > 0 else 0
            self.prev_btn.disabled = self.page == 0
            self.next_btn.opacity = 1 if self.page < self.total_pages - 1 else 0
            self.next_btn.disabled = self.page >= self.total_pages - 1
            self.page_label.text = f"Trang {self.page + 1}/{self.total_pages}"
            self.page_label.texture_update()
        except Exception as e:
            logger.error(f"Lỗi trong ScoreScreen.update_page: {e}")

# === Menu Screen ===
class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical')
        try:
            self.background = Image(source="better1.png", fit_mode="fill", size=Window.size)
            self.add_widget(self.background, index=0)
        except Exception as e:
            logger.error(f"Lỗi khi tải background better1.png: {e}")

        spacer = Widget(size_hint=(1, 1))
        self.layout = BoxLayout(
            orientation='vertical',
            padding=10,
            spacing=5,
            size_hint=(1, None),
            height=300
        )
        self.main_layout.add_widget(spacer)
        self.main_layout.add_widget(self.layout)
        self.add_widget(self.main_layout)

        menu_options = [
            ("Chơi", "choi"),
            ("Điểm cao nhất", "diem_cao_nhat"),
            ("Hướng dẫn tân thủ", "huong_dan_tan_thu"),
            ("Di chuyển", "di_chuyen"),
            ("Thoát", "thoat"),
        ]
        for text, method in menu_options:
            btn = HoverButton(
                text=text,
                font_name='retro',
                font_size=40,
                color=(1, 1, 1, 1),
                background_color=(0, 0, 0, 0),
                background_normal='',
                background_down='',
                border=(0, 0, 0, 0),
                padding=(0, 0),
                size_hint=(1, None),
                height=50
            )
            btn.bind(on_press=getattr(self, method))
            btn.bind(on_enter=self.on_button_hover)
            btn.bind(on_leave=self.on_button_leave)
            self.layout.add_widget(btn)

    def on_button_leave(self, instance):
        instance.color = (1, 1, 1, 1)

    def on_button_hover(self, instance):
        instance.color = (1, 1, 0, 1)

    def choi(self, *args):
        if self.manager.has_screen("game"):
            self.manager.current = "game"
        else:
            logger.error("game screen not found in ScreenManager")

    def diem_cao_nhat(self, *args):
        if not self.manager.has_screen("score"):
            self.manager.add_widget(ScoreScreen(name="score"))
        self.manager.current = "score"

    # def toc_do(self, *args):
    #     if not self.manager.has_screen("info_speed"):
    #         self.manager.add_widget(InfoScreen("Tốc Độ", "Tốc độ: 60 FPS", name="info_speed"))
    #     self.manager.current = "info_speed"

    def huong_dan_tan_thu(self, *args):
        if not self.manager.has_screen("guide"):
            self.manager.add_widget(GuideScreen(name="guide"))
        self.manager.current = "guide"

    def di_chuyen(self, *args):
        if not self.manager.has_screen("info_move"):
            self.manager.add_widget(
                InfoScreen("Cách Di Chuyển", "WASD hoặc mũi tên, Shift để tăng tốc.", name="info_move"))
        self.manager.current = "info_move"

    def thoat(self, *args):
        App.get_running_app().stop()

# === SpaceMax App ===
class SpaceMaxApp(App):
    def build(self):
        Window.size = (720, 640)
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(GameScreen(name="game"))
        sm.add_widget(GameOverScreen(name="game_over"))
        sm.bind(on_current=self.on_screen_change)
        return sm

    def debug_clock(self, dt):
        pass

    def on_screen_change(self, instance, value):
        if not instance.has_screen(value):
            logger.error(f"Attempted to switch to non-existent screen: {value}")

if __name__ == "__main__":
    SpaceMaxApp().run()

import os
import sys
import math
import struct
import random
import glob
import pygame

# Opsiyonel Video Oynatıcı Kontrolleri
HAS_PYVIDPLAYER = False
try:
    from pyvidplayer2 import Video
    HAS_PYVIDPLAYER = True
except ImportError:
    HAS_PYVIDPLAYER = False

HAS_CV2 = False
try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

# Opsiyonel yerel (çevrimdışı) metin-okuma motoru: "GOOOOL!" bağırışı için.
# Kurulu değilse veya sistemde bir TTS motoru bulunamazsa sessizce devre dışı kalır,
# oyun sentezlenmiş "kalabalık tezahüratı" sesiyle devam eder.
HAS_PYTTSX3 = False
try:
    import pyttsx3
    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False

# -------------------------------------------------------------
# 1. GENEL SABİTLER VE AYARLAR
# -------------------------------------------------------------
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FPS = 60

# Renk Tanımları (RGB)
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GRAY = (70, 70, 70)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (40, 40, 40)
GREEN_FIELD = (46, 139, 87)
GREEN_FIELD_DARK = (34, 110, 68)
LINE_WHITE = (240, 240, 240)
SKY_BLUE = (135, 206, 235)
YELLOW = (255, 215, 0)
RED = (220, 50, 50)
ORANGE = (255, 140, 0)
CLEAT_BLACK = (18, 18, 18)
CLEAT_STUD = (225, 225, 230)
BLUE_ACCENT = (41, 128, 185)
POWER_PINK = (255, 60, 200)

# Takım ve Renk Veritabanı
LIGLER = {
    "Türkiye": [
        {"ad": "Galatasaray", "kod": "gs", "renk1": (169, 4, 50), "renk2": (253, 185, 19)},
        {"ad": "Fenerbahçe", "kod": "fb", "renk1": (0, 45, 114), "renk2": (254, 209, 0)},
        {"ad": "Beşiktaş", "kod": "bjk", "renk1": (255, 255, 255), "renk2": (10, 10, 10)},
        {"ad": "Trabzonspor", "kod": "ts", "renk1": (128, 0, 32), "renk2": (114, 182, 226)},
    ],
    "İspanya": [
        {"ad": "Real Madrid", "kod": "real", "renk1": (245, 245, 245), "renk2": (218, 165, 32)},
        {"ad": "Barcelona", "kod": "barca", "renk1": (0, 77, 152), "renk2": (165, 0, 52)},
        {"ad": "Atletico Madrid", "kod": "atletico", "renk1": (203, 53, 36), "renk2": (39, 64, 139)},
    ],
    "Fransa": [
        {"ad": "Paris SG", "kod": "psg", "renk1": (0, 65, 112), "renk2": (218, 41, 28)},
        {"ad": "Marseille", "kod": "om", "renk1": (240, 240, 240), "renk2": (33, 150, 243)},
        {"ad": "Monaco", "kod": "monaco", "renk1": (227, 6, 19), "renk2": (255, 255, 255)},
    ],
    "İngiltere": [
        {"ad": "Manchester City", "kod": "mancity", "renk1": (108, 171, 221), "renk2": (255, 255, 255)},
        {"ad": "Manchester United", "kod": "manutd", "renk1": (218, 41, 28), "renk2": (10, 10, 10)},
        {"ad": "Tottenham", "kod": "tottenham", "renk1": (255, 255, 255), "renk2": (19, 34, 87)},
        {"ad": "Chelsea", "kod": "chelsea", "renk1": (3, 70, 148), "renk2": (255, 255, 255)},
    ]
}

# -------------------------------------------------------------
# 2. VİDEO YÖNETİMİ VE ÖNBELLEKLEME
# -------------------------------------------------------------
VIDEO_EXTENSIONS = ("*.mp4", "*.avi", "*.mov", "*.mkv", "*.webm", "*.wmv")
VIDEO_CACHE = {}

def init_video_folders():
    base = "videolar"
    takimlar = ["fenerbahce", "galatasaray", "besiktas", "trabzonspor", "genel"]
    for t in takimlar:
        os.makedirs(os.path.join(base, "gol", t), exist_ok=True)
        os.makedirs(os.path.join(base, "mac_sonu", t), exist_ok=True)
    os.makedirs(os.path.join(base, "mac_sonu", "beraberlik"), exist_ok=True)

init_video_folders()

def scan_videos():
    global VIDEO_CACHE
    base = "videolar"
    VIDEO_CACHE.clear()
    for root, _, _ in os.walk(base):
        files = []
        for ext in VIDEO_EXTENSIONS:
            files.extend(glob.glob(os.path.join(root, ext)))
            files.extend(glob.glob(os.path.join(root, ext.upper())))
        if files:
            VIDEO_CACHE[os.path.normpath(root)] = list(set(files))

scan_videos()

def get_random_video(category, team_code_or_name):
    base = "videolar"
    slug = team_code_or_name.lower().replace("ç", "c").replace("ş", "s").replace("ı", "i").replace("ğ", "g")

    folder_candidates = [
        os.path.normpath(os.path.join(base, category, slug)),
        os.path.normpath(os.path.join(base, category, "fenerbahce" if "fener" in slug or "fb" in slug else "")),
        os.path.normpath(os.path.join(base, category, "galatasaray" if "gala" in slug or "gs" in slug else "")),
        os.path.normpath(os.path.join(base, category, "besiktas" if "besik" in slug or "bjk" in slug else "")),
        os.path.normpath(os.path.join(base, category, "trabzonspor" if "trab" in slug or "ts" in slug else "")),
        os.path.normpath(os.path.join(base, category, "genel"))
    ]

    all_files = []
    for folder in folder_candidates:
        if folder in VIDEO_CACHE:
            all_files.extend(VIDEO_CACHE[folder])

    if all_files:
        return random.choice(all_files)
    return None

# -------------------------------------------------------------
# 3. DİNAMİK SES YÖNETİCİSİ (Güçlendirilmiş + GOOOOL sesi)
# -------------------------------------------------------------
class SoundManager:
    def __init__(self):
        self.enabled = False
        self.kick_sound = None
        self.shot_sound = None
        self.goal_sound = None
        self.post_sound = None
        self.header_sound = None
        self.whistle_sound = None
        self.tick_sound = None
        self.crowd_cheer_sound = None
        self.crowd_ooh_sound = None
        self.goal_voice_sound = None

        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            try:
                pygame.mixer.set_num_channels(16)
            except Exception:
                pass
            self.enabled = True
            # Darbe (vuruş) sesleri: ton + kısa gürültü katmanı (daha "dolgun" his)
            self.kick_sound = self._gen_tone(170, 0.09, drop=True, noise_amt=0.30)
            self.shot_sound = self._gen_tone(310, 0.17, drop=True, noise_amt=0.42)
            self.header_sound = self._gen_tone(440, 0.13, drop=True, noise_amt=0.22)
            self.post_sound = self._gen_metal_hit()
            self.goal_sound = self._gen_fanfare()
            self.whistle_sound = self._gen_whistle()
            self.tick_sound = self._gen_tone(900, 0.07, drop=False, noise_amt=0.05)
            self.crowd_cheer_sound = self._gen_noise_burst(1.1, envelope="rise_fall")
            self.crowd_ooh_sound = self._gen_noise_burst(0.45, envelope="dip")
            self.goal_voice_sound = self._gen_voice_shout("Goooool!")
        except Exception:
            self.enabled = False

    def _gen_tone(self, freq, duration, drop=False, noise_amt=0.0):
        try:
            sample_rate = 22050
            n_samples = int(sample_rate * duration)
            buf = bytearray()
            for i in range(n_samples):
                t = float(i) / sample_rate
                f = freq * (1.0 - 0.6 * (float(i) / n_samples)) if drop else freq
                progress = float(i) / n_samples
                amp = 0.5 * (1.0 - progress)
                tone_val = math.sin(2 * math.pi * f * t)
                noise_val = random.uniform(-1.0, 1.0) * noise_amt * math.exp(-6.0 * progress)
                val = int(amp * 32767 * (tone_val + noise_val))
                val = max(-32768, min(32767, val))
                buf.extend(struct.pack('<h', val))
            return pygame.mixer.Sound(buffer=bytes(buf))
        except Exception:
            return None

    def _gen_metal_hit(self):
        try:
            sample_rate = 22050
            duration = 0.18
            n_samples = int(sample_rate * duration)
            buf = bytearray()
            for i in range(n_samples):
                t = float(i) / sample_rate
                amp = 0.46 * math.exp(-12 * t)
                val = int(amp * 32767 * (0.6 * math.sin(2 * math.pi * 580 * t) + 0.4 * math.sin(2 * math.pi * 840 * t)))
                val = max(-32768, min(32767, val))
                buf.extend(struct.pack('<h', val))
            return pygame.mixer.Sound(buffer=bytes(buf))
        except Exception:
            return None

    def _gen_fanfare(self):
        try:
            sample_rate = 22050
            duration = 0.5
            n_samples = int(sample_rate * duration)
            buf = bytearray()
            notes = [523.25, 659.25, 783.99, 1046.50]
            step = n_samples // len(notes)
            for i in range(n_samples):
                idx = min(len(notes) - 1, i // step)
                f = notes[idx]
                t = float(i) / sample_rate
                amp = 0.42 * (1.0 - 0.15 * (float(i % step) / step))
                val = int(amp * 32767 * math.sin(2 * math.pi * f * t))
                val = max(-32768, min(32767, val))
                buf.extend(struct.pack('<h', val))
            return pygame.mixer.Sound(buffer=bytes(buf))
        except Exception:
            return None

    def _gen_whistle(self):
        try:
            sample_rate = 22050
            duration = 0.35
            n_samples = int(sample_rate * duration)
            buf = bytearray()
            for i in range(n_samples):
                t = float(i) / sample_rate
                progress = i / n_samples
                f = 2100.0 if progress < 0.55 else 1700.0
                if progress < 0.85:
                    amp = 0.5
                else:
                    amp = 0.5 * (1.0 - (progress - 0.85) / 0.15)
                val = int(amp * 32767 * math.sin(2 * math.pi * f * t))
                val = max(-32768, min(32767, val))
                buf.extend(struct.pack('<h', val))
            return pygame.mixer.Sound(buffer=bytes(buf))
        except Exception:
            return None

    def _gen_noise_burst(self, duration, envelope="rise_fall"):
        # Kalabalık uğultusu / "ooh" tepkisi: filtrelenmiş beyaz gürültü
        try:
            sample_rate = 22050
            n_samples = int(sample_rate * duration)
            raw = [random.uniform(-1.0, 1.0) for _ in range(n_samples)]

            filtered = []
            window = 6
            for i in range(n_samples):
                lo = max(0, i - window)
                hi = min(n_samples, i + window)
                filtered.append(sum(raw[lo:hi]) / (hi - lo))

            buf = bytearray()
            for i in range(n_samples):
                progress = i / n_samples
                if envelope == "rise_fall":
                    if progress < 0.2:
                        amp = 0.36 * (progress / 0.2)
                    elif progress < 0.7:
                        amp = 0.36
                    else:
                        amp = 0.36 * (1.0 - (progress - 0.7) / 0.3)
                else:
                    amp = 0.42 * math.sin(math.pi * progress)

                val = int(amp * 32767 * filtered[i])
                val = max(-32768, min(32767, val))
                buf.extend(struct.pack('<h', val))
            return pygame.mixer.Sound(buffer=bytes(buf))
        except Exception:
            return None

    def _gen_voice_shout(self, text):
        # Çevrimdışı sistem TTS motoruyla (varsa) gerçek "GOOOOL!" bağırışı üretir.
        # pyttsx3 / sistem motoru yoksa None döner; oyun crowd_cheer_sound ile devam eder.
        if not HAS_PYTTSX3:
            return None
        tmp_path = os.path.join(os.getcwd(), "_gooool_tmp.wav")
        try:
            engine = pyttsx3.init()
            try:
                engine.setProperty('rate', 130)
                engine.setProperty('volume', 1.0)
            except Exception:
                pass
            engine.save_to_file(text, tmp_path)
            engine.runAndWait()
            if os.path.exists(tmp_path):
                snd = pygame.mixer.Sound(tmp_path)
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
                return snd
        except Exception:
            return None
        return None

    def play(self, sound):
        if self.enabled and sound:
            try:
                sound.play()
            except Exception:
                pass

# -------------------------------------------------------------
# 4. YÜZ, KRAMPON, TOP VE GÖLGE ÇİZİMLERİ (GÜVENLİ & OPTİMİZE)
# -------------------------------------------------------------
def load_face_images():
    faces = {}
    os.makedirs("resimler", exist_ok=True)
    meme_expressions = ["B-)", ":D", "XD", ">:(", ":3"]

    for i in range(1, 6):
        path = os.path.join("resimler", f"yuz{i}.png")
        if os.path.exists(path):
            try:
                img = pygame.image.load(path)
                try:
                    img = img.convert_alpha()
                except Exception:
                    pass
                img = pygame.transform.smoothscale(img, (70, 70))
                faces[i] = img
            except Exception:
                faces[i] = None
        else:
            faces[i] = None

        if faces[i] is None:
            surf = pygame.Surface((70, 70), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255, 220, 150), (35, 35), 33)
            pygame.draw.circle(surf, BLACK, (35, 35), 33, 2)
            font_mim = pygame.font.SysFont("arial", 20, bold=True)
            text_surf = font_mim.render(meme_expressions[i - 1], True, BLACK)
            t_rect = text_surf.get_rect(center=(35, 35))
            surf.blit(text_surf, t_rect)
            try:
                faces[i] = surf.convert_alpha()
            except Exception:
                faces[i] = surf

    return faces

# Display açıldıktan sonra ilk ihtiyaç anında güvenle oluşturulur
_BASE_CLEAT_SURF = None

def get_base_cleat_surf():
    global _BASE_CLEAT_SURF
    if _BASE_CLEAT_SURF is None:
        surf = pygame.Surface((34, 18), pygame.SRCALPHA)
        body_poly = [(4, 3), (18, 2), (28, 6), (32, 11), (28, 14), (6, 14), (3, 10)]
        pygame.draw.polygon(surf, CLEAT_BLACK, body_poly)
        pygame.draw.polygon(surf, BLACK, body_poly, 1)
        pygame.draw.line(surf, WHITE, (12, 5), (20, 8), 2)
        pygame.draw.line(surf, LIGHT_GRAY, (14, 8), (22, 11), 1)
        for sx, sy in [(8, 14), (16, 14), (24, 14)]:
            pygame.draw.rect(surf, CLEAT_STUD, (sx, sy, 3, 3))
        try:
            _BASE_CLEAT_SURF = surf.convert_alpha()
        except Exception:
            _BASE_CLEAT_SURF = surf
    return _BASE_CLEAT_SURF

def render_cleat(facing_right=True, angle=0.0):
    surf = get_base_cleat_surf()
    if not facing_right:
        surf = pygame.transform.flip(surf, True, False)
    if angle != 0:
        surf = pygame.transform.rotate(surf, angle)
    return surf

_BASE_BALL_SURF = None

def get_base_ball_surf(radius):
    global _BASE_BALL_SURF
    if _BASE_BALL_SURF is None:
        d = radius * 2
        surf = pygame.Surface((d, d), pygame.SRCALPHA)
        cx, cy = radius, radius
        pygame.draw.circle(surf, WHITE, (cx, cy), radius)
        pygame.draw.circle(surf, BLACK, (cx, cy), radius, 2)
        pygame.draw.polygon(surf, BLACK, [
            (cx, cy - 6),
            (cx + 6, cy - 2),
            (cx + 4, cy + 5),
            (cx - 4, cy + 5),
            (cx - 6, cy - 2)
        ])
        pygame.draw.circle(surf, BLACK, (cx - 10, cy - 9), 3)
        pygame.draw.circle(surf, BLACK, (cx + 11, cy - 8), 3)
        pygame.draw.circle(surf, BLACK, (cx - 2, cy + 12), 3)
        try:
            _BASE_BALL_SURF = surf.convert_alpha()
        except Exception:
            _BASE_BALL_SURF = surf
    return _BASE_BALL_SURF

_BASE_SHADOW_SURF = None

def get_shadow_surf():
    global _BASE_SHADOW_SURF
    if _BASE_SHADOW_SURF is None:
        surf = pygame.Surface((60, 24), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (0, 0, 0, 95), (0, 0, 60, 24))
        try:
            _BASE_SHADOW_SURF = surf.convert_alpha()
        except Exception:
            _BASE_SHADOW_SURF = surf
    return _BASE_SHADOW_SURF

def draw_shadow(screen, x, ground_y, height_off_ground, base_w=54, base_h=20):
    shadow = get_shadow_surf()
    height_off_ground = max(0.0, height_off_ground)
    scale = max(0.35, 1.0 - min(height_off_ground, 200) / 220.0)
    w = max(6, int(base_w * scale))
    h = max(3, int(base_h * scale))
    scaled = pygame.transform.scale(shadow, (w, h))
    rect = scaled.get_rect(center=(int(x), int(ground_y)))
    screen.blit(scaled, rect)

# -------------------------------------------------------------
# 5. TUŞ İSİMLENDİRME YARDIMCISI
# -------------------------------------------------------------
KEY_NAMES = {
    pygame.K_UP: "Yukarı Ok",
    pygame.K_DOWN: "Aşağı Ok",
    pygame.K_LEFT: "Sol Ok",
    pygame.K_RIGHT: "Sağ Ok",
    pygame.K_SPACE: "Boşluk",
    pygame.K_PERIOD: ".",
    pygame.K_COMMA: ",",
    pygame.K_KP0: "Num 0",
    pygame.K_KP1: "Num 1",
    pygame.K_KP2: "Num 2",
    pygame.K_KP3: "Num 3",
    pygame.K_KP4: "Num 4",
    pygame.K_KP5: "Num 5",
    pygame.K_KP6: "Num 6",
    pygame.K_KP7: "Num 7",
    pygame.K_KP8: "Num 8",
    pygame.K_KP9: "Num 9",
    pygame.K_RETURN: "Enter",
    pygame.K_LSHIFT: "Sol Shift",
    pygame.K_RSHIFT: "Sağ Shift",
    pygame.K_LCTRL: "Sol Ctrl",
    pygame.K_RCTRL: "Sağ Ctrl",
}

def get_key_display_name(key_code):
    if key_code in KEY_NAMES:
        return KEY_NAMES[key_code]
    name = pygame.key.name(key_code)
    return name.upper() if name else f"Tuş {key_code}"

# -------------------------------------------------------------
# 6. ÖZEL GÜÇLER TANIMI
# -------------------------------------------------------------
POWER_OPTIONS = [
    {"id": "freeze_enemy", "name": "Adamı Dondurma"},
    {"id": "shrink_own_goal", "name": "Kendi Kaleni Küçültme"},
    {"id": "enlarge_enemy_goal", "name": "Rakip Kaleyi Büyütme"},
    {"id": "giant", "name": "Dev Adam"},
    {"id": "freeze_ball", "name": "Topu Dondurma"},
    {"id": "super_shot", "name": "Süper Hızlı Atış"},
    {"id": "invert_controls", "name": "Rakip Kontrolleri Ters Çevirme"},
]
POWER_NAMES = {p["id"]: p["name"] for p in POWER_OPTIONS}

# -------------------------------------------------------------
# 7. OYUNCU, TOP VE KALE FİZİĞİ
# -------------------------------------------------------------
class Player:
    def __init__(self, x, y, is_p1=True):
        self.start_x = x
        self.start_y = y
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.is_p1 = is_p1
        self.on_ground = False
        self.just_landed = False

        self.base_radius_head = 32
        self.base_body_w = 44
        self.base_body_h = 42
        self.radius_head = self.base_radius_head
        self.body_w = self.base_body_w
        self.body_h = self.base_body_h

        self.speed = 5.8
        self.jump_power = -13.5
        self.gravity = 0.65

        self.face_id = 1 if is_p1 else 2
        self.team = LIGLER["Türkiye"][0 if is_p1 else 1]

        self.shot_cooldown = 0
        self.walk_anim = 0.0
        self.kick_timer = 0
        self.kick_type = "high"
        self.ai_timer = 0

        # Özel güç durumu
        self.power_id = None
        self.power_cooldown_timer = 0
        self.frozen_timer = 0
        self.invert_timer = 0
        self.giant_timer = 0
        self.super_shot_timer = 0
        self.scale = 1.0

    def reset_position(self):
        self.x = float(self.start_x)
        self.y = float(self.start_y)
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.just_landed = False
        self.kick_timer = 0
        self.walk_anim = 0.0
        self.ai_timer = 0

    def reset_powers(self):
        self.power_cooldown_timer = 0
        self.frozen_timer = 0
        self.invert_timer = 0
        self.giant_timer = 0
        self.super_shot_timer = 0
        self.scale = 1.0
        self.radius_head = self.base_radius_head
        self.body_w = self.base_body_w
        self.body_h = self.base_body_h

    def trigger_kick(self, kick_type="high"):
        self.kick_timer = 15
        self.kick_type = kick_type

    def _tick_shared_timers(self):
        if self.shot_cooldown > 0:
            self.shot_cooldown -= 1
        if self.kick_timer > 0:
            self.kick_timer -= 1
        if self.power_cooldown_timer > 0:
            self.power_cooldown_timer -= 1
        if self.super_shot_timer > 0:
            self.super_shot_timer -= 1
        if self.giant_timer > 0:
            self.giant_timer -= 1
            if self.giant_timer == 0:
                self.scale = 1.0
        self.radius_head = self.base_radius_head * self.scale
        self.body_w = self.base_body_w * self.scale
        self.body_h = self.base_body_h * self.scale

    def update_human(self, keys, bindings, ground_y, left_limit, right_limit):
        self._tick_shared_timers()

        if self.frozen_timer > 0:
            self.frozen_timer -= 1
            self.vx = 0.0
            self._apply_motion(ground_y, left_limit, right_limit)
            return

        invert = self.invert_timer > 0
        if invert:
            self.invert_timer -= 1

        sol_pressed = keys[bindings["sol"]]
        sag_pressed = keys[bindings["sag"]]
        if invert:
            sol_pressed, sag_pressed = sag_pressed, sol_pressed

        target_vx = 0.0
        if sol_pressed:
            target_vx = -self.speed
        if sag_pressed:
            target_vx = self.speed

        # İvmeli hareket: anlık zıplama yerine hafif momentum hissi
        self.vx += (target_vx - self.vx) * 0.45
        if abs(self.vx) < 0.15:
            self.vx = 0.0

        if keys[bindings["zipla"]] and self.on_ground:
            self.vy = self.jump_power
            self.on_ground = False

        self._apply_motion(ground_y, left_limit, right_limit)

    def update_bot(self, ball, difficulty, ground_y, left_limit, right_limit, sound_mgr):
        self._tick_shared_timers()

        if self.frozen_timer > 0:
            self.frozen_timer -= 1
            self._apply_motion(ground_y, left_limit, right_limit)
            return

        self.ai_timer += 1

        if difficulty == "Kolay":
            bot_speed = 3.8
            reaction_mod = 12
            jump_prob = 0.25
            shot_distance = 65
        elif difficulty == "Orta":
            bot_speed = 5.2
            reaction_mod = 6
            jump_prob = 0.65
            shot_distance = 80
        else:  # Zor
            bot_speed = 6.3
            reaction_mod = 2
            jump_prob = 0.95
            shot_distance = 92

        target_x = 750.0
        if ball.x > self.x:
            target_x = 880.0
        elif ball.x > 380:
            target_x = ball.x + 35.0
        else:
            target_x = 650.0

        target_vx = 0.0
        if abs(self.x - target_x) > 8:
            target_vx = bot_speed if self.x < target_x else -bot_speed

        if self.invert_timer > 0:
            self.invert_timer -= 1
            target_vx = -target_vx

        self.vx += (target_vx - self.vx) * 0.4
        if abs(self.vx) < 0.15:
            self.vx = 0.0

        dist_to_ball = math.hypot(ball.x - self.x, ball.y - self.y)
        if self.on_ground:
            ball_overhead = (abs(ball.x - self.x) < 55) and (ball.y < self.y - 40)
            if ball_overhead and (random.random() < jump_prob):
                self.vy = self.jump_power
                self.on_ground = False

        if dist_to_ball < shot_distance and self.shot_cooldown <= 0:
            if self.ai_timer % reaction_mod == 0:
                boost = 1.55 if self.super_shot_timer > 0 else 1.0
                if ball.y < self.y - 20:
                    self.trigger_kick("high")
                    ball.vx = -14.5 * boost
                    ball.vy = -12.5 * boost
                    ball.spin = -random.uniform(2.0, 4.2)
                else:
                    self.trigger_kick("low")
                    ball.vx = -18.0 * boost
                    ball.vy = -3.2 * boost
                    ball.spin = -random.uniform(1.0, 2.6)
                self.shot_cooldown = 20
                sound_mgr.play(sound_mgr.shot_sound)

        self._apply_motion(ground_y, left_limit, right_limit)

    def _apply_motion(self, ground_y, left_limit, right_limit):
        if abs(self.vx) > 0.3 and self.on_ground:
            self.walk_anim += 0.32
        else:
            self.walk_anim = 0.0

        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy

        self.just_landed = False
        if self.y >= ground_y:
            if not self.on_ground:
                self.just_landed = True
            self.y = ground_y
            self.vy = 0.0
            self.on_ground = True

        half_w = self.body_w / 2
        if self.x - half_w < left_limit:
            self.x = left_limit + half_w
        if self.x + half_w > right_limit:
            self.x = right_limit - half_w

    def get_head_center(self):
        return (int(self.x), int(self.y - self.body_h - self.radius_head + 8))

    def get_hitbox(self):
        hx, hy = self.get_head_center()
        top_y = hy - self.radius_head
        height = (self.y - top_y) + 14
        return pygame.Rect(int(self.x - self.body_w / 2), int(top_y), self.body_w, int(height))

    def get_foot_transform(self):
        base_offset_x = 10 if self.is_p1 else -10
        foot_x = self.x + base_offset_x
        foot_y = self.y + 4
        foot_angle = 0.0

        if self.kick_timer > 0:
            progress = math.sin(((15 - self.kick_timer) / 15.0) * math.pi)
            reach_x = 25.0 * (1.0 if self.is_p1 else -1.0) * progress
            reach_y = (-24.0 if self.kick_type == "high" else -12.0) * progress
            foot_x += reach_x
            foot_y += reach_y
            foot_angle = (38.0 if self.is_p1 else -38.0) * progress
        elif self.walk_anim != 0.0:
            foot_x += math.sin(self.walk_anim) * 9.0
            foot_y += -abs(math.cos(self.walk_anim)) * 3.5
            foot_angle = math.sin(self.walk_anim) * 14.0 * (1.0 if self.is_p1 else -1.0)

        return foot_x, foot_y, foot_angle

    def draw(self, screen, face_images, ground_y):
        draw_shadow(screen, self.x, ground_y, max(0.0, ground_y - self.y))

        hx, hy = self.get_head_center()

        body_rect = pygame.Rect(int(self.x - self.body_w / 2), int(self.y - self.body_h), int(self.body_w), int(self.body_h))
        pygame.draw.rect(screen, self.team["renk1"], body_rect, border_radius=8)
        stripe_rect = pygame.Rect(int(self.x - 6 * self.scale), int(self.y - self.body_h), int(12 * self.scale), int(self.body_h))
        pygame.draw.rect(screen, self.team["renk2"], stripe_rect)
        pygame.draw.rect(screen, BLACK, body_rect, 2, border_radius=8)

        fx, fy, angle = self.get_foot_transform()
        cleat_img = render_cleat(facing_right=self.is_p1, angle=angle)
        c_rect = cleat_img.get_rect(center=(int(fx), int(fy)))
        screen.blit(cleat_img, c_rect)

        face_img = face_images.get(self.face_id)
        if face_img:
            img_to_draw = face_img
            if not self.is_p1:
                img_to_draw = pygame.transform.flip(face_img, True, False)
            if abs(self.scale - 1.0) > 0.01:
                size = max(10, int(70 * self.scale))
                img_to_draw = pygame.transform.smoothscale(img_to_draw, (size, size))
            f_rect = img_to_draw.get_rect(center=(hx, hy))
            screen.blit(img_to_draw, f_rect)
        else:
            pygame.draw.circle(screen, (255, 220, 160), (hx, hy), int(self.radius_head))
            pygame.draw.circle(screen, BLACK, (hx, hy), int(self.radius_head), 2)

        if self.frozen_timer > 0:
            ice_surf = pygame.Surface((int(self.body_w) + 20, int(self.body_h) + int(self.radius_head * 2) + 16), pygame.SRCALPHA)
            ice_surf.fill((150, 225, 255, 90))
            ice_rect = ice_surf.get_rect(center=(int(self.x), int(self.y - self.body_h / 2)))
            screen.blit(ice_surf, ice_rect)


class Ball:
    def __init__(self, x, y):
        self.start_x = x
        self.start_y = y
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.spin = 0.0
        self.rotation = 0.0
        self.stall_frames = 0
        self.radius = 16
        self.gravity = 0.42
        self.friction = 0.988
        self.bounce = 0.74

    def reset_position(self):
        self.x = float(self.start_x)
        self.y = float(self.start_y)
        self.vx = 0.0
        self.vy = -3.0
        self.spin = 0.0
        self.rotation = 0.0
        self.stall_frames = 0

    def update(self, ground_y, left_limit, right_limit, ceiling_y=25):
        self.vy += self.gravity
        self.vx *= self.friction

        airborne = (self.y + self.radius) < (ground_y - 1)
        if airborne and self.spin != 0.0:
            # Magnus benzeri hafif kavis etkisi (kavisli şutlar)
            self.vy += self.spin * 0.012
            self.spin *= 0.985
        else:
            self.spin *= 0.9

        self.rotation = (self.rotation + self.vx * 3.2 + self.spin * 1.2) % 360

        self.x += self.vx
        self.y += self.vy

        if self.y + self.radius >= ground_y:
            self.y = ground_y - self.radius
            self.vy = -self.vy * self.bounce
            if abs(self.vy) < 1.0:
                self.vy = 0.0
            self.spin *= 0.6

        if self.y - self.radius <= ceiling_y:
            self.y = ceiling_y + self.radius
            self.vy = abs(self.vy) * self.bounce

        if self.x - self.radius <= left_limit:
            self.x = left_limit + self.radius
            self.vx = abs(self.vx) * self.bounce
        elif self.x + self.radius >= right_limit:
            self.x = right_limit - self.radius
            self.vx = -abs(self.vx) * self.bounce

    def draw(self, screen, ground_y):
        draw_shadow(screen, self.x, ground_y, max(0.0, (ground_y - self.radius) - self.y), base_w=34, base_h=14)

        base = get_base_ball_surf(self.radius)
        rotated = pygame.transform.rotate(base, self.rotation)
        rect = rotated.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(rotated, rect)


# -------------------------------------------------------------
# 7.5 PARTİKÜL SİSTEMİ (toz / konfeti)
# -------------------------------------------------------------
class Particle:
    def __init__(self, x, y, vx, vy, life, color, size, gravity=0.2):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = max(1, life)
        self.color = color
        self.size = size
        self.gravity = gravity

    def update(self):
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        return self.life > 0

    def draw(self, screen):
        ratio = max(0.0, self.life / self.max_life)
        s = max(1, int(self.size * ratio))
        rect = pygame.Rect(int(self.x - s / 2), int(self.y - s / 2), s, s)
        pygame.draw.rect(screen, self.color, rect)


class Goal:
    def __init__(self, x, y, width, height, is_left=True):
        self.x = x
        self.base_height = height
        self.bottom_ref = y + height
        self.y = y
        self.width = width
        self.height = height
        self.is_left = is_left
        self.post_thickness = 10

        self.tip_x = (x + width) if is_left else x
        self.tip_y = y + self.post_thickness / 2

    def set_height_scale(self, scale):
        self.height = self.base_height * scale
        self.y = self.bottom_ref - self.height
        self.tip_y = self.y + self.post_thickness / 2

    def resolve_crossbar_collision(self, ball, sound_mgr):
        hit_post = False
        goal_top_y = self.y
        in_goal_x = (self.x - 10 <= ball.x <= self.x + self.width + 10)

        if in_goal_x and (ball.y < self.y + self.post_thickness) and (ball.y + ball.radius >= goal_top_y):
            ball.y = goal_top_y - ball.radius
            ball.vy = -abs(ball.vy) * ball.bounce
            if abs(ball.vy) < 1.6:
                ball.vy = -1.6  # Direğin tepesinde asla tamamen durmasın
            hit_post = True
            ball.stall_frames += 1
            if ball.stall_frames > 10:
                # Sıkışmayı kır: birkaç kare üst üste direkte takılırsa yana doğru güçlü it
                nudge_dir = random.choice([-1.0, 1.0])
                ball.vx += nudge_dir * random.uniform(3.0, 5.0)
                ball.vy = -abs(ball.vy) - 2.5
                ball.stall_frames = 0
        else:
            ball.stall_frames = 0

        dx = ball.x - self.tip_x
        dy = ball.y - self.tip_y
        dist = math.hypot(dx, dy)
        min_dist = ball.radius + 6

        if dist < min_dist and dist > 0:
            nx = dx / dist
            ny = dy / dist
            overlap = min_dist - dist
            ball.x += nx * overlap
            ball.y += ny * overlap

            speed = math.hypot(ball.vx, ball.vy)
            bounce_speed = max(speed * 0.8, 6.0)
            ball.vx = nx * bounce_speed
            ball.vy = ny * bounce_speed
            hit_post = True

        if self.x <= ball.x <= self.x + self.width:
            crossbar_bottom = self.y + self.post_thickness
            if crossbar_bottom <= ball.y - ball.radius <= crossbar_bottom + 8 and ball.vy < 0:
                ball.y = crossbar_bottom + ball.radius
                ball.vy = abs(ball.vy) * ball.bounce
                hit_post = True

        if hit_post:
            sound_mgr.play(sound_mgr.post_sound)

        return hit_post

    def is_goal(self, ball):
        strictly_under_crossbar = (ball.y - ball.radius > self.y + self.post_thickness)
        above_ground = (ball.y + ball.radius <= 515)

        if not (strictly_under_crossbar and above_ground):
            return False

        if self.is_left:
            return (ball.x + ball.radius < self.x + self.width)
        else:
            return (ball.x - ball.radius > self.x)


def resolve_players_collision(p1, p2):
    rect1 = p1.get_hitbox()
    rect2 = p2.get_hitbox()

    if rect1.colliderect(rect2):
        dx = p2.x - p1.x
        dy = p2.y - p1.y

        if abs(dy) > abs(dx) and dy != 0:
            if dy > 0:
                p1.y = rect2.top + p1.body_h / 2
                p1.vy = 0
                p1.on_ground = True
            else:
                p2.y = rect1.top + p2.body_h / 2
                p2.vy = 0
                p2.on_ground = True
        else:
            overlap = (rect1.width / 2 + rect2.width / 2) - abs(dx)
            if overlap > 0:
                push = overlap / 2.0
                if dx > 0:
                    p1.x -= push
                    p2.x += push
                else:
                    p1.x += push
                    p2.x -= push


def resolve_player_ball_collision(player, ball, sound_mgr, game=None):
    hx, hy = player.get_head_center()
    dist_x = ball.x - hx
    dist_y = ball.y - hy
    distance = math.hypot(dist_x, dist_y)
    min_dist = player.radius_head + ball.radius

    if distance < min_dist and distance > 0:
        nx = dist_x / distance
        ny = dist_y / distance
        overlap = min_dist - distance
        ball.x += nx * overlap
        ball.y += ny * overlap

        rel_vel = (ball.vx - player.vx) * nx + (ball.vy - player.vy) * ny
        if rel_vel < 0:
            # Zıplayarak yapılan kafa vuruşu daha güçlü olur
            header_power = 1.35 if not player.on_ground else 1.0
            impulse = -1.4 * rel_vel * header_power
            ball.vx += nx * impulse + player.vx * 0.4
            ball.vy += ny * impulse + player.vy * 0.4
            ball.spin = player.vx * 0.4 + random.uniform(-1.0, 1.0)
            sound_mgr.play(sound_mgr.header_sound if sound_mgr.header_sound else sound_mgr.kick_sound)

            if game is not None and game.commentary_cooldown <= 0 and random.random() < 0.35:
                game.show_commentary(random.choice(game.header_quotes), 80, WHITE)
                game.commentary_cooldown = 70
        return

    body_box = pygame.Rect(
        int(player.x - player.body_w / 2),
        int(player.y - player.body_h),
        int(player.body_w),
        int(player.body_h) + 10
    )

    closest_x = max(body_box.left, min(ball.x, body_box.right))
    closest_y = max(body_box.top, min(ball.y, body_box.bottom))
    dx = ball.x - closest_x
    dy = ball.y - closest_y
    dist_sq = dx * dx + dy * dy

    if dist_sq < ball.radius * ball.radius:
        dist_box = math.sqrt(dist_sq) if dist_sq > 0 else 1.0
        nx = dx / dist_box
        ny = dy / dist_box
        overlap = ball.radius - dist_box
        ball.x += nx * overlap
        ball.y += ny * overlap

        side_push = 3.8 if player.is_p1 else -3.8
        ball.vx = (ball.vx * 0.5) + side_push + player.vx
        ball.vy = -abs(ball.vy) * 0.45 - 1.4
        ball.spin *= 0.4
        sound_mgr.play(sound_mgr.kick_sound)

        if game is not None and game.commentary_cooldown <= 0 and random.random() < 0.18:
            game.show_commentary(random.choice(game.shoulder_quotes), 70, LIGHT_GRAY)
            game.commentary_cooldown = 60


def handle_human_shots(player, ball, keys, bindings, sound_mgr):
    high_shot = keys[bindings["hava_sut"]]
    low_shot = keys[bindings["yer_sut"]]

    if not (high_shot or low_shot):
        return

    if player.shot_cooldown > 0:
        return

    player.trigger_kick("high" if high_shot else "low")

    dist_to_ball = math.hypot(ball.x - player.x, ball.y - (player.y - player.body_h / 2))

    if dist_to_ball < 88:
        direction = 1.0 if player.is_p1 else -1.0
        player.shot_cooldown = 18
        boost = 1.55 if player.super_shot_timer > 0 else 1.0

        if high_shot:
            ball.vx = direction * 14.5 * boost
            ball.vy = -12.5 * boost
            ball.spin = direction * random.uniform(2.0, 4.2)
        elif low_shot:
            ball.vx = direction * 18.0 * boost
            ball.vy = -3.2 * boost
            ball.spin = direction * random.uniform(1.0, 2.6)

        sound_mgr.play(sound_mgr.shot_sound)

# -------------------------------------------------------------
# 8. OYUN ANA MOTORU (STATE MACHINE)
# -------------------------------------------------------------
class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF)
        pygame.display.set_caption("KafaTopu3 (Özelleştirilebilir Tuşlar)")
        self.clock = pygame.time.Clock()

        self.font_title = pygame.font.SysFont("impact", 64)
        self.font_sub = pygame.font.SysFont("comicsansms", 28, bold=True)
        self.font_btn = pygame.font.SysFont("arial", 20, bold=True)
        self.font_hud = pygame.font.SysFont("impact", 36)
        self.font_mim = pygame.font.SysFont("impact", 58)
        self.font_countdown = pygame.font.SysFont("impact", 110)

        self.state = "menu"
        self.sound_mgr = SoundManager()
        self.face_images = load_face_images()

        self.game_mode = "1_oyuncu"
        self.difficulty = "Orta"

        # Tuş Atamaları
        self.default_p1_keys = {
            "sol": pygame.K_a,
            "sag": pygame.K_d,
            "zipla": pygame.K_w,
            "hava_sut": pygame.K_q,
            "yer_sut": pygame.K_e,
        }
        self.default_p2_keys = {
            "sol": pygame.K_LEFT,
            "sag": pygame.K_RIGHT,
            "zipla": pygame.K_UP,
            "hava_sut": pygame.K_PERIOD,
            "yer_sut": pygame.K_KP0,
        }
        self.p1_keys = self.default_p1_keys.copy()
        self.p2_keys = self.default_p2_keys.copy()

        self.waiting_for_key = None

        self.current_video_player = None
        self.current_cv2_cap = None
        self.video_return_state = "oyun"
        self.video_title = ""
        self.video_fallback_timer = 0

        self.ground_y = 510
        self.field_left = 60
        self.field_right = 940
        self.goal_width = 80
        self.goal_height = 170

        self.goal_left = Goal(self.field_left - self.goal_width, self.ground_y - self.goal_height, self.goal_width, self.goal_height, is_left=True)
        self.goal_right = Goal(self.field_right, self.ground_y - self.goal_height, self.goal_width, self.goal_height, is_left=False)
        self.goal_left_scale_timer = 0
        self.goal_right_scale_timer = 0

        self.p1 = Player(220, self.ground_y, is_p1=True)
        self.p2 = Player(780, self.ground_y, is_p1=False)
        self.ball = Ball(SCREEN_WIDTH // 2, 250)

        self.score_p1 = 0
        self.score_p2 = 0
        self.match_time = 120.0
        self.last_rendered_second = -1
        self.goal_popup_timer = 0
        self.goal_meme_text = "GOL!"
        self.match_winner_text = ""

        # Partikül sistemi
        self.particles = []

        # Spiker (yorumcu) sistemi
        self.commentary_text = ""
        self.commentary_timer = 0
        self.commentary_color = YELLOW
        self.commentary_cooldown = 0
        self.final_countdown_announced = False
        self.last_countdown_number = None
        self.countdown_flash_timer = 0

        self.goal_commentary_quotes = [
            "GOOOL! {team} ÖNE GEÇTİ!",
            "İNANILMAZ BİR GOL, {team}!",
            "AĞLARLA BULUŞTU! {team} SEVİNİYOR!",
            "MİM GİBİ GOL, {team}!",
        ]
        self.near_miss_quotes = ["DİREKTEN DÖNDÜ!", "AAAH, NE KAÇTI!", "SON ANDA KURTULDU!"]
        self.header_quotes = ["KAFA VURUŞU!", "MÜKEMMEL KAFA TOPU!", "HAVADA HARİKA BİR VURUŞ!"]
        self.shoulder_quotes = ["OMUZLA KESTİ!", "GÖVDESİYLE ENGELLEDİ!"]

        # Özel güçler
        self.power_options = POWER_OPTIONS
        self.p1_selected_power = None
        self.p2_selected_power = None
        self.ball_freeze_timer = 0
        self.super_power_banner_timer = 0
        self.super_power_banner_text = ""

        self.lig_isimleri = list(LIGLER.keys())
        self.p1_lig_idx = 0
        self.p1_takim_idx = 0
        self.p2_lig_idx = 0
        self.p2_takim_idx = 1

        self.meme_quotes = ["BRUH ANI!", "İNANILMAZ GOOOL!", "HESAPLANDI!", "MİM GİBİ GOL!", "AĞLARA GİTTİ!"]

        self.precalc_background()

    def precalc_background(self):
        self.bg_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert()

        # Gökyüzü gradyanı
        sky_top = (95, 170, 220)
        sky_bottom = (190, 225, 245)
        for y in range(0, 360):
            ratio = y / 360.0
            r = int(sky_top[0] + (sky_bottom[0] - sky_top[0]) * ratio)
            g = int(sky_top[1] + (sky_bottom[1] - sky_top[1]) * ratio)
            b = int(sky_top[2] + (sky_bottom[2] - sky_top[2]) * ratio)
            pygame.draw.line(self.bg_surf, (r, g, b), (0, y), (SCREEN_WIDTH, y))

        # Bulutlar
        cloud_positions = [(120, 70), (360, 45), (620, 90), (840, 55)]
        for cx, cy in cloud_positions:
            for dx, dy, rad in [(0, 0, 22), (18, -6, 18), (-18, -4, 16), (34, 4, 14), (-32, 6, 13)]:
                pygame.draw.circle(self.bg_surf, WHITE, (cx + dx, cy + dy), rad)

        # Işık direkleri (floodlight)
        for lx in (40, SCREEN_WIDTH - 40):
            pygame.draw.rect(self.bg_surf, (90, 90, 95), (lx - 4, 40, 8, 320))
            pygame.draw.rect(self.bg_surf, (60, 60, 65), (lx - 26, 20, 52, 22), border_radius=4)
            for gx in range(lx - 20, lx + 21, 8):
                pygame.draw.circle(self.bg_surf, (255, 250, 210), (gx, 31), 4)

        # Tribün
        pygame.draw.rect(self.bg_surf, (100, 110, 120), (0, 360, SCREEN_WIDTH, 120))
        for sx in range(0, SCREEN_WIDTH, 40):
            pygame.draw.line(self.bg_surf, (120, 130, 140), (sx, 360), (sx, 480), 2)

        # Tribün kalabalığı (sabit, tohumlu rastgelelik -> performans için tek seferlik)
        crowd_colors = [(210, 60, 60), (60, 90, 200), (230, 210, 80), (240, 240, 240), (80, 170, 90)]
        local_rand = random.Random(42)
        for row_y in range(368, 476, 10):
            for cx in range(10, SCREEN_WIDTH, 14):
                if local_rand.random() < 0.75:
                    col = local_rand.choice(crowd_colors)
                    pygame.draw.circle(self.bg_surf, col, (cx, row_y), 3)

        # Saha (çim)
        pygame.draw.rect(self.bg_surf, GREEN_FIELD, (0, 480, SCREEN_WIDTH, 120))
        for x_step in range(0, SCREEN_WIDTH, 80):
            if (x_step // 80) % 2 == 0:
                pygame.draw.rect(self.bg_surf, GREEN_FIELD_DARK, (x_step, 480, 80, 120))

        # Saha çizgileri
        pygame.draw.line(self.bg_surf, LINE_WHITE, (self.field_left, self.ground_y), (self.field_right, self.ground_y), 4)
        pygame.draw.line(self.bg_surf, LINE_WHITE, (SCREEN_WIDTH // 2, 380), (SCREEN_WIDTH // 2, self.ground_y), 3)
        pygame.draw.circle(self.bg_surf, LINE_WHITE, (SCREEN_WIDTH // 2, int(self.ground_y - 65)), 65, 3)

        # Ceza sahası çizgileri
        pygame.draw.rect(self.bg_surf, LINE_WHITE, (self.field_left, self.ground_y - 90, 70, 90), 3)
        pygame.draw.rect(self.bg_surf, LINE_WHITE, (self.field_right - 70, self.ground_y - 90, 70, 90), 3)

        self._draw_goal_to_surf(self.bg_surf, self.goal_left)
        self._draw_goal_to_surf(self.bg_surf, self.goal_right)

    def _draw_goal_to_surf(self, target_surf, goal):
        net_rect = pygame.Rect(goal.x, goal.y, goal.width, goal.height)
        for gx in range(goal.x, goal.x + goal.width, 10):
            pygame.draw.line(target_surf, (220, 220, 220), (gx, goal.y), (gx, goal.y + goal.height), 1)
        for gy in range(goal.y, goal.y + goal.height, 10):
            pygame.draw.line(target_surf, (220, 220, 220), (goal.x, gy), (goal.x + goal.width, gy), 1)
        pygame.draw.rect(target_surf, WHITE, net_rect, goal.post_thickness)
        pygame.draw.circle(target_surf, WHITE, (int(goal.tip_x), int(goal.tip_y)), 7)

    def _draw_goal_overlay(self, goal, color):
        # Kale boyutu geçici olarak değiştiğinde, orijinal (sabit) çizimin üstüne
        # yarı saydam bir vurgu çizilir; performans için tüm arka plan yeniden çizilmez.
        overlay = pygame.Surface((goal.width, int(goal.height)), pygame.SRCALPHA)
        overlay.fill((color[0], color[1], color[2], 90))
        pygame.draw.rect(overlay, color, overlay.get_rect(), 3)
        self.screen.blit(overlay, (goal.x, goal.y))

    def draw_back_button(self):
        btn_rect = pygame.Rect(20, 16, 95, 36)
        mouse_pos = pygame.mouse.get_pos()
        hover = btn_rect.collidepoint(mouse_pos)
        color = RED if hover else DARK_GRAY
        pygame.draw.rect(self.screen, color, btn_rect, border_radius=6)
        pygame.draw.rect(self.screen, WHITE, btn_rect, 2, border_radius=6)
        txt = self.font_btn.render("< Geri", True, WHITE)
        self.screen.blit(txt, txt.get_rect(center=btn_rect.center))
        return btn_rect

    def show_commentary(self, text, duration=100, color=YELLOW):
        self.commentary_text = text
        self.commentary_timer = duration
        self.commentary_color = color

    def spawn_dust(self, x, y, count=5):
        for _ in range(count):
            vx = random.uniform(-1.5, 1.5)
            vy = random.uniform(-1.8, -0.4)
            life = random.randint(14, 24)
            size = random.randint(2, 4)
            self.particles.append(Particle(x, y, vx, vy, life, (210, 200, 180), size, gravity=0.12))

    def spawn_confetti(self, x, y, team_colors, count=36):
        palette = list(team_colors) + [WHITE, YELLOW]
        for _ in range(count):
            vx = random.uniform(-3.2, 3.2)
            vy = random.uniform(-6.5, -2.5)
            life = random.randint(40, 70)
            size = random.randint(3, 5)
            color = random.choice(palette)
            self.particles.append(Particle(x, y, vx, vy, life, color, size, gravity=0.22))

    # --- ÖZEL GÜÇ AKTİVASYONU ---
    def try_activate_power(self, user, opponent, own_goal, opp_goal):
        if not user.power_id or user.power_cooldown_timer > 0:
            return

        power = user.power_id
        power_name = POWER_NAMES.get(power, power)
        who = "P1" if user.is_p1 else ("BOT" if self.game_mode == "1_oyuncu" else "P2")
        self.show_commentary(f"SÜPER GÜÇ! {who}: {power_name}", 90, POWER_PINK)
        self.super_power_banner_timer = 55
        self.super_power_banner_text = power_name
        self.sound_mgr.play(self.sound_mgr.whistle_sound)

        if power == "freeze_enemy":
            opponent.frozen_timer = 180  # 3 sn
        elif power == "shrink_own_goal":
            own_goal.set_height_scale(0.55)
            if own_goal is self.goal_left:
                self.goal_left_scale_timer = 360  # 6 sn
            else:
                self.goal_right_scale_timer = 360
        elif power == "enlarge_enemy_goal":
            opp_goal.set_height_scale(1.6)
            if opp_goal is self.goal_left:
                self.goal_left_scale_timer = 360
            else:
                self.goal_right_scale_timer = 360
        elif power == "giant":
            user.giant_timer = 300  # 5 sn
            user.scale = 1.55
        elif power == "freeze_ball":
            self.ball_freeze_timer = 90  # 1.5 sn
            self.ball.vx = 0.0
            self.ball.vy = 0.0
        elif power == "super_shot":
            user.super_shot_timer = 240  # 4 sn
        elif power == "invert_controls":
            opponent.invert_timer = 300  # 5 sn

        user.power_cooldown_timer = 300  # Kullanıldıktan sonra 5 sn kilitli

    def play_meme_video(self, category, team_code_or_name, next_state="oyun", title="KOMİK AN"):
        video_path = get_random_video(category, team_code_or_name)
        self.video_return_state = next_state
        self.video_title = title

        if not video_path:
            if next_state == "mac_sonu":
                self.state = "mac_sonu"
            return False

        if HAS_PYVIDPLAYER:
            try:
                self.current_video_player = Video(video_path)
                self.current_video_player.resize((SCREEN_WIDTH, SCREEN_HEIGHT))
                self.state = "video_oynatma"
                return True
            except Exception:
                self.current_video_player = None

        if HAS_CV2:
            try:
                self.current_cv2_cap = cv2.VideoCapture(video_path)
                self.state = "video_oynatma"
                return True
            except Exception:
                self.current_cv2_cap = None

        try:
            os.startfile(video_path)
        except Exception:
            pass

        self.video_fallback_timer = 180
        self.state = "video_oynatma"
        return True

    def stop_current_video(self):
        if HAS_PYVIDPLAYER and self.current_video_player:
            try:
                self.current_video_player.close()
            except Exception:
                pass
            self.current_video_player = None

        if HAS_CV2 and self.current_cv2_cap:
            try:
                self.current_cv2_cap.release()
            except Exception:
                pass
            self.current_cv2_cap = None

        self.state = self.video_return_state
        if self.state == "oyun":
            self.p1.reset_position()
            self.p2.reset_position()
            self.ball.reset_position()

    def handle_video_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN and (e.key in (pygame.K_SPACE, pygame.K_ESCAPE)):
                self.stop_current_video()
                return
            elif e.type == pygame.MOUSEBUTTONDOWN:
                self.stop_current_video()
                return

    def update_and_draw_video(self):
        self.screen.fill(BLACK)

        if HAS_PYVIDPLAYER and self.current_video_player:
            try:
                if self.current_video_player.active:
                    self.current_video_player.draw(self.screen, (0, 0))
                else:
                    self.stop_current_video()
                    return
            except Exception:
                self.stop_current_video()
                return

        elif HAS_CV2 and self.current_cv2_cap:
            ret, frame = self.current_cv2_cap.read()
            if ret:
                frame = cv2.resize(frame, (SCREEN_WIDTH, SCREEN_HEIGHT))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                surf = pygame.image.frombuffer(frame.tobytes(), (SCREEN_WIDTH, SCREEN_HEIGHT), "RGB")
                self.screen.blit(surf, (0, 0))
            else:
                self.stop_current_video()
                return
        else:
            if self.video_fallback_timer > 0:
                self.video_fallback_timer -= 1
                msg = self.font_hud.render("MİM VİDEOSU OYNATILIYOR...", True, YELLOW)
                sub = self.font_btn.render("Devam etmek için [BOŞLUK] tuşuna basınız veya tıklayınız", True, WHITE)
                self.screen.blit(msg, msg.get_rect(center=(SCREEN_WIDTH // 2, 260)))
                self.screen.blit(sub, sub.get_rect(center=(SCREEN_WIDTH // 2, 320)))
            else:
                self.stop_current_video()
                return

        skip_txt = self.font_btn.render("Geçmek için [BOŞLUK] tuşuna basınız", True, (240, 240, 240))
        self.screen.blit(skip_txt, (20, SCREEN_HEIGHT - 35))

    # --- DURUM 1: ANA MENÜ ---
    def handle_menu(self, events):
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mouse_pos = e.pos
                if self.btn_play.collidepoint(mouse_pos):
                    self.state = "takim_secim"
                elif self.btn_custom.collidepoint(mouse_pos):
                    self.state = "ozellestirme"
                elif self.btn_controls.collidepoint(mouse_pos):
                    self.state = "tus_ayarlari"

    def draw_menu(self):
        self.screen.fill(SKY_BLUE)
        pygame.draw.rect(self.screen, GREEN_FIELD, (0, 480, SCREEN_WIDTH, 120))

        title = self.font_title.render("KAFA TOPU 3", True, BLACK)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 140)))

        mouse_pos = pygame.mouse.get_pos()
        self.btn_play = pygame.Rect(SCREEN_WIDTH // 2 - 140, 235, 280, 56)
        self.btn_custom = pygame.Rect(SCREEN_WIDTH // 2 - 160, 310, 320, 56)
        self.btn_controls = pygame.Rect(SCREEN_WIDTH // 2 - 140, 385, 280, 56)

        buttons = [
            (self.btn_play, "OYNA"),
            (self.btn_custom, "KARAKTER ÖZELLEŞTİRME"),
            (self.btn_controls, "TUŞ AYARLARI")
        ]

        for b, text in buttons:
            hover = b.collidepoint(mouse_pos)
            pygame.draw.rect(self.screen, YELLOW if hover else WHITE, b, border_radius=12)
            pygame.draw.rect(self.screen, BLACK, b, 3, border_radius=12)
            txt_surf = self.font_btn.render(text, True, BLACK)
            self.screen.blit(txt_surf, txt_surf.get_rect(center=b.center))

    # --- DURUM 2: KARAKTER ÖZELLEŞTİRME ---
    def handle_customization(self, events):
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if self.draw_back_button().collidepoint(e.pos):
                    self.state = "menu"
                    return

                if self.btn_p1_face_prev.collidepoint(e.pos):
                    self.p1.face_id = 5 if self.p1.face_id == 1 else self.p1.face_id - 1
                elif self.btn_p1_face_next.collidepoint(e.pos):
                    self.p1.face_id = 1 if self.p1.face_id == 5 else self.p1.face_id + 1

                if self.btn_p2_face_prev.collidepoint(e.pos):
                    self.p2.face_id = 5 if self.p2.face_id == 1 else self.p2.face_id - 1
                elif self.btn_p2_face_next.collidepoint(e.pos):
                    self.p2.face_id = 1 if self.p2.face_id == 5 else self.p2.face_id + 1

    def draw_customization(self):
        self.screen.fill((45, 52, 54))
        self.draw_back_button()

        header = self.font_hud.render("KARAKTER YÜZ ÖZELLEŞTİRME", True, YELLOW)
        self.screen.blit(header, header.get_rect(center=(SCREEN_WIDTH // 2, 50)))

        p1_box = pygame.Rect(120, 120, 320, 380)
        pygame.draw.rect(self.screen, DARK_GRAY, p1_box, border_radius=15)
        pygame.draw.rect(self.screen, LIGHT_GRAY, p1_box, 2, border_radius=15)
        p1_title = self.font_sub.render("OYUNCU 1 (P1)", True, WHITE)
        self.screen.blit(p1_title, p1_title.get_rect(center=(p1_box.centerx, 160)))

        p1_face = self.face_images[self.p1.face_id]
        scaled_p1 = pygame.transform.scale(p1_face, (130, 130))
        self.screen.blit(scaled_p1, scaled_p1.get_rect(center=(p1_box.centerx, 270)))

        self.btn_p1_face_prev = pygame.Rect(150, 380, 50, 45)
        self.btn_p1_face_next = pygame.Rect(340, 380, 50, 45)
        self._draw_arrow_btn(self.btn_p1_face_prev, "<")
        self._draw_arrow_btn(self.btn_p1_face_next, ">")
        p1_lbl = self.font_btn.render(f"Yüz #{self.p1.face_id}", True, YELLOW)
        self.screen.blit(p1_lbl, p1_lbl.get_rect(center=(p1_box.centerx, 402)))

        p2_box = pygame.Rect(560, 120, 320, 380)
        pygame.draw.rect(self.screen, DARK_GRAY, p2_box, border_radius=15)
        pygame.draw.rect(self.screen, LIGHT_GRAY, p2_box, 2, border_radius=15)
        p2_title = self.font_sub.render("OYUNCU 2 / BOT", True, WHITE)
        self.screen.blit(p2_title, p2_title.get_rect(center=(p2_box.centerx, 160)))

        p2_face = self.face_images[self.p2.face_id]
        scaled_p2 = pygame.transform.scale(p2_face, (130, 130))
        self.screen.blit(scaled_p2, scaled_p2.get_rect(center=(p2_box.centerx, 270)))

        self.btn_p2_face_prev = pygame.Rect(590, 380, 50, 45)
        self.btn_p2_face_next = pygame.Rect(780, 380, 50, 45)
        self._draw_arrow_btn(self.btn_p2_face_prev, "<")
        self._draw_arrow_btn(self.btn_p2_face_next, ">")
        p2_lbl = self.font_btn.render(f"Yüz #{self.p2.face_id}", True, YELLOW)
        self.screen.blit(p2_lbl, p2_lbl.get_rect(center=(p2_box.centerx, 402)))

    def _draw_arrow_btn(self, rect, text):
        mouse_pos = pygame.mouse.get_pos()
        hover = rect.collidepoint(mouse_pos)
        pygame.draw.rect(self.screen, YELLOW if hover else WHITE, rect, border_radius=8)
        pygame.draw.rect(self.screen, BLACK, rect, 2, border_radius=8)
        txt = self.font_btn.render(text, True, BLACK)
        self.screen.blit(txt, txt.get_rect(center=rect.center))

    # --- DURUM 3: TUŞ ATAMALARI BÖLÜMÜ ---
    def handle_controls(self, events):
        for e in events:
            if self.waiting_for_key:
                if e.type == pygame.KEYDOWN:
                    if e.key != pygame.K_ESCAPE:
                        p_id, action = self.waiting_for_key
                        if p_id == 1:
                            self.p1_keys[action] = e.key
                        else:
                            self.p2_keys[action] = e.key
                    self.waiting_for_key = None
                    return
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    self.waiting_for_key = None
                    return
                continue

            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if self.draw_back_button().collidepoint(e.pos):
                    self.state = "menu"
                    return

                if hasattr(self, "btn_reset_keys") and self.btn_reset_keys.collidepoint(e.pos):
                    self.p1_keys = self.default_p1_keys.copy()
                    self.p2_keys = self.default_p2_keys.copy()
                    return

                for action, rect in getattr(self, "p1_key_rects", {}).items():
                    if rect.collidepoint(e.pos):
                        self.waiting_for_key = (1, action)
                        return

                for action, rect in getattr(self, "p2_key_rects", {}).items():
                    if rect.collidepoint(e.pos):
                        self.waiting_for_key = (2, action)
                        return

    def draw_controls(self):
        self.screen.fill((35, 40, 48))
        self.draw_back_button()

        header = self.font_hud.render("TUŞ ATAMALARI", True, YELLOW)
        self.screen.blit(header, header.get_rect(center=(SCREEN_WIDTH // 2, 40)))

        info = self.font_btn.render("Değiştirmek istediğiniz tuşa tıklayın ve ardından yeni tuşa basın.", True, LIGHT_GRAY)
        self.screen.blit(info, info.get_rect(center=(SCREEN_WIDTH // 2, 75)))

        actions = [
            ("sol", "Sola Hareket"),
            ("sag", "Sağa Hareket"),
            ("zipla", "Zıplama"),
            ("hava_sut", "Havadan Şut"),
            ("yer_sut", "Yerden Şut"),
        ]

        self.p1_key_rects = {}
        self.p2_key_rects = {}

        # P1 Paneli
        p1_box = pygame.Rect(80, 110, 390, 380)
        pygame.draw.rect(self.screen, DARK_GRAY, p1_box, border_radius=12)
        pygame.draw.rect(self.screen, BLUE_ACCENT, p1_box, 2, border_radius=12)
        p1_title = self.font_sub.render("OYUNCU 1 (P1)", True, YELLOW)
        self.screen.blit(p1_title, p1_title.get_rect(center=(p1_box.centerx, 140)))

        start_y = 180
        mouse_pos = pygame.mouse.get_pos()

        for idx, (action, label) in enumerate(actions):
            y = start_y + idx * 56
            lbl_surf = self.font_btn.render(label, True, WHITE)
            self.screen.blit(lbl_surf, (p1_box.left + 25, y + 8))

            btn_rect = pygame.Rect(p1_box.right - 145, y, 120, 38)
            self.p1_key_rects[action] = btn_rect

            is_waiting = (self.waiting_for_key == (1, action))
            key_name = "..." if is_waiting else get_key_display_name(self.p1_keys[action])

            btn_col = ORANGE if is_waiting else (LIGHT_GRAY if btn_rect.collidepoint(mouse_pos) else WHITE)
            pygame.draw.rect(self.screen, btn_col, btn_rect, border_radius=8)
            pygame.draw.rect(self.screen, BLACK, btn_rect, 2, border_radius=8)

            txt = self.font_btn.render(key_name, True, BLACK)
            self.screen.blit(txt, txt.get_rect(center=btn_rect.center))

        # P2 Paneli
        p2_box = pygame.Rect(530, 110, 390, 380)
        pygame.draw.rect(self.screen, DARK_GRAY, p2_box, border_radius=12)
        pygame.draw.rect(self.screen, RED, p2_box, 2, border_radius=12)
        p2_title = self.font_sub.render("OYUNCU 2 (P2)", True, YELLOW)
        self.screen.blit(p2_title, p2_title.get_rect(center=(p2_box.centerx, 140)))

        for idx, (action, label) in enumerate(actions):
            y = start_y + idx * 56
            lbl_surf = self.font_btn.render(label, True, WHITE)
            self.screen.blit(lbl_surf, (p2_box.left + 25, y + 8))

            btn_rect = pygame.Rect(p2_box.right - 145, y, 120, 38)
            self.p2_key_rects[action] = btn_rect

            is_waiting = (self.waiting_for_key == (2, action))
            key_name = "..." if is_waiting else get_key_display_name(self.p2_keys[action])

            btn_col = ORANGE if is_waiting else (LIGHT_GRAY if btn_rect.collidepoint(mouse_pos) else WHITE)
            pygame.draw.rect(self.screen, btn_col, btn_rect, border_radius=8)
            pygame.draw.rect(self.screen, BLACK, btn_rect, 2, border_radius=8)

            txt = self.font_btn.render(key_name, True, BLACK)
            self.screen.blit(txt, txt.get_rect(center=btn_rect.center))

        # Varsayılan Tuşlara Sıfırla Butonu
        self.btn_reset_keys = pygame.Rect(SCREEN_WIDTH // 2 - 130, 520, 260, 48)
        hover_reset = self.btn_reset_keys.collidepoint(mouse_pos)
        pygame.draw.rect(self.screen, DARK_GRAY if not hover_reset else GRAY, self.btn_reset_keys, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, self.btn_reset_keys, 2, border_radius=10)
        rst_txt = self.font_btn.render("Varsayılana Sıfırla", True, WHITE)
        self.screen.blit(rst_txt, rst_txt.get_rect(center=self.btn_reset_keys.center))

        note = self.font_btn.render("Özel güç: P1 = [S] tuşu   |   P2 = [Aşağı Ok] tuşu", True, POWER_PINK)
        self.screen.blit(note, note.get_rect(center=(SCREEN_WIDTH // 2, 575)))

    # --- DURUM 4: TAKIM VE MOD SEÇİMİ ---
    def handle_team_selection(self, events):
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if self.draw_back_button().collidepoint(e.pos):
                    self.state = "menu"
                    return

                if self.btn_mode_single.collidepoint(e.pos):
                    self.game_mode = "1_oyuncu"
                elif self.btn_mode_multi.collidepoint(e.pos):
                    self.game_mode = "2_oyuncu"

                if self.game_mode == "1_oyuncu":
                    if self.btn_diff_easy.collidepoint(e.pos):
                        self.difficulty = "Kolay"
                    elif self.btn_diff_med.collidepoint(e.pos):
                        self.difficulty = "Orta"
                    elif self.btn_diff_hard.collidepoint(e.pos):
                        self.difficulty = "Zor"

                if self.btn_p1_lig_prev.collidepoint(e.pos):
                    self.p1_lig_idx = (self.p1_lig_idx - 1) % len(self.lig_isimleri)
                    self.p1_takim_idx = 0
                elif self.btn_p1_lig_next.collidepoint(e.pos):
                    self.p1_lig_idx = (self.p1_lig_idx + 1) % len(self.lig_isimleri)
                    self.p1_takim_idx = 0

                lig_adi_p1 = self.lig_isimleri[self.p1_lig_idx]
                if self.btn_p1_team_prev.collidepoint(e.pos):
                    self.p1_takim_idx = (self.p1_takim_idx - 1) % len(LIGLER[lig_adi_p1])
                elif self.btn_p1_team_next.collidepoint(e.pos):
                    self.p1_takim_idx = (self.p1_takim_idx + 1) % len(LIGLER[lig_adi_p1])

                if self.btn_p2_lig_prev.collidepoint(e.pos):
                    self.p2_lig_idx = (self.p2_lig_idx - 1) % len(self.lig_isimleri)
                    self.p2_takim_idx = 0
                elif self.btn_p2_lig_next.collidepoint(e.pos):
                    self.p2_lig_idx = (self.p2_lig_idx + 1) % len(self.lig_isimleri)
                    self.p2_takim_idx = 0

                lig_adi_p2 = self.lig_isimleri[self.p2_lig_idx]
                if self.btn_p2_team_prev.collidepoint(e.pos):
                    self.p2_takim_idx = (self.p2_takim_idx - 1) % len(LIGLER[lig_adi_p2])
                elif self.btn_p2_team_next.collidepoint(e.pos):
                    self.p2_takim_idx = (self.p2_takim_idx + 1) % len(LIGLER[lig_adi_p2])

                if self.btn_start_match.collidepoint(e.pos):
                    self.p1.team = LIGLER[self.lig_isimleri[self.p1_lig_idx]][self.p1_takim_idx]
                    self.p2.team = LIGLER[self.lig_isimleri[self.p2_lig_idx]][self.p2_takim_idx]
                    self.p1_selected_power = None
                    self.p2_selected_power = None
                    self.state = "ozel_guc_secim"

    def start_match(self):
        self.score_p1 = 0
        self.score_p2 = 0
        self.match_time = 120.0
        self.last_rendered_second = -1
        self.p1.reset_position()
        self.p2.reset_position()
        self.ball.reset_position()
        self.goal_popup_timer = 0
        self.particles = []
        self.commentary_timer = 0
        self.commentary_cooldown = 0
        self.final_countdown_announced = False
        self.last_countdown_number = None
        self.countdown_flash_timer = 0

        # Özel güç durumlarını sıfırla ve seçilenleri ata
        self.p1.reset_powers()
        self.p2.reset_powers()
        self.p1.power_id = self.p1_selected_power
        self.p2.power_id = self.p2_selected_power
        self.goal_left.set_height_scale(1.0)
        self.goal_right.set_height_scale(1.0)
        self.goal_left_scale_timer = 0
        self.goal_right_scale_timer = 0
        self.ball_freeze_timer = 0
        self.super_power_banner_timer = 0

        self.cached_p1_name = self.font_btn.render(self.p1.team["ad"][:10], True, self.p1.team["renk1"])
        p2_display_name = f"BOT ({self.difficulty})" if self.game_mode == "1_oyuncu" else self.p2.team["ad"][:10]
        self.cached_p2_name = self.font_btn.render(p2_display_name, True, self.p2.team["renk1"])
        self.cached_time_surf = None

        self.state = "oyun"
        self.show_commentary("MAÇ BAŞLIYOR!", 100, WHITE)
        self.sound_mgr.play(self.sound_mgr.whistle_sound)

    def draw_team_selection(self):
        self.screen.fill((30, 39, 46))
        self.draw_back_button()

        header = self.font_hud.render("TAKIM VE MOD SEÇİMİ", True, YELLOW)
        self.screen.blit(header, header.get_rect(center=(SCREEN_WIDTH // 2, 30)))

        self.btn_mode_single = pygame.Rect(260, 60, 220, 36)
        self.btn_mode_multi = pygame.Rect(520, 60, 220, 36)
        self._draw_toggle_btn(self.btn_mode_single, "1 Oyunculu (vs Bot)", self.game_mode == "1_oyuncu")
        self._draw_toggle_btn(self.btn_mode_multi, "2 Oyunculu (Yerel)", self.game_mode == "2_oyuncu")

        if self.game_mode == "1_oyuncu":
            diff_lbl = self.font_btn.render("Zorluk:", True, WHITE)
            self.screen.blit(diff_lbl, (240, 110))
            self.btn_diff_easy = pygame.Rect(320, 105, 100, 32)
            self.btn_diff_med = pygame.Rect(440, 105, 100, 32)
            self.btn_diff_hard = pygame.Rect(560, 105, 100, 32)
            self._draw_toggle_btn(self.btn_diff_easy, "Kolay", self.difficulty == "Kolay", active_color=GREEN_FIELD)
            self._draw_toggle_btn(self.btn_diff_med, "Orta", self.difficulty == "Orta", active_color=ORANGE)
            self._draw_toggle_btn(self.btn_diff_hard, "Zor", self.difficulty == "Zor", active_color=RED)
        else:
            lbl = self.font_btn.render("Yerel 2 Kişilik Mod (Tuşları 'Tuş Ayarları'ndan değiştirebilirsiniz)", True, LIGHT_GRAY)
            self.screen.blit(lbl, lbl.get_rect(center=(SCREEN_WIDTH // 2, 120)))

        p1_box = pygame.Rect(100, 150, 360, 345)
        pygame.draw.rect(self.screen, DARK_GRAY, p1_box, border_radius=12)
        pygame.draw.rect(self.screen, LIGHT_GRAY, p1_box, 2, border_radius=12)
        t1 = self.font_sub.render("P1 (SEN)", True, WHITE)
        self.screen.blit(t1, t1.get_rect(center=(p1_box.centerx, 180)))

        lig_p1 = self.lig_isimleri[self.p1_lig_idx]
        takim_p1 = LIGLER[lig_p1][self.p1_takim_idx]

        self.btn_p1_lig_prev = pygame.Rect(120, 215, 45, 36)
        self.btn_p1_lig_next = pygame.Rect(395, 215, 45, 36)
        self._draw_arrow_btn(self.btn_p1_lig_prev, "<")
        self._draw_arrow_btn(self.btn_p1_lig_next, ">")
        lig_p1_txt = self.font_btn.render(lig_p1, True, YELLOW)
        self.screen.blit(lig_p1_txt, lig_p1_txt.get_rect(center=(p1_box.centerx, 233)))

        self.btn_p1_team_prev = pygame.Rect(120, 270, 45, 36)
        self.btn_p1_team_next = pygame.Rect(395, 270, 45, 36)
        self._draw_arrow_btn(self.btn_p1_team_prev, "<")
        self._draw_arrow_btn(self.btn_p1_team_next, ">")
        team_p1_txt = self.font_btn.render(takim_p1["ad"], True, WHITE)
        self.screen.blit(team_p1_txt, team_p1_txt.get_rect(center=(p1_box.centerx, 288)))

        self._draw_kit_preview(p1_box.centerx, 375, takim_p1["renk1"], takim_p1["renk2"])

        p2_box = pygame.Rect(540, 150, 360, 345)
        pygame.draw.rect(self.screen, DARK_GRAY, p2_box, border_radius=12)
        pygame.draw.rect(self.screen, LIGHT_GRAY, p2_box, 2, border_radius=12)
        p2_title_str = f"BOT ({self.difficulty.upper()})" if self.game_mode == "1_oyuncu" else "OYUNCU 2"
        t2 = self.font_sub.render(p2_title_str, True, WHITE)
        self.screen.blit(t2, t2.get_rect(center=(p2_box.centerx, 180)))

        lig_p2 = self.lig_isimleri[self.p2_lig_idx]
        takim_p2 = LIGLER[lig_p2][self.p2_takim_idx]

        self.btn_p2_lig_prev = pygame.Rect(560, 215, 45, 36)
        self.btn_p2_lig_next = pygame.Rect(835, 215, 45, 36)
        self._draw_arrow_btn(self.btn_p2_lig_prev, "<")
        self._draw_arrow_btn(self.btn_p2_lig_next, ">")
        lig_p2_txt = self.font_btn.render(lig_p2, True, YELLOW)
        self.screen.blit(lig_p2_txt, lig_p2_txt.get_rect(center=(p2_box.centerx, 233)))

        self.btn_p2_team_prev = pygame.Rect(560, 270, 45, 36)
        self.btn_p2_team_next = pygame.Rect(835, 270, 45, 36)
        self._draw_arrow_btn(self.btn_p2_team_prev, "<")
        self._draw_arrow_btn(self.btn_p2_team_next, ">")
        team_p2_txt = self.font_btn.render(takim_p2["ad"], True, WHITE)
        self.screen.blit(team_p2_txt, team_p2_txt.get_rect(center=(p2_box.centerx, 288)))

        self._draw_kit_preview(p2_box.centerx, 375, takim_p2["renk1"], takim_p2["renk2"])

        self.btn_start_match = pygame.Rect(SCREEN_WIDTH // 2 - 140, 520, 280, 54)
        hover = self.btn_start_match.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(self.screen, GREEN_FIELD if not hover else (60, 179, 113), self.btn_start_match, border_radius=12)
        pygame.draw.rect(self.screen, WHITE, self.btn_start_match, 3, border_radius=12)
        st_txt = self.font_btn.render("DEVAM ET (ÖZEL GÜÇ SEÇ)", True, WHITE)
        self.screen.blit(st_txt, st_txt.get_rect(center=self.btn_start_match.center))

    def _draw_toggle_btn(self, rect, text, is_active, active_color=BLUE_ACCENT):
        color = active_color if is_active else DARK_GRAY
        border_col = WHITE if is_active else GRAY
        pygame.draw.rect(self.screen, color, rect, border_radius=8)
        pygame.draw.rect(self.screen, border_col, rect, 2, border_radius=8)
        txt = self.font_btn.render(text, True, WHITE)
        self.screen.blit(txt, txt.get_rect(center=rect.center))

    def _draw_kit_preview(self, cx, cy, c1, c2):
        rect = pygame.Rect(cx - 32, cy - 32, 64, 64)
        pygame.draw.rect(self.screen, c1, rect, border_radius=8)
        pygame.draw.rect(self.screen, c2, (cx - 9, cy - 32, 18, 64))
        pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=8)

    # --- DURUM 4.5: ÖZEL GÜÇ SEÇİMİ ---
    def handle_ozel_guc_secim(self, events):
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if self.draw_back_button().collidepoint(e.pos):
                    self.state = "menu"
                    return

                for pid, rect in getattr(self, "p1_power_rects", {}).items():
                    if rect.collidepoint(e.pos):
                        self.p1_selected_power = pid
                        return

                if self.game_mode == "2_oyuncu":
                    for pid, rect in getattr(self, "p2_power_rects", {}).items():
                        if rect.collidepoint(e.pos):
                            self.p2_selected_power = pid
                            return

                if self.btn_power_start.collidepoint(e.pos):
                    if not self.p1_selected_power:
                        self.p1_selected_power = random.choice(self.power_options)["id"]
                    if self.game_mode == "1_oyuncu":
                        self.p2_selected_power = random.choice(self.power_options)["id"]
                    elif not self.p2_selected_power:
                        self.p2_selected_power = random.choice(self.power_options)["id"]
                    self.start_match()
                    return

    def draw_ozel_guc_secim(self):
        self.screen.fill((28, 30, 42))
        self.draw_back_button()

        header = self.font_hud.render("ÖZEL GÜÇ SEÇİMİ", True, YELLOW)
        self.screen.blit(header, header.get_rect(center=(SCREEN_WIDTH // 2, 40)))
        sub = self.font_btn.render("Her oyuncu sadece 1 tane seçer  •  Maç içinde P1: [S]  P2: [Aşağı Ok]", True, LIGHT_GRAY)
        self.screen.blit(sub, sub.get_rect(center=(SCREEN_WIDTH // 2, 68)))

        mouse_pos = pygame.mouse.get_pos()

        p1_box = pygame.Rect(70, 90, 400, 390)
        pygame.draw.rect(self.screen, DARK_GRAY, p1_box, border_radius=12)
        pygame.draw.rect(self.screen, LIGHT_GRAY, p1_box, 2, border_radius=12)
        t1 = self.font_sub.render("OYUNCU 1", True, WHITE)
        self.screen.blit(t1, t1.get_rect(center=(p1_box.centerx, 118)))

        self.p1_power_rects = {}
        for idx, power in enumerate(self.power_options):
            rect = pygame.Rect(p1_box.left + 20, 145 + idx * 45, p1_box.width - 40, 38)
            self.p1_power_rects[power["id"]] = rect
            selected = (self.p1_selected_power == power["id"])
            hover = rect.collidepoint(mouse_pos)
            col = YELLOW if selected else (LIGHT_GRAY if hover else WHITE)
            pygame.draw.rect(self.screen, col, rect, border_radius=8)
            pygame.draw.rect(self.screen, BLACK, rect, 2, border_radius=8)
            txt = self.font_btn.render(power["name"], True, BLACK)
            self.screen.blit(txt, txt.get_rect(center=rect.center))

        p2_box = pygame.Rect(530, 90, 400, 390)
        pygame.draw.rect(self.screen, DARK_GRAY, p2_box, border_radius=12)
        pygame.draw.rect(self.screen, LIGHT_GRAY, p2_box, 2, border_radius=12)
        p2_title_str = "BOT (rastgele seçecek)" if self.game_mode == "1_oyuncu" else "OYUNCU 2"
        t2 = self.font_sub.render(p2_title_str, True, WHITE)
        self.screen.blit(t2, t2.get_rect(center=(p2_box.centerx, 118)))

        self.p2_power_rects = {}
        if self.game_mode == "2_oyuncu":
            for idx, power in enumerate(self.power_options):
                rect = pygame.Rect(p2_box.left + 20, 145 + idx * 45, p2_box.width - 40, 38)
                self.p2_power_rects[power["id"]] = rect
                selected = (self.p2_selected_power == power["id"])
                hover = rect.collidepoint(mouse_pos)
                col = YELLOW if selected else (LIGHT_GRAY if hover else WHITE)
                pygame.draw.rect(self.screen, col, rect, border_radius=8)
                pygame.draw.rect(self.screen, BLACK, rect, 2, border_radius=8)
                txt = self.font_btn.render(power["name"], True, BLACK)
                self.screen.blit(txt, txt.get_rect(center=rect.center))
        else:
            info = self.font_btn.render("Bot, maç başında otomatik bir güç seçecek.", True, LIGHT_GRAY)
            self.screen.blit(info, info.get_rect(center=(p2_box.centerx, 260)))

        self.btn_power_start = pygame.Rect(SCREEN_WIDTH // 2 - 140, 500, 280, 54)
        hover = self.btn_power_start.collidepoint(mouse_pos)
        pygame.draw.rect(self.screen, GREEN_FIELD if not hover else (60, 179, 113), self.btn_power_start, border_radius=12)
        pygame.draw.rect(self.screen, WHITE, self.btn_power_start, 3, border_radius=12)
        st_txt = self.font_btn.render("MAÇA BAŞLA", True, WHITE)
        self.screen.blit(st_txt, st_txt.get_rect(center=self.btn_power_start.center))

    # --- DURUM 5: MAÇ / OYUN ---
    def handle_game(self, events):
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if self.draw_back_button().collidepoint(e.pos):
                    self.state = "menu"
                    return

            if e.type == pygame.KEYDOWN and self.goal_popup_timer <= 0:
                if e.key == pygame.K_s:
                    self.try_activate_power(self.p1, self.p2, self.goal_left, self.goal_right)
                elif e.key == pygame.K_DOWN:
                    self.try_activate_power(self.p2, self.p1, self.goal_right, self.goal_left)

    def update_game(self):
        keys = pygame.key.get_pressed()

        if self.commentary_cooldown > 0:
            self.commentary_cooldown -= 1

        self.particles = [p for p in self.particles if p.update()]

        # Özel güç zamanlayıcıları (kutlama sırasında bile işlemeye devam eder)
        if self.goal_left_scale_timer > 0:
            self.goal_left_scale_timer -= 1
            if self.goal_left_scale_timer == 0:
                self.goal_left.set_height_scale(1.0)
        if self.goal_right_scale_timer > 0:
            self.goal_right_scale_timer -= 1
            if self.goal_right_scale_timer == 0:
                self.goal_right.set_height_scale(1.0)
        if self.super_power_banner_timer > 0:
            self.super_power_banner_timer -= 1

        if self.game_mode == "1_oyuncu" and self.p2.power_id and self.p2.power_cooldown_timer <= 0:
            if random.random() < 0.006:
                self.try_activate_power(self.p2, self.p1, self.goal_right, self.goal_left)

        self.match_time -= 1.0 / FPS
        if self.match_time <= 0:
            self.match_time = 0
            self.finish_match()
            return

        if (not self.final_countdown_announced) and self.match_time <= 10.0:
            self.final_countdown_announced = True
            self.show_commentary("SON 10 SANİYE!", 100, RED)

        if self.match_time <= 5.0:
            current_count = int(math.ceil(self.match_time))
            if current_count != self.last_countdown_number and current_count > 0:
                self.last_countdown_number = current_count
                self.countdown_flash_timer = 34
                self.sound_mgr.play(self.sound_mgr.tick_sound)
        if self.countdown_flash_timer > 0:
            self.countdown_flash_timer -= 1

        if self.goal_popup_timer > 0:
            self.goal_popup_timer -= 1
            if self.goal_popup_timer == 0:
                self.p1.reset_position()
                self.p2.reset_position()
                self.ball.reset_position()
                self.sound_mgr.play(self.sound_mgr.whistle_sound)
            return

        self.p1.update_human(keys, self.p1_keys, self.ground_y, self.field_left, self.field_right)
        handle_human_shots(self.p1, self.ball, keys, self.p1_keys, self.sound_mgr)
        if self.p1.just_landed:
            self.spawn_dust(self.p1.x, self.ground_y, 5)

        if self.game_mode == "1_oyuncu":
            self.p2.update_bot(self.ball, self.difficulty, self.ground_y, self.field_left, self.field_right, self.sound_mgr)
        else:
            self.p2.update_human(keys, self.p2_keys, self.ground_y, self.field_left, self.field_right)
            handle_human_shots(self.p2, self.ball, keys, self.p2_keys, self.sound_mgr)
        if self.p2.just_landed:
            self.spawn_dust(self.p2.x, self.ground_y, 5)

        resolve_players_collision(self.p1, self.p2)

        if self.ball_freeze_timer > 0:
            self.ball_freeze_timer -= 1
            self.ball.vx = 0.0
            self.ball.vy = 0.0
        else:
            self.ball.update(self.ground_y, self.field_left - self.goal_width + 5, self.field_right + self.goal_width - 5)

            hit1 = self.goal_left.resolve_crossbar_collision(self.ball, self.sound_mgr)
            hit2 = self.goal_right.resolve_crossbar_collision(self.ball, self.sound_mgr)
            if (hit1 or hit2) and self.commentary_cooldown <= 0:
                self.show_commentary(random.choice(self.near_miss_quotes), 90, ORANGE)
                self.sound_mgr.play(self.sound_mgr.crowd_ooh_sound)
                self.commentary_cooldown = 90

            resolve_player_ball_collision(self.p1, self.ball, self.sound_mgr, self)
            resolve_player_ball_collision(self.p2, self.ball, self.sound_mgr, self)

            if self.goal_left.is_goal(self.ball):
                self.score_p2 += 1
                self.goal_popup_timer = 95
                scorer_team = self.p2.team["ad"]
                self.goal_meme_text = f"{scorer_team.upper()} ATTI!"

                self.sound_mgr.play(self.sound_mgr.goal_sound)
                self.sound_mgr.play(self.sound_mgr.crowd_cheer_sound)
                if self.sound_mgr.goal_voice_sound:
                    self.sound_mgr.play(self.sound_mgr.goal_voice_sound)
                self.spawn_confetti(self.ball.x, self.ball.y, [self.p2.team["renk1"], self.p2.team["renk2"]])
                self.show_commentary(random.choice(self.goal_commentary_quotes).format(team=scorer_team.upper()), 110, YELLOW)
                self.play_meme_video("gol", scorer_team, next_state="oyun", title=f"{scorer_team} GOL ANI")

            elif self.goal_right.is_goal(self.ball):
                self.score_p1 += 1
                self.goal_popup_timer = 95
                scorer_team = self.p1.team["ad"]
                self.goal_meme_text = f"{scorer_team.upper()} ATTI!"

                self.sound_mgr.play(self.sound_mgr.goal_sound)
                self.sound_mgr.play(self.sound_mgr.crowd_cheer_sound)
                if self.sound_mgr.goal_voice_sound:
                    self.sound_mgr.play(self.sound_mgr.goal_voice_sound)
                self.spawn_confetti(self.ball.x, self.ball.y, [self.p1.team["renk1"], self.p1.team["renk2"]])
                self.show_commentary(random.choice(self.goal_commentary_quotes).format(team=scorer_team.upper()), 110, YELLOW)
                self.play_meme_video("gol", scorer_team, next_state="oyun", title=f"{scorer_team} GOL ANI")

    def finish_match(self):
        self.sound_mgr.play(self.sound_mgr.whistle_sound)

        if self.score_p1 > self.score_p2:
            winner_team = self.p1.team["ad"]
            self.match_winner_text = f"KAZANAN: {winner_team.upper()} (P1)!"
            video_played = self.play_meme_video("mac_sonu", winner_team, next_state="mac_sonu", title=f"{winner_team} GALİBİYETİ")
        elif self.score_p2 > self.score_p1:
            winner_team = self.p2.team["ad"]
            display_side = "BOT" if self.game_mode == "1_oyuncu" else "P2"
            self.match_winner_text = f"KAZANAN: {winner_team.upper()} ({display_side})!"
            video_played = self.play_meme_video("mac_sonu", winner_team, next_state="mac_sonu", title=f"{winner_team} GALİBİYETİ")
        else:
            self.match_winner_text = "MAÇ BERABERE BİTTİ!"
            video_played = self.play_meme_video("mac_sonu", "beraberlik", next_state="mac_sonu", title="BERABERLİK ANI")

        if not video_played:
            self.state = "mac_sonu"

    def draw_game(self):
        self.screen.blit(self.bg_surf, (0, 0))

        if self.goal_left_scale_timer > 0:
            self._draw_goal_overlay(self.goal_left, (255, 90, 90) if self.goal_left.height < self.goal_left.base_height else (90, 255, 130))
        if self.goal_right_scale_timer > 0:
            self._draw_goal_overlay(self.goal_right, (255, 90, 90) if self.goal_right.height < self.goal_right.base_height else (90, 255, 130))

        self.p1.draw(self.screen, self.face_images, self.ground_y)
        self.p2.draw(self.screen, self.face_images, self.ground_y)
        self.ball.draw(self.screen, self.ground_y)

        for p in self.particles:
            p.draw(self.screen)

        self.draw_back_button()

        hud_box = pygame.Rect(SCREEN_WIDTH // 2 - 220, 12, 440, 72)
        pygame.draw.rect(self.screen, BLACK, hud_box, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, hud_box, 2, border_radius=10)

        score_txt = self.font_hud.render(f"{self.score_p1}  -  {self.score_p2}", True, YELLOW)
        self.screen.blit(score_txt, score_txt.get_rect(center=(SCREEN_WIDTH // 2, 36)))

        self.screen.blit(self.cached_p1_name, (hud_box.left + 15, 30))
        self.screen.blit(self.cached_p2_name, self.cached_p2_name.get_rect(right=hud_box.right - 15, centery=42))

        current_sec = int(self.match_time)
        if current_sec != self.last_rendered_second:
            self.last_rendered_second = current_sec
            mins = current_sec // 60
            secs = current_sec % 60
            time_color = RED if self.match_time <= 10.0 else WHITE
            self.cached_time_surf = self.font_btn.render(f"{mins:02d}:{secs:02d}", True, time_color)

        if self.cached_time_surf:
            self.screen.blit(self.cached_time_surf, self.cached_time_surf.get_rect(center=(SCREEN_WIDTH // 2, 65)))

        # Güç göstergeleri (hazır/bekleme)
        self._draw_power_indicator(self.p1, hud_box.left - 10, 46, align_right=True)
        self._draw_power_indicator(self.p2, hud_box.right + 10, 46, align_right=False)

        # Spiker banner (yazılı yorum)
        if self.commentary_timer > 0:
            self.commentary_timer -= 1
            alpha = 255
            if self.commentary_timer < 20:
                alpha = int(255 * (self.commentary_timer / 20))
            banner = pygame.Surface((SCREEN_WIDTH, 38), pygame.SRCALPHA)
            banner.fill((0, 0, 0, 150))
            txt_surf = self.font_sub.render(self.commentary_text, True, self.commentary_color)
            banner.blit(txt_surf, txt_surf.get_rect(center=(SCREEN_WIDTH // 2, 19)))
            banner.set_alpha(alpha)
            self.screen.blit(banner, (0, 92))

        # Büyük geri sayım (son 5 saniye)
        if self.countdown_flash_timer > 0 and self.last_countdown_number:
            cd_surf = self.font_countdown.render(str(self.last_countdown_number), True, RED)
            cd_outline = self.font_countdown.render(str(self.last_countdown_number), True, BLACK)
            rect = cd_surf.get_rect(center=(SCREEN_WIDTH // 2, 170))
            self.screen.blit(cd_outline, (rect.x + 4, rect.y + 4))
            self.screen.blit(cd_surf, rect)

        # Büyük "SÜPER GÜÇ" yazısı
        if self.super_power_banner_timer > 0:
            sp_surf = self.font_mim.render("SÜPER GÜÇ!", True, POWER_PINK)
            sp_outline = self.font_mim.render("SÜPER GÜÇ!", True, BLACK)
            rect = sp_surf.get_rect(center=(SCREEN_WIDTH // 2, 150))
            self.screen.blit(sp_outline, (rect.x + 3, rect.y + 3))
            self.screen.blit(sp_surf, rect)

        if self.goal_popup_timer > 0:
            meme_surf = self.font_mim.render(self.goal_meme_text, True, ORANGE)
            outline_surf = self.font_mim.render(self.goal_meme_text, True, BLACK)
            rect = meme_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
            self.screen.blit(outline_surf, (rect.x + 3, rect.y + 3))
            self.screen.blit(meme_surf, rect)

    def _draw_power_indicator(self, player, x, y, align_right):
        if not player.power_id:
            return
        ready = player.power_cooldown_timer <= 0
        col = (90, 230, 120) if ready else (150, 150, 150)
        w, h = 90, 22
        rect = pygame.Rect(x - w if align_right else x, y, w, h)
        pygame.draw.rect(self.screen, col, rect, border_radius=6)
        pygame.draw.rect(self.screen, BLACK, rect, 2, border_radius=6)
        label = "HAZIR" if ready else f"{player.power_cooldown_timer // FPS + 1}sn"
        txt = self.font_btn.render(label, True, BLACK)
        f = pygame.font.SysFont("arial", 14, bold=True)
        txt = f.render(label, True, BLACK)
        self.screen.blit(txt, txt.get_rect(center=rect.center))

    # --- DURUM 6: MAÇ SONU EKRANI ---
    def handle_match_over(self, events):
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mouse_pos = e.pos
                if self.draw_back_button().collidepoint(mouse_pos) or self.btn_menu_return.collidepoint(mouse_pos):
                    self.state = "menu"

    def draw_match_over(self):
        self.screen.fill((25, 25, 30))
        self.draw_back_button()

        t_surf = self.font_title.render("MAÇ BİTTİ!", True, YELLOW)
        self.screen.blit(t_surf, t_surf.get_rect(center=(SCREEN_WIDTH // 2, 130)))

        win_surf = self.font_hud.render(self.match_winner_text, True, WHITE)
        self.screen.blit(win_surf, win_surf.get_rect(center=(SCREEN_WIDTH // 2, 220)))

        final_score_str = f"Skor: {self.score_p1} - {self.score_p2}"
        sc_surf = self.font_mim.render(final_score_str, True, ORANGE)
        self.screen.blit(sc_surf, sc_surf.get_rect(center=(SCREEN_WIDTH // 2, 300)))

        self.btn_menu_return = pygame.Rect(SCREEN_WIDTH // 2 - 140, 420, 280, 56)
        hover = self.btn_menu_return.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(self.screen, BLUE_ACCENT if hover else DARK_GRAY, self.btn_menu_return, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, self.btn_menu_return, 2, border_radius=10)
        r_txt = self.font_btn.render("ANA MENÜYE DÖN", True, WHITE)
        self.screen.blit(r_txt, r_txt.get_rect(center=self.btn_menu_return.center))

    # --- ANA DÖNGÜ ---
    def run(self):
        running = True
        while running:
            events = pygame.event.get()
            for e in events:
                if e.type == pygame.QUIT:
                    running = False

            if self.state == "menu":
                self.handle_menu(events)
                self.draw_menu()
            elif self.state == "ozellestirme":
                self.handle_customization(events)
                self.draw_customization()
            elif self.state == "tus_ayarlari":
                self.handle_controls(events)
                self.draw_controls()
            elif self.state == "takim_secim":
                self.handle_team_selection(events)
                self.draw_team_selection()
            elif self.state == "ozel_guc_secim":
                self.handle_ozel_guc_secim(events)
                self.draw_ozel_guc_secim()
            elif self.state == "oyun":
                self.handle_game(events)
                self.update_game()
                self.draw_game()
            elif self.state == "video_oynatma":
                self.handle_video_events(events)
                self.update_and_draw_video()
            elif self.state == "mac_sonu":
                self.handle_match_over(events)
                self.draw_match_over()

            pygame.display.flip()
            self.clock.tick(FPS)

        self.stop_current_video()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()

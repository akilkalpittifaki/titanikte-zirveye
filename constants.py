import pygame

# Oyun penceresi boyutları
WIDTH, HEIGHT = 1920, 1080
FPS = 60

# Renkler
DARK_BLUE = (10, 20, 50)
LIGHT_BLUE = (65, 105, 225)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
DARK_BROWN = (90, 40, 10)
BUTTON_COLOR = (180, 180, 200)

# Oyun durumları
MAIN_MENU = 0
PLAYING = 1
STOCK_MARKET = 2
INVENTORY = 3
DIALOG = 4
GAME_OVER = 5

# Font ayarları
pygame.font.init()
FONT_SMALL = pygame.font.SysFont("Arial", 24)
FONT_MEDIUM = pygame.font.SysFont("Arial", 32)
FONT_LARGE = pygame.font.SysFont("Arial", 48)

# Oda bilgileri
ROOMS = {
    "güverte": {
        "name": "Ana Güverte",
        "bounds": (WIDTH//2 - 600, 300, WIDTH//2 + 600, HEIGHT - 50),
        "exits": {
            "borsa": (WIDTH - 200, 350),
            "kabin": (200, 350),
            "çalışma_alanı": (WIDTH // 2, 400)
        }
    },
    "borsa": {
        "name": "Borsa Salonu",
        "bounds": (0, 0, WIDTH, HEIGHT),
        "exits": {
            "güverte": (WIDTH // 2, HEIGHT - 100)
        }
    },
    "kabin": {
        "name": "Kabin",
        "bounds": (0, 0, WIDTH, HEIGHT),
        "exits": {
            "güverte": (WIDTH // 2, HEIGHT - 100)
        }
    },
    "çalışma_alanı": {
        "name": "Çalışma Alanı",
        "bounds": (0, 0, WIDTH, HEIGHT),
        "exits": {
            "güverte": (WIDTH // 2, HEIGHT - 100)
        }
    }
}
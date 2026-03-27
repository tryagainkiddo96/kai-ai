import config


class Config:
    APP_NAME = getattr(config, 'APP_NAME', 'WormGPT V7')
    VERSION = getattr(config, 'VERSION', '7.0.0')

    ACCENT_COLOR = '#00C6FF'
    ACCENT_GRADIENT = 'qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #00C6FF, stop:1 #0072FF)'
    CARD_GRADIENT = 'qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #111827, stop:1 #1f2937)'
    TEAL_GRADIENT = 'qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #1de9b6, stop:1 #00bfa5)'
    NEON_GRADIENT = 'qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #8e2de2, stop:1 #4a00e0)'
    MODERN_GRADIENT_1 = 'qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #141E30, stop:1 #243B55)'

    BUTTON_HOVER = '#14c4c4'
    BUTTON_PRESSED = '#0f9e9e'
    ERROR_COLOR = '#ff4d4f'

    FONT_FAMILY = 'Segoe UI'
    FONT_FAMILY_MONO = 'Consolas'
    FONT_SIZE_HEADER = 28
    FONT_SIZE_TITLE = 24
    FONT_SIZE_LARGE = 18
    FONT_SIZE_MEDIUM = 15
    FONT_SIZE_NORMAL = 13
    FONT_SIZE_SMALL = 12

    TEXT_COLOR = '#FFFFFF'
    TEXT_SECONDARY = '#cbd5e1'
    TEXT_MUTED = '#94a3b8'

    WINDOW_MIN_WIDTH = 1200
    WINDOW_MIN_HEIGHT = 780

    AI_MODEL_TECHNICAL = 'gpt-4o'
    AI_MODEL_DISPLAY = 'GPT-4o'

    SPLASH_DURATION = 2800

    API_BASE_URL = 'https://api.example.com'

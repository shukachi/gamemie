"""
Game configuration.
Resolution, brightness, and other display settings.
"""
import json
import os
import arcade

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Arcade Club"

# Graphics
BRIGHTNESS = 1.0
FULLSCREEN = True
RESOLUTION = (1280, 720)  # used in windowed mode

# Sound
LOBBY_MUSIC_VOLUME = 0.5
SETTINGS_MUSIC_VOLUME = 0.5

# Game
FPS = 60
PLAYER_SPEED = 200  # pixels per second

# Machines
MACHINES_PER_ROW = 3
MACHINE_SPACING_X = 350
MACHINE_SPACING_Y = 300
MACHINE_START_X = 200
MACHINE_START_Y = 200

# Attempts
ATTEMPTS_PER_MACHINE = 3

# UI
DIALOG_WIDTH = 400
DIALOG_HEIGHT = 300

# Key bindings (mutable — changed at runtime by controls dialog)
KEY_BINDINGS = {
    'up':       arcade.key.W,
    'down':     arcade.key.S,
    'left':     arcade.key.A,
    'right':    arcade.key.D,
    'interact': arcade.key.E,
}

# Mouse control flag
MOUSE_CONTROL = False

# ── Persistence ───────────────────────────────────────────────────────
_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "data", "settings.json")


def save_settings() -> None:
    global FULLSCREEN, RESOLUTION, LOBBY_MUSIC_VOLUME, SETTINGS_MUSIC_VOLUME
    os.makedirs(os.path.dirname(_FILE), exist_ok=True)
    with open(_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "fullscreen": FULLSCREEN,
            "resolution": list(RESOLUTION),
            "lobby_music_volume": LOBBY_MUSIC_VOLUME,
            "settings_music_volume": SETTINGS_MUSIC_VOLUME,
        }, f)


def load_settings() -> None:
    global FULLSCREEN, RESOLUTION, LOBBY_MUSIC_VOLUME, SETTINGS_MUSIC_VOLUME
    if not os.path.exists(_FILE):
        return
    try:
        with open(_FILE, encoding="utf-8") as f:
            data = json.load(f)
        FULLSCREEN = bool(data.get("fullscreen", FULLSCREEN))
        res = data.get("resolution")
        if res and len(res) == 2:
            RESOLUTION = tuple(res)
        LOBBY_MUSIC_VOLUME = float(data.get("lobby_music_volume", LOBBY_MUSIC_VOLUME))
        SETTINGS_MUSIC_VOLUME = float(data.get("settings_music_volume", SETTINGS_MUSIC_VOLUME))
    except Exception:
        pass

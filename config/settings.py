"""
Game configuration.
Resolution, brightness, and other display settings.
"""
import arcade

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Arcade Club"

# Graphics
BRIGHTNESS = 1.0
FULLSCREEN = False

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

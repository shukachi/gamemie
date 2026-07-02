"""
Guide for adding new arcade games to the project.
"""

# HOW TO ADD A NEW GAME

## Step 1: Create Your Game Class

1. Copy `src/games/TEMPLATE_GAME.py` and rename it to your game (e.g., `src/games/breakout_game.py`)
2. Rename the class from `MyCustomGame` to your game name (e.g., `BreakoutGame`)
3. Implement the game logic by filling in the TODO sections:
   - `on_show()`: Initialize game state
   - `on_draw()`: Render all game elements
   - `on_update(delta_time)`: Update game logic each frame
   - `on_key_press()`: Handle keyboard input
   - Add any additional methods you need

## Step 2: Register Your Game

Add your game to the `GameRegistry` in `src/games/registry.py`:

```python
from src.games.breakout_game import BreakoutGame

class GameRegistry:
    MACHINES = [
        # ... existing machines ...
        {
            'id': 'breakout_1',           # Unique ID for this machine
            'name': 'Breakout Game',      # Display name in lobby
            'game_class': BreakoutGame,
        },
    ]
```

## Step 3: Add Sprites and Assets (Optional)

- Place sprites in `assets/sprites/`
- Place background images in `assets/backgrounds/`
- Place sound effects in `assets/sounds/`
- Use paths like `assets/sprites/my_sprite.png` when loading

## Step 4: Score System

The `on_finish_callback` is called with `(score, completed)` when the game ends:
- `score`: Points earned in this game session
- `completed`: True if player finished normally, False if they quit early

Update `self.score` throughout the game and call `self.finish_game(True)` when done.

## Key APIs

### BaseGame class (inherit from this):
- `self.score`: Current game score (int)
- `self.time_remaining`: Game duration in seconds
- `self.finish_game(completed: bool)`: End the game and return to lobby

### Arcade Library:
- Drawing: `arcade.draw_rectangle_filled()`, `arcade.draw_circle_filled()`, `arcade.draw_text()`, etc.
- Input: Handle `on_key_press()`, `on_key_release()`, `on_mouse_press()`
- Sprites: Load with `arcade.Sprite()`
- See: https://api.arcade.academy/

## Example: Simple Click Counter Game

```python
import arcade
from src.games.base_game import BaseGame
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT

class ClickerGame(BaseGame):
    def __init__(self, machine_id: str, on_finish_callback):
        super().__init__("Clicker Game", machine_id, on_finish_callback)
        self.elapsed_time = 0
        self.time_remaining = 30

    def on_show(self):
        self.elapsed_time = 0
        self.score = 0

    def on_draw(self):
        arcade.start_render()
        arcade.draw_rectangle_filled(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                      SCREEN_WIDTH, SCREEN_HEIGHT,
                                      arcade.color.LIGHT_BLUE)
        arcade.draw_text(f"Clicks: {self.score}", 50, SCREEN_HEIGHT - 50,
                        font_size=20, color=arcade.color.BLACK)
        arcade.draw_text(f"Time: {max(0, self.time_remaining - self.elapsed_time):.1f}s",
                        50, SCREEN_HEIGHT - 100, font_size=16, color=arcade.color.BLACK)

    def on_update(self, delta_time: float):
        self.elapsed_time += delta_time
        if self.elapsed_time >= self.time_remaining:
            self.finish_game(True)

    def on_key_press(self, key: int, modifiers: int):
        if key == arcade.key.SPACE:
            self.score += 1
        elif key == arcade.key.ESCAPE:
            self.finish_game(False)

# Then register in registry.py:
# {
#     'id': 'clicker_1',
#     'name': 'Clicker',
#     'game_class': ClickerGame,
# }
```

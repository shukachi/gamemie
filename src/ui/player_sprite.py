"""Player sprite with directional walking animation from an 8x4 spritesheet."""

from pathlib import Path
from PIL import Image
import arcade

COLUMNS = 6    # actual frames per direction (detected from sprite content)
ROWS = 4
FRAME_W = 32   # width of each normalized frame cell
FRAME_H = 43   # height: 172 / 4 rows
ANIMATION_FPS = 8.0

_DIRECTION_ROW = {
    "down":  0,
    "left":  1,
    "right": 2,
    "up":    3,
}

_SRC_HANDLE  = ":player:girl_sprite.png"
_FIXED_HANDLE = ":player:girl_sprite_fixed.png"


def _detect_frame_centers(img: Image.Image, row: int) -> list[int]:
    """Return the center x of each character in the given sprite row."""
    y0 = row * FRAME_H
    w = img.width
    # Collect columns with any visible pixel
    opaque = []
    for x in range(w):
        for y in range(y0, y0 + FRAME_H):
            if img.getpixel((x, y))[3] > 10:
                opaque.append(x)
                break

    if not opaque:
        return []

    # Group consecutive opaque columns into content regions
    regions: list[tuple[int, int]] = []
    start = opaque[0]
    prev = opaque[0]
    for x in opaque[1:]:
        if x > prev + 3:          # gap wider than 3px = frame separator
            regions.append((start, prev))
            start = x
        prev = x
    regions.append((start, prev))

    # Keep only substantial regions (ignore thin artefacts)
    regions = [(a, b) for a, b in regions if b - a >= 4]
    return [(a + b) // 2 for a, b in regions]


def _build_fixed_sheet(src: Path, dst: Path) -> None:
    """
    Rebuild the sprite sheet so every frame is a properly-centred FRAME_W x FRAME_H cell.
    The original sheet has 6 characters per row, unevenly spaced — this fixes that.
    """
    img = Image.open(src).convert("RGBA")
    half = FRAME_W // 2
    new_img = Image.new("RGBA", (COLUMNS * FRAME_W, ROWS * FRAME_H), (0, 0, 0, 0))

    for row in range(ROWS):
        y0 = row * FRAME_H
        centers = _detect_frame_centers(img, row)[:COLUMNS]
        for col, cx in enumerate(centers):
            x0 = max(0, cx - half)
            x1 = x0 + FRAME_W
            if x1 > img.width:
                x1 = img.width
                x0 = max(0, x1 - FRAME_W)
            frame = img.crop((x0, y0, x1, y0 + FRAME_H))
            new_img.paste(frame, (col * FRAME_W, y0))

    new_img.save(dst)


class PlayerSprite:
    """Renders the player as an animated sprite with 4-directional walk animation."""

    def __init__(self, x: float, y: float, scale: float = 2.5):
        self.x = x
        self.y = y
        self.scale = scale

        src_path  = arcade.resources.resolve_resource_path(_SRC_HANDLE)
        fixed_path = arcade.resources.resolve_resource_path(_FIXED_HANDLE)

        if not fixed_path.exists():
            _build_fixed_sheet(src_path, fixed_path)

        sheet = arcade.load_spritesheet(_FIXED_HANDLE)
        all_frames = sheet.get_texture_grid(
            size=(FRAME_W, FRAME_H),
            columns=COLUMNS,
            count=COLUMNS * ROWS,
        )

        self._textures: dict[str, list[arcade.Texture]] = {}
        for direction, row in _DIRECTION_ROW.items():
            start = row * COLUMNS
            self._textures[direction] = all_frames[start: start + COLUMNS]

        self.direction = "down"
        self._frame_idx = 0
        self._timer = 0.0

    @property
    def draw_width(self) -> float:
        return FRAME_W * self.scale

    @property
    def draw_height(self) -> float:
        return FRAME_H * self.scale

    def update(self, dt: float, speed_x: float, speed_y: float) -> None:
        moving = speed_x != 0 or speed_y != 0

        if abs(speed_x) >= abs(speed_y):
            if speed_x > 0:
                self.direction = "right"
            elif speed_x < 0:
                self.direction = "left"
        else:
            if speed_y > 0:
                self.direction = "up"
            elif speed_y < 0:
                self.direction = "down"

        if moving:
            self._timer += dt
            frame_duration = 1.0 / ANIMATION_FPS
            while self._timer >= frame_duration:
                self._timer -= frame_duration
                self._frame_idx = (self._frame_idx + 1) % COLUMNS
        else:
            self._frame_idx = 0
            self._timer = 0.0

    def draw(self) -> None:
        texture = self._textures[self.direction][self._frame_idx]
        arcade.draw_texture_rect(
            texture,
            arcade.XYWH(self.x, self.y, self.draw_width, self.draw_height),
        )

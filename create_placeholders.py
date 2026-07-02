"""
Asset placeholder generator.
Creates placeholder images for quick testing.
Requires PIL (Pillow) - can be extended with real art later.
"""

import os
from pathlib import Path


def create_placeholder_assets():
    """
    Create placeholder sprite images.
    This is optional - games can work without image files initially.
    """
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("PIL not available - using placeholder text rendering instead")
        print("Install Pillow for better placeholder images: pip install Pillow")
        return

    assets_dir = Path("assets")

    # Background placeholder
    bg_dir = assets_dir / "backgrounds"
    bg_dir.mkdir(parents=True, exist_ok=True)
    bg_img = Image.new("RGB", (1280, 720), color=(30, 40, 60))
    draw = ImageDraw.Draw(bg_img)
    draw.text((100, 100), "Arcade Club Lobby", fill=(200, 200, 200))
    bg_img.save(bg_dir / "lobby_bg.png")

    # Sprite placeholders
    sprites_dir = assets_dir / "sprites"
    sprites_dir.mkdir(parents=True, exist_ok=True)

    # Machine sprite
    machine_img = Image.new("RGB", (64, 64), color=(0, 200, 255))
    draw = ImageDraw.Draw(machine_img)
    draw.rectangle((4, 4, 60, 60), outline=(255, 255, 255), width=2)
    draw.text((10, 25), "GAME", fill=(0, 0, 0))
    machine_img.save(sprites_dir / "machine.png")

    # Player sprite
    player_img = Image.new("RGB", (40, 40), color=(0, 255, 0))
    draw = ImageDraw.Draw(player_img)
    draw.rectangle((5, 5, 35, 35), outline=(255, 255, 255), width=2)
    player_img.save(sprites_dir / "player.png")

    print("✓ Placeholder assets created in assets/")


if __name__ == "__main__":
    create_placeholder_assets()

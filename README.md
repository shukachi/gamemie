# Arcade Club — 2D Game with Arcade Machines

A Python-based 2D game where a player walks through an arcade club lobby, plays simple mini-games on arcade machines, accumulates points, and competes in leaderboards.

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install arcade library
pip install arcade
```

### 2. Run the Game

```bash
python main.py
```

## Game Features

- **Lobby**: Walk around with arrow keys and interact with arcade machines (Press E)
- **Arcade Machines**: Each machine has 3 attempts. Complete mini-games to earn points
- **Scoring**: Accumulate points across all machines
- **Leaderboards**: Per-machine leaderboards + global club leaderboard
- **Cashier**: Visit the cashier to reset attempts or view your score
- **Persistence**: Scores are saved to JSON files

## Controls

- **Arrow Keys**: Move around the lobby
- **E**: Interact with nearby machines or cashier
- **ESC**: Exit dialogs or games

## Project Structure

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed file layout.

## Adding New Games

See [HOW_TO_ADD_GAMES.md](HOW_TO_ADD_GAMES.md) for a complete guide on:
- Creating new arcade machine games
- Registering them with the system
- Adding sprites and assets
- Scoring systems

## Customization

- **Settings**: Edit `config/settings.py` to adjust resolution, FPS, machine layout, etc.
- **Add Assets**: Place sprites, backgrounds, and sounds in `assets/` subdirectories
- **Leaderboards**: Stored in `data/leaderboards/` as JSON files

## Architecture

- **Arcade Library**: Uses Python Arcade for rendering and input handling
- **View System**: Game is organized into scenes (loading screen → lobby → games → dialogs)
- **Player State**: Tracks attempts per machine and accumulated score
- **Leaderboard System**: JSON-based persistent storage for scores

## Tech Stack

- **Language**: Python 3.12+
- **Game Library**: [Python Arcade](https://api.arcade.academy/)
- **Data Storage**: JSON files

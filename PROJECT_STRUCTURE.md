# Project Structure

```
gamemie/
├── main.py                          # Entry point - run this to start the game
├── requirements.txt                 # Python dependencies
├── CLAUDE.md                        # Claude Code guidance
├── HOW_TO_ADD_GAMES.md             # Developer guide for adding new games
│
├── config/
│   └── settings.py                 # Global game settings (resolution, FPS, etc.)
│
├── src/
│   ├── core/
│   │   ├── leaderboard.py          # Leaderboard management and storage
│   │   └── player_state.py         # Player session state tracking
│   │
│   ├── games/
│   │   ├── base_game.py            # Base class all games inherit from
│   │   ├── demo_game.py            # Example placeholder game
│   │   ├── registry.py             # Registry of all arcade machines
│   │   └── TEMPLATE_GAME.py        # Template for creating new games
│   │
│   └── ui/
│       ├── loading.py              # Loading screen
│       ├── lobby.py                # Main lobby scene with machines & cashier
│       └── dialogs.py              # UI components (confirmation, leaderboards)
│
├── assets/
│   ├── sprites/                    # Game sprites and graphics
│   ├── backgrounds/                # Background images
│   ├── sounds/                     # Audio files
│   └── fonts/                      # Custom fonts (if needed)
│
└── data/
    └── leaderboards/               # JSON files storing leaderboard scores
```

## Key Files

- **main.py** - Run this to start the game
- **config/settings.py** - Adjust screen resolution, FPS, machine layout, etc.
- **src/games/registry.py** - Add new arcade machines here
- **src/games/TEMPLATE_GAME.py** - Template for creating new games
- **HOW_TO_ADD_GAMES.md** - Detailed guide for developers

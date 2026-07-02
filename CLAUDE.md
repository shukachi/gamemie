# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Tech Stack

- **Language:** Python
- **Game library:** [Python Arcade](https://api.arcade.academy/)

## Game Concept — Arcade Club (2D)

A 2D arcade club game where a player walks around a lobby and interacts with arcade machines.

### Core Loop

1. Game starts with a **loading screen**, then the player spawns in the **lobby**.
2. The lobby contains multiple **arcade machines** and a **cashier NPC**.
3. When the player walks up to a machine, a **confirmation dialog** appears before starting the mini-game.
4. After finishing a mini-game, the player is **returned to the lobby**.
5. Each machine has **3 attempts**. When all 3 are spent, the machine is **locked** for that session.
6. When all attempts on all machines are exhausted, the **cashier** can reset all attempts, allowing the player to start accumulating points again.
7. After all attempts on all machines are spent, the **club total score** is submitted to the **global leaderboard**.

### Scoring & Leaderboards

- Each arcade machine has its own **per-machine leaderboard** (shown in the confirmation dialog before play).
- There is one **global club leaderboard** tracking total accumulated score across all machines.

### Cashier NPC

Located in the lobby. Acts as the main **game menu**, providing access to:
- Graphics settings
- Difficulty settings (per-game and global)
- Global club leaderboard
- Early session end (forfeit remaining attempts and submit score)
- Reset all attempts (when all machines are locked)

### Launcher

A separate launcher app (pre-game) handles:
- Installation
- Global settings: screen resolution, brightness, and other display options

## Architecture Notes

- Screens/views: loading screen → lobby → confirmation dialog → mini-game → back to lobby
- Each arcade machine is its own mini-game module; the lobby orchestrates launching them
- Player state (attempts per machine, accumulated score) persists for the full session
- Leaderboard data should be stored persistently (file or SQLite) so scores survive between sessions

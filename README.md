# Bloxorz

Bloxorz is a 3D puzzle game implemented in Python with the Ursina Engine.
The player rolls a rectangular block across floating platforms and must place
it upright on the goal tile. The project also includes DFS, BFS, UCS, and A*
solvers.

## Level Groups

The 12 levels are divided into four difficulty groups:

| Group | Levels | Characteristics |
| --- | --- | --- |
| Easy | 1–3 | Introduces the basic controls, rules, and simple paths. |
| Medium | 4–6 | Adds longer routes, narrow platforms, and basic switches. |
| Hard | 7–9 | Uses complex layouts, special tiles, and fewer safe routes. |
| Super Hard | 10–12 | Combines all mechanics and requires precise, multi-step planning. |

## Requirements

- Python 3.10 or later
- `pip`

The required Python packages are listed in `requirements.txt`.

## Installation

Open a terminal in the project directory and create a virtual environment:

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Running the Game

From the project root, run:

```bash
python main.py
```

Use the main menu to start the game, select a level, or choose an AI search
algorithm. Use the arrow keys to move the block.

## Running the Tests

```bash
python -m pytest
```

## Project Structure

```text
ai/       Search algorithms and solver utilities
assets/   Images and other game resources
core/     Board, block, state, and movement logic
game/     Game screens, rendering, and controllers
gui/      Statistics interface
levels/   Level definitions in JSON format
tests/    Automated tests
main.py   Application entry point
```

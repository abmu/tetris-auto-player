# engf34-assignment-4

A high-scoring Tetris Auto-Player which attempts to play optimally by assigning heuristic values to each possible move.

[tetris-auto-player.webm](https://github.com/user-attachments/assets/9c4c7f64-1fde-47d1-9981-93659a90ac99)

## Setup

1. Get a copy of this repository and change into the `tetris/` directory, using Git or otherwise.

```bash
git clone https://github.com/abmu/tetris-auto-player.git
cd tetris-auto-player/tetris/
```

2. Ensure you have Pygame installed.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pygame
```

3. If desired, adjust the weights used in the `player.py` file and settings such as the random seed in the `constants.py` file.

4. Run the game:

```bash
python3 visual-pygame.py
```

## Notes

The implementation of the custom Tetris game itself was not done by me, but instead by Prof. Mark Handley and a faculty member of the UCL department of Computer Science.

My code is limited to the following: `player.py`, `tetris_generations.py`, `generations/`. You can adjust and run the `tetris_generations.py` file to attempt to discover optimal weights using either simulated annealing or a genetic algorithm.

[Assignment brief](https://github.com/mhandley/ENGF34-2023/blob/main/assignments/assignment4/assignment4.pdf).

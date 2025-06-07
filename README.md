# Wordle Solver

A simple Wordle solver written in Python with a CLI. Works for any other similar Wordle-like games as long as you provide the possible words in a text file in the `/words/` folder. Already comes with the possible words for [Wordle](https://www.nytimes.com/games/wordle/index.html) and [Termo](https://term.ooo) and [Letreco](https://www.gabtoschi.com/letreco/). Works for guesses of any length and for any number of guesses.

Requires Python >=3.13 and [bconsole](https://pypi.org/project/bconsole/) >=0.0.11 for the CLI in `main.py`. The solver itself in `solver.py` has no dependencies.

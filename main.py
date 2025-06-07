from pathlib import Path

from bconsole import Console, Foreground, Modifier
from bconsole.utils import replace_last

from solver import Guess, LetterStatus, Solver

_COLOR_MAP = {
    LetterStatus.Correct: Foreground.GREEN,
    LetterStatus.Incorrect: (GRAY := Foreground.make_rgb(64, 64, 72)),
    LetterStatus.Miss: Foreground.YELLOW,
}


def prettify_guess(guess: Guess, /) -> str:
    return "".join(
        col(letter.char, _COLOR_MAP[letter.status]) for letter in guess.letters
    )


console = Console()
col = console.colorize

files = list(Path("./words").glob("*.txt"))

if not files:
    console.panic("No possible words list found.")

name = console.options(
    "Which words list are you going to use?",
    options=list(map(lambda f: f.stem, files)),
    title=False,
    wrapper=None,
)

solver = Solver.from_file(f"./words/{name}.txt")

console.space()

console.print("Welcome to betakors/wordle-solver!", Foreground.GREEN + Modifier.BOLD)
console.print("To guess, use the following format:")
console.print(
    f"{col('c', Foreground.GREEN)}: {col('correct', Foreground.GREEN)} letter, {col('i', GRAY)}: {col('incorrect', GRAY)} letter, {col('m', Foreground.YELLOW)}: {col('missed', Foreground.YELLOW)} letter"
)
console.print(
    f"So, for example, if the word is '{prettify_guess(Guess.from_map('apple', 'ciiim'))}', you should write:"
)
console.arrow("apple-ciiim")
console.space()

while True:
    input = console.input(f"[Guess #{len(solver.guesses) + 1}]", allow_extras=True)

    if "-" not in input:
        console.error("Invalid guess.", hint="Guesses must be in the correct format.")
        continue

    try:
        solver.add_guess(guess := Guess.from_map(*input.split("-")))
    except ValueError:
        console.error(
            "Invalid guess.",
            hint=f"Guesses must have the same length as the possible words ({solver.word_length} characters).",
        )
        continue

    words_left = solver.solve()

    console.erase_lines()
    console.arrow(prettify_guess(guess))

    if len(words_left) == 0:
        console.error("No words left. Something went wrong.")
        break
    elif len(words_left) == 1:
        console.arrow(f"Final word: {words_left[0]}")
        break
    else:
        console.print(f"{len(words_left)} Words left.", end=" ")

        if len(words_left) > 2000:
            console.print("Too many words to display.", GRAY)
        else:
            console.print(
                f"They are: {replace_last(', '.join(words_left), ',', ' and')}.",  # type: ignore
                GRAY,
            )

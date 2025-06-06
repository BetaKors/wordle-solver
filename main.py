from bconsole import Console, Foreground, Modifier

from solver import Guess, Solver


def colorize(text: str, color: str) -> str:
    return f"{color}{text}{Modifier.RESET}"


GRAY = Foreground.make_rgb(64, 64, 72)

console = Console()

if (
    console.options("Which game are you playing?", options=["Wordle", "Termo"])
    == "Wordle"
):
    file = "wordle_words.txt"
else:
    file = "termooo_words.txt"

solver = Solver.from_file(file)

console.clear()

console.print("Welcome to The Solver™!", Foreground.GREEN + Modifier.BOLD)
console.print("To guess, use the following format:")
console.print(
    f"{colorize('c', Foreground.GREEN)}: {colorize('correct', Foreground.GREEN)} letter, {colorize('i', GRAY)}: {colorize('incorrect', GRAY)} letter, {colorize('m', Foreground.YELLOW)}: {colorize('missed', Foreground.YELLOW)} letter"
)
console.print(
    f"So, for example, if the word is '{str(Guess.from_map('apple', 'ciiim'))}', you should write:"
)
console.arrow("apple-ciiim")
console.space()

while True:
    input = console.input(f"[Guess #{len(solver.guesses) + 1}] ", allow_extras=True)

    if "-" not in input:
        console.error("Invalid guess.", hint="Guesses must be in the correct format.")
        continue

    try:
        solver.guess(guess := Guess.from_map(*input.split("-")))
    except ValueError:
        console.error(
            "Invalid guess.",
            hint=f"Guesses must have the same length as the possible words ({solver.word_length} characters).",
        )
        continue

    words_left = solver.solve()

    console.erase_lines()
    console.arrow(str(guess))

    if len(words_left) == 0:
        console.print("No words left. Something went wrong.", Foreground.RED)
        break
    elif len(words_left) == 1:
        console.arrow(f"Final word: {words_left[0]}")
        break
    else:
        console.print(f"{len(words_left)} Words left.", end=" ")
        console.print(f"They are: {', '.join(words_left)}", GRAY)

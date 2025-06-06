from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import ClassVar, Self, final

from bconsole import Foreground, Modifier


@final
class GuessType(Enum):
    Correct = 1
    Incorrect = auto()
    Miss = auto()


@final
@dataclass(frozen=True)
class Letter:
    char: str
    type: GuessType

    _COLOR_MAP: ClassVar = {
        GuessType.Correct: Foreground.GREEN,
        GuessType.Incorrect: Foreground.make_rgb(64, 64, 72),
        GuessType.Miss: Foreground.YELLOW,
    }

    def __str__(self) -> str:
        return self._COLOR_MAP[self.type] + self.char + Modifier.RESET


@final
@dataclass(frozen=True)
class Guess:
    letters: list[Letter]

    _TYPE_MAP: ClassVar = {
        "c": GuessType.Correct,
        "i": GuessType.Incorrect,
        "m": GuessType.Miss,
    }

    @classmethod
    def from_map(cls, word: str, map: str, /) -> Self:
        return cls(
            [
                Letter(char.lower(), cls._TYPE_MAP[type.lower()])
                for char, type in zip(word, map)
            ],
        )

    def __str__(self) -> str:
        return "".join(str(letter) for letter in self.letters)

    def __len__(self) -> int:
        return len(self.letters)


class Solver:
    def __init__(
        self, possible_words: list[str], /, *, guesses: list[Guess] | None = None
    ) -> None:
        self._possible_words = possible_words
        self._guesses = guesses or []

        self._word_length = len(possible_words[0])

        for guess in self._guesses:
            self._validate_guess(guess)

    @classmethod
    def from_file(
        cls, path: Path | str, /, *, guesses: list[Guess] | None = None
    ) -> Self:
        with open(path, mode="r", encoding="utf-8") as file:
            return cls(file.read().splitlines(), guesses=guesses)

    @property
    def guesses(self) -> list[Guess]:
        return self._guesses

    @property
    def word_length(self) -> int:
        return self._word_length

    @property
    def _all_letters(self) -> set[Letter]:
        return {letter for guess in self._guesses for letter in guess.letters}

    @property
    def _incorrect_chars(self) -> set[str]:
        return {
            letter.char
            for letter in self._all_letters
            if letter.type == GuessType.Incorrect
            and letter.char not in self._correct_chars
            and letter.char not in self._miss_chars
        }

    @property
    def _correct_chars(self) -> set[str]:
        return {
            letter.char
            for letter in self._all_letters
            if letter.type == GuessType.Correct
        }

    @property
    def _miss_chars(self) -> set[str]:
        return {
            letter.char for letter in self._all_letters if letter.type == GuessType.Miss
        }

    @property
    def _correct_chars_pos(self) -> list[tuple[str, int]]:
        return [
            (letter.char, i)
            for guess in self._guesses
            for i, letter in enumerate(guess.letters)
            if letter.type == GuessType.Correct
        ]

    @property
    def _miss_chars_pos(self) -> list[tuple[str, int]]:
        return [
            (letter.char, i)
            for guess in self._guesses
            for i, letter in enumerate(guess.letters)
            if letter.type == GuessType.Miss
        ]

    def guess(self, guess: Guess, /) -> None:
        self._validate_guess(guess)
        self._guesses.append(guess)

    def solve(self) -> list[str]:
        return list(filter(self._keep_word, self._possible_words))

    def _keep_word(self, word: str, /) -> bool:
        return (
            not any(char in self._incorrect_chars for char in word)
            and all(letter == word[i] for letter, i in self._correct_chars_pos)
            and all(letter != word[i] for letter, i in self._miss_chars_pos)
            and all(letter in word for letter in self._miss_chars)
        )

    def _validate_guess(self, guess: Guess, /) -> None:
        if len(guess) != self._word_length:
            raise ValueError("Guess must have the same length as the possible words")

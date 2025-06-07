from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import ClassVar, Self, Sequence, final


@final
class LetterStatus(Enum):
    Correct = 1
    Incorrect = auto()
    Miss = auto()


@final
@dataclass(frozen=True)
class Letter:
    char: str
    status: LetterStatus


@final
@dataclass(frozen=True)
class Guess:
    letters: list[Letter]

    _CHAR_TO_STATUS_MAP: ClassVar = {
        "c": LetterStatus.Correct,
        "i": LetterStatus.Incorrect,
        "m": LetterStatus.Miss,
    }

    @classmethod
    def from_map(cls, word: str, map: str, /) -> Self:
        return cls(
            [
                Letter(char.lower(), cls._CHAR_TO_STATUS_MAP[type.lower()])
                for char, type in zip(word, map)
            ],
        )

    @property
    def word(self) -> str:
        return "".join(letter.char for letter in self.letters)

    def __len__(self) -> int:
        return len(self.letters)


@final
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
    def guesses(self) -> Sequence[Guess]:
        return self._guesses.copy()

    @property
    def word_length(self) -> int:
        return self._word_length

    def add_guess(self, guess: Guess, /) -> None:
        self._validate_guess(guess)
        self._guesses.append(guess)

    def remove_guess(self, guess: Guess | str, /) -> None:
        if isinstance(guess, str):
            self._guesses.remove(next(filter(lambda g: g.word == guess, self._guesses)))
            return

        self._guesses.remove(guess)

    def clear_guesses(self) -> None:
        self._guesses.clear()

    def solve(self) -> list[str]:
        return list(filter(self._keep_word, self._possible_words))

    def _keep_word(self, word: str, /) -> bool:
        all_letters = {letter for guess in self._guesses for letter in guess.letters}

        correct_chars = {
            letter.char
            for letter in all_letters
            if letter.status == LetterStatus.Correct
        }

        miss_chars = {
            letter.char for letter in all_letters if letter.status == LetterStatus.Miss
        }

        incorrect_chars = {
            letter.char
            for letter in all_letters
            if letter.status == LetterStatus.Incorrect
            and letter.char not in correct_chars
            and letter.char not in miss_chars
        }

        correct_chars_pos = [
            (letter.char, i)
            for guess in self._guesses
            for i, letter in enumerate(guess.letters)
            if letter.status == LetterStatus.Correct
        ]

        miss_chars_pos = [
            (letter.char, i)
            for guess in self._guesses
            for i, letter in enumerate(guess.letters)
            if letter.status == LetterStatus.Miss
        ]

        return (
            not any(char in incorrect_chars for char in word)
            and all(letter == word[i] for letter, i in correct_chars_pos)
            and all(letter != word[i] for letter, i in miss_chars_pos)
            and all(letter in word for letter in miss_chars)
        )

    def _validate_guess(self, guess: Guess, /) -> None:
        if len(guess) != self._word_length:
            raise ValueError("Guess must have the same length as the possible words")

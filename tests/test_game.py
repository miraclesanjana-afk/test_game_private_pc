import io
import random
import unittest
from unittest.mock import patch

import main
from main import WORD_BANK, scramble_word, show_hint


class ScrambleWordTests(unittest.TestCase):
    def test_scramble_contains_same_letters_but_is_not_the_original(self):
        for word, _ in WORD_BANK:
            scrambled = scramble_word(word, random.Random(1))
            self.assertNotEqual(scrambled, word)
            self.assertCountEqual(scrambled, word)

    def test_hint_includes_first_letter_and_word_length(self):
        self.assertEqual(show_hint("python"), "It starts with 'p' and has 6 letters.")


class GameFlowTests(unittest.TestCase):
    def test_hint_and_skip_work_during_a_game(self):
        rounds = [("python", "Programming"), ("guitar", "Music")]
        output = io.StringIO()

        with patch("main.random.sample", return_value=rounds):
            with patch("builtins.input", side_effect=["hint", "PYTHON", "skip"]):
                with patch("sys.stdout", output):
                    main.play_game()

        self.assertIn("Correct! +5 points.", output.getvalue())
        self.assertIn("Skipped! The word was 'guitar'.", output.getvalue())
        self.assertIn("Final score: 5 points | Solved: 1/2", output.getvalue())


if __name__ == "__main__":
    unittest.main()

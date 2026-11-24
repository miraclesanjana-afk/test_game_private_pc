import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


class StreamlitGameTests(unittest.TestCase):
    def create_app(self):
        app_path = Path(__file__).resolve().parents[1] / "app.py"
        return AppTest.from_file(str(app_path)).run()

    def test_correct_answer_scores_and_advances_round(self):
        app = self.create_app()
        answer = app.session_state["rounds"][0][0]

        app.text_input[0].set_value(answer.upper())
        app.button[1].click().run()

        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["score"], 10)
        self.assertEqual(app.session_state["round_index"], 1)

    def test_hint_reduces_points(self):
        app = self.create_app()
        answer = app.session_state["rounds"][0][0]

        app.button[2].click().run()
        app.text_input[0].set_value(answer)
        app.button[1].click().run()

        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["score"], 5)

    def test_skip_advances_round_and_new_game_resets_score(self):
        app = self.create_app()
        app.button[3].click().run()

        self.assertEqual(app.session_state["round_index"], 1)

        app.button[0].click().run()

        self.assertEqual(app.session_state["round_index"], 0)
        self.assertEqual(app.session_state["score"], 0)


if __name__ == "__main__":
    unittest.main()

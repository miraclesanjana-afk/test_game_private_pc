"""Terminal (CLI) front end for the word scramble game."""

from __future__ import annotations

from config import key_status
from game import ScrambleGame
from oxford_client import WordBank
from stats import Stats


def main() -> None:
    print("Word Scramble - find the Oxford-dictionary word from its scrambled letters.\n")
    status = key_status()
    print(
        "Keys present:",
        ", ".join(f"{k}={'yes' if v else 'no'}" for k, v in status.items()),
    )

    bank = WordBank.load()
    print(f"Word bank: {len(bank)} words (source: {bank.source})")

    stats = Stats.load()
    game = ScrambleGame(bank)

    try:
        while not game.is_finished:
            print(f"\nRound {game.round_no}/{game.rounds} - Score: {game.score}")
            print(f"Letters: {game.scrambled}")
            guess = input("Guess (or 'hint' / 'quit'): ").strip()
            lowered = guess.lower()
            if lowered in ("quit", "exit"):
                print("Thanks for playing!")
                return
            if lowered == "hint":
                print(f"Hint: {game.get_hint()}")
                continue
            correct, message = game.submit_guess(guess)
            print(message)
            if correct and game.current:
                print("Definition:", (game.current.get("definitions") or [""])[0])
                if game.current.get("part_of_speech"):
                    print("Part of speech:", game.current["part_of_speech"])
                if not game.is_finished:
                    game.next_round()
    except EOFError:
        pass

    if game.is_finished:
        stats.record(game.score, game.rounds)
        print(f"Game over! Final score: {game.score}  (best: {stats.best_score})")


if __name__ == "__main__":
    main()

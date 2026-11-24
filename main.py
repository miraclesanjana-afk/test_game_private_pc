import random


WORD_BANK = (
    ("python", "Programming"),
    ("keyboard", "Technology"),
    ("planet", "Space"),
    ("library", "Places"),
    ("guitar", "Music"),
    ("rainbow", "Nature"),
    ("puzzle", "Games"),
    ("volcano", "Nature"),
    ("battery", "Technology"),
    ("sandwich", "Food"),
    ("elephant", "Animals"),
    ("compass", "Travel"),
    ("notebook", "Everyday things"),
    ("mountain", "Nature"),
    ("chocolate", "Food"),
    ("telescope", "Space"),
    ("bicycle", "Travel"),
    ("festival", "Events"),
)
ROUNDS_PER_GAME = 10
POINTS_PER_ANSWER = 10
POINTS_WITH_HINT = 5


def scramble_word(word, rng=None):
    """Return a shuffled version of a word that differs from the original."""
    chooser = rng or random
    letters = list(word)
    chooser.shuffle(letters)
    scrambled = "".join(letters)

    if scrambled == word and len(letters) > 1:
        scrambled = "".join(letters[1:] + letters[:1])

    return scrambled


def show_hint(word):
    """Return a short hint containing the first letter and word length."""
    return f"It starts with '{word[0]}' and has {len(word)} letters."


def play_game():
    print("=== WORD SCRAMBLE ===")
    print("Unscramble each word and type your answer.")
    print("Commands: hint (half points), skip, quit\n")

    score = 0
    solved = 0
    rounds = random.sample(WORD_BANK, k=min(ROUNDS_PER_GAME, len(WORD_BANK)))

    for round_number, (word, category) in enumerate(rounds, start=1):
        used_hint = False
        print(f"Round {round_number}/{len(rounds)} | Category: {category}")
        print(f"Scrambled word: {scramble_word(word).upper()}")

        while True:
            answer = input("Your answer: ").strip().casefold()

            if answer == "quit":
                print("\nThanks for playing!")
                print(f"Final score: {score} points | Solved: {solved}")
                return

            if answer == "hint":
                if used_hint:
                    print("You've already used the hint for this word.")
                else:
                    print(show_hint(word))
                    used_hint = True
                continue

            if answer == "skip":
                print(f"Skipped! The word was '{word}'.\n")
                break

            if answer == word:
                earned = POINTS_WITH_HINT if used_hint else POINTS_PER_ANSWER
                score += earned
                solved += 1
                print(f"Correct! +{earned} points.\n")
                break

            print("Not quite. Try again, ask for a hint, or type 'skip'.")

    print("Game over!")
    print(f"Final score: {score} points | Solved: {solved}/{len(rounds)}")


if __name__ == "__main__":
    play_game()

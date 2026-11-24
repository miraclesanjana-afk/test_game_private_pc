"""Streamlit web UI for the Word Scramble game.

Run with:  streamlit run app.py
"""

from __future__ import annotations

from typing import Any, Dict

import streamlit as st

from game import ScrambleGame
from oxford_client import WordBank
from stats import Stats

st.set_page_config(page_title="Word Scramble", page_icon="D", layout="centered")

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
    }
    .block {
        background: rgba(30, 41, 59, 0.85);
        border-radius: 20px;
        padding: 32px;
        max-width: 680px;
        margin: 0 auto;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
    }
    .letters {
        font-family: 'Courier New', monospace;
        font-size: 3rem;
        letter-spacing: 0.5rem;
        font-weight: 800;
        color: #e2e8f0;
        background: #1e293b;
        padding: 28px 36px;
        border-radius: 16px;
        text-align: center;
        text-transform: uppercase;
        text-shadow: 0 0 25px #8b5cf6;
        margin: 24px auto;
        width: fit-content;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def load_word_bank() -> WordBank:
    return WordBank.load()


def load_stats() -> Stats:
    return Stats.load()


def init_state() -> None:
    if "game" not in st.session_state:
        st.session_state["game"] = ScrambleGame(load_word_bank())
    st.session_state.setdefault("message", None)
    st.session_state.setdefault("last_correct", False)
    st.session_state.setdefault("hint", None)


def reset_game(game: ScrambleGame) -> None:
    game.reset()
    st.session_state["message"] = None
    st.session_state["last_correct"] = False
    st.session_state["hint"] = None


def definition_of(game: ScrambleGame) -> str:
    current: Dict[str, Any] = game.current or {}
    return "; ".join(current.get("definitions") or []) or "No definition available."


def main() -> None:
    init_state()
    game = st.session_state["game"]

    with st.sidebar:
        st.title("Scramble Game")
        word_bank = load_word_bank()
        st.caption(f"Word bank: {len(word_bank)} words - source: {word_bank.source}")
        stats = load_stats()
        st.metric("Best score", stats.best_score)
        st.metric("Games played", stats.total_played)
        st.radio("Difficulty", ["Easy", "Medium", "Hard"], key="difficulty_sel", horizontal=True)
        st.slider("Rounds per game", 3, 15, 8, key="rounds_sel")
        if st.button("New Game", type="primary"):
            game.difficulty = st.session_state.get("difficulty_sel", "Medium").lower()
            game.rounds = int(st.session_state.get("rounds_sel", 8))
            reset_game(game)
        if st.button("Refresh word bank"):
            game.word_bank = WordBank.load(force_refresh=True)
            reset_game(game)

    st.markdown('<div class="block">', unsafe_allow_html=True)
    st.title("Word Scramble")
    st.caption("Rearrange the letters to find the Oxford-dictionary word.")

    if game.is_finished:
        stats = load_stats()
        stats.record(game.score, game.rounds)
        st.balloons()
        st.success(f"Game over! Final score: {game.score}")
        if st.button("Play Again", key="play-again"):
            reset_game(game)
    else:
        st.markdown(f'<div class="letters">{game.scrambled}</div>', unsafe_allow_html=True)
        st.caption(f"{len(game.scrambled)} letters - Round {game.round_no}/{game.rounds}")

        if st.button("Show definition hint", key="hint-btn"):
            st.session_state["hint"] = game.get_hint()
        if st.session_state.get("hint"):
            st.info(f"Hint: {st.session_state['hint']}")

        with st.form("guess_form"):
            guess = st.text_input("Your guess", key="guess").strip()
            if st.form_submit_button("Check", type="primary"):
                correct, message = game.submit_guess(guess)
                st.session_state["message"] = message
                st.session_state["last_correct"] = correct

        message = st.session_state.get("message")
        if st.session_state.get("last_correct"):
            st.success(message or "Correct!")
            with st.expander("Word definition"):
                st.write(definition_of(game))
                pos = (game.current or {}).get("part_of_speech")
                if pos:
                    st.write(f"_({pos})_")
            if game.is_finished:
                stats = load_stats()
                stats.record(game.score, game.rounds)
                st.balloons()
                st.success(f"Game over! Final score: {game.score}")
                if st.button("Play Again", key="play-again-2"):
                    reset_game(game)
            elif st.button("Next Round", key="next-round"):
                game.next_round()
                st.session_state["message"] = None
                st.session_state["last_correct"] = False
                st.session_state["hint"] = None
        elif message:
            st.error(message)

        st.metric("Score", game.score)

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()

import random

import streamlit as st

from main import (
    POINTS_PER_ANSWER,
    POINTS_WITH_HINT,
    ROUNDS_PER_GAME,
    WORD_BANK,
    scramble_word,
    show_hint,
)


def start_new_game():
    selected_words = random.sample(
        WORD_BANK, k=min(ROUNDS_PER_GAME, len(WORD_BANK))
    )
    st.session_state.rounds = [
        (word, category, scramble_word(word))
        for word, category in selected_words
    ]
    st.session_state.round_index = 0
    st.session_state.score = 0
    st.session_state.solved = 0
    st.session_state.hint_used = False
    st.session_state.hint_visible = False
    st.session_state.feedback = None


st.set_page_config(page_title="Word Scramble", page_icon="🔤")
st.title("🔤 Word Scramble")
st.write("Unscramble the word, earn points, and see how many you can solve!")

if "rounds" not in st.session_state:
    start_new_game()

if st.button("Start a new game"):
    start_new_game()
    st.rerun()

round_index = st.session_state.round_index
rounds = st.session_state.rounds

if round_index >= len(rounds):
    st.success("Game over!")
    st.metric("Final score", f"{st.session_state.score} points")
    st.write(f"You solved {st.session_state.solved} out of {len(rounds)} words.")
else:
    word, category, scrambled = rounds[round_index]
    score_column, round_column = st.columns(2)
    score_column.metric("Score", st.session_state.score)
    round_column.metric("Round", f"{round_index + 1} / {len(rounds)}")

    st.caption(f"Category: {category}")
    st.subheader(scrambled.upper())

    with st.form("answer_form", clear_on_submit=True):
        answer = st.text_input("Your answer", key="answer")
        submitted = st.form_submit_button("Check answer")

    if submitted:
        if answer.strip().casefold() == word:
            points = (
                POINTS_WITH_HINT
                if st.session_state.hint_used
                else POINTS_PER_ANSWER
            )
            st.session_state.score += points
            st.session_state.solved += 1
            st.session_state.round_index += 1
            st.session_state.hint_used = False
            st.session_state.hint_visible = False
            st.session_state.feedback = ("success", f"Correct! You earned {points} points.")
        else:
            st.session_state.feedback = (
                "error",
                "Not quite. Try again, use a hint, or skip this word.",
            )
        st.rerun()

    hint_column, skip_column = st.columns(2)
    if hint_column.button("Show hint", disabled=st.session_state.hint_used):
        st.session_state.hint_used = True
        st.session_state.hint_visible = True

    if skip_column.button("Skip word"):
        st.session_state.feedback = ("info", f"The word was **{word}**.")
        st.session_state.round_index += 1
        st.session_state.hint_used = False
        st.session_state.hint_visible = False
        st.rerun()

    if st.session_state.hint_visible and st.session_state.round_index == round_index:
        st.info(show_hint(word))

if st.session_state.feedback:
    feedback_type, message = st.session_state.feedback
    getattr(st, feedback_type)(message)
    st.session_state.feedback = None

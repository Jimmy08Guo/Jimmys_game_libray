import random
from collections import Counter
import streamlit as st

st.set_page_config(page_title="Jimmy's Game Library", page_icon="🎮", layout="centered")

GAMES = ["🏠 Home", "🪙 Coin Clicker", "🪙 Flip a Coin", "🎲 Throw a Die", "🔢 Guess My Number", "➖ Subtraction Game", "🎨 Mastermind", "🐂 Bulls and Cows"]
COLORS = "RGBYPO"


def new_bulls_secret():
    first = random.choice("123456789")
    return first + "".join(random.sample([x for x in "0123456789" if x != first], 3))


def reset_game(game):
    if game == "🪙 Coin Clicker":
        st.session_state.coins = 0
        st.session_state.click_power = 1
    elif game == "🔢 Guess My Number":
        st.session_state.guess_secret = random.randint(0, 100)
        st.session_state.guess_attempts = 0
        st.session_state.guess_message = ""
    elif game == "➖ Subtraction Game":
        st.session_state.subtract_total = random.randint(20, 50)
        st.session_state.subtract_message = ""
    elif game == "🎨 Mastermind":
        st.session_state.master_secret = "".join(random.choices(COLORS, k=4))
        st.session_state.master_history = []
        st.session_state.master_message = ""
    elif game == "🐂 Bulls and Cows":
        st.session_state.bulls_secret = new_bulls_secret()
        st.session_state.bulls_history = []
        st.session_state.bulls_message = ""


def mastermind_score(secret, guess):
    exact = sum(a == b for a, b in zip(secret, guess))
    total = sum((Counter(secret) & Counter(guess)).values())
    return exact, total - exact


def bulls_score(secret, guess):
    bulls = sum(a == b for a, b in zip(secret, guess))
    cows = len(set(secret) & set(guess)) - bulls
    return bulls, cows


for game in GAMES[1:]:
    marker = {
        "🪙 Coin Clicker": "coins", "🔢 Guess My Number": "guess_secret",
        "➖ Subtraction Game": "subtract_total", "🎨 Mastermind": "master_secret",
        "🐂 Bulls and Cows": "bulls_secret",
    }.get(game)
    if marker and marker not in st.session_state:
        reset_game(game)

st.title("🎮 Jimmy's Game Library")
st.caption("Interactive Python games built with Streamlit · Created by Jimmy")
choice = st.sidebar.radio("Choose a game", GAMES)

if choice == "🏠 Home":
    st.write("Welcome! Choose a game from the sidebar to start playing.")
    for game in GAMES[1:]:
        st.write(game)

elif choice == "🪙 Coin Clicker":
    st.header("🪙 Coin Clicker")
    st.write("Click to earn coins. Spend coins to increase your click power!")
    st.metric("Coins", st.session_state.coins)
    st.write(f"Power: **{st.session_state.click_power}** coins per click")
    left, right = st.columns(2)
    if left.button("Get coins", use_container_width=True):
        st.session_state.coins += st.session_state.click_power
        st.rerun()
    cost = st.session_state.click_power * 10
    if right.button(f"Upgrade ({cost} coins)", use_container_width=True):
        if st.session_state.coins >= cost:
            st.session_state.coins -= cost
            st.session_state.click_power += 1
            st.rerun()
        else:
            st.warning("Not enough coins yet!")
    if st.button("Reset coins"):
        reset_game(choice)
        st.rerun()

elif choice == "🪙 Flip a Coin":
    st.header("🪙 Flip a Coin")
    if st.button("Flip the coin"):
        st.session_state.flip_result = random.choice(["Heads!", "Tails!"])
    if "flip_result" in st.session_state:
        st.success(st.session_state.flip_result)

elif choice == "🎲 Throw a Die":
    st.header("🎲 Throw a Die")
    if st.button("Throw the die"):
        st.session_state.die_result = random.randint(1, 6)
    if "die_result" in st.session_state:
        st.success(f"You rolled {st.session_state.die_result}!")

elif choice == "🔢 Guess My Number":
    st.header("🔢 Guess My Number")
    st.write("I chose a number from 0 to 100. Can you find it?")
    st.write(f"Attempts: **{st.session_state.guess_attempts}**")
    with st.form("guess_form"):
        guess = st.number_input("Your guess", min_value=0, max_value=100, step=1)
        submitted = st.form_submit_button("Guess")
    if submitted:
        st.session_state.guess_attempts += 1
        secret = st.session_state.guess_secret
        if guess < secret:
            st.session_state.guess_message = "My number is greater than your guess."
        elif guess > secret:
            st.session_state.guess_message = "My number is less than your guess."
        else:
            st.session_state.guess_message = f"You got it in {st.session_state.guess_attempts} attempts! 🎉"
    if st.session_state.guess_message:
        st.info(st.session_state.guess_message)
    if st.button("New number"):
        reset_game(choice)
        st.rerun()

elif choice == "➖ Subtraction Game":
    st.header("➖ Subtraction Game")
    st.write("Subtract 1 to 5 each turn. Try to reach zero!")
    st.metric("Remaining total", st.session_state.subtract_total)
    if st.session_state.subtract_total == 0:
        st.success("Game over — you reached 0! 🎉")
    else:
        with st.form("subtract_form"):
            amount = st.selectbox("How much will you subtract?", list(range(1, 6)))
            submitted = st.form_submit_button("Subtract")
        if submitted:
            if amount > st.session_state.subtract_total:
                st.session_state.subtract_message = "You cannot subtract more than the remaining total."
            else:
                st.session_state.subtract_total -= amount
                st.session_state.subtract_message = f"You subtracted {amount}."
            st.rerun()
    if st.session_state.subtract_message:
        st.info(st.session_state.subtract_message)
    if st.button("New subtraction game"):
        reset_game(choice)
        st.rerun()

elif choice == "🎨 Mastermind":
    st.header("🎨 Mastermind")
    st.write("Guess a 4-letter color code using R, G, B, Y, P, O. Repeated colors are allowed. You have 10 attempts.")
    history = st.session_state.master_history
    won = bool(history and history[-1][1] == 4)
    finished = won or len(history) >= 10
    with st.form("master_form"):
        guess = st.text_input("Your color code", max_chars=4, placeholder="RGBY").upper().strip()
        submitted = st.form_submit_button("Check code", disabled=finished)
    if submitted:
        if len(guess) != 4 or any(c not in COLORS for c in guess):
            st.session_state.master_message = "Enter exactly four valid color letters (RGBYPO)."
        else:
            exact, misplaced = mastermind_score(st.session_state.master_secret, guess)
            st.session_state.master_history.append((guess, exact, misplaced))
            if exact == 4:
                st.session_state.master_message = "You solved the code! 🎉"
            elif len(st.session_state.master_history) == 10:
                st.session_state.master_message = f"No attempts left. The code was {st.session_state.master_secret}."
            else:
                st.session_state.master_message = "Keep trying!"
        st.rerun()
    if st.session_state.master_message:
        st.info(st.session_state.master_message)
    for number, (attempt, exact, misplaced) in enumerate(reversed(st.session_state.master_history), 1):
        st.write(f"**{attempt}** — exact: {exact}, wrong position: {misplaced}")
    if st.button("New Mastermind game"):
        reset_game(choice)
        st.rerun()

elif choice == "🐂 Bulls and Cows":
    st.header("🐂 Bulls and Cows")
    st.write("Guess a 4-digit number with no repeated digits. Bulls = correct digit and position. Cows = correct digit, wrong position.")
    history = st.session_state.bulls_history
    won = bool(history and history[-1][1] == 4)
    with st.form("bulls_form"):
        guess = st.text_input("Your 4-digit guess", max_chars=4, placeholder="1234").strip()
        submitted = st.form_submit_button("Check number", disabled=won)
    if submitted:
        if len(guess) != 4 or not guess.isdigit() or len(set(guess)) != 4:
            st.session_state.bulls_message = "Enter exactly four different digits."
        else:
            bulls, cows = bulls_score(st.session_state.bulls_secret, guess)
            st.session_state.bulls_history.append((guess, bulls, cows))
            st.session_state.bulls_message = (f"You won in {len(st.session_state.bulls_history)} attempts! 🎉" if bulls == 4 else "Keep trying!")
        st.rerun()
    if st.session_state.bulls_message:
        st.info(st.session_state.bulls_message)
    for attempt, bulls, cows in reversed(st.session_state.bulls_history):
        st.write(f"**{attempt}** — Bulls: {bulls}, Cows: {cows}")
    if st.button("New Bulls and Cows game"):
        reset_game(choice)
        st.rerun()

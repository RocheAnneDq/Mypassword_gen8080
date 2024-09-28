import random
import string
import streamlit as st
import os
import json

# Retrieve owner passcode from environment variable, or use a default for testing
OWNER_PASSCODE = os.getenv("OWNER_PASSCODE", "mypassword123")  # Update with your secure passcode

# File to store the password history
HISTORY_FILE = "password_history.json"

# Function to load password history from file
def load_password_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

# Function to save password history to file
def save_password_history():
    with open(HISTORY_FILE, "w") as f:
        json.dump(st.session_state.password_history, f)

# Initialize password history in session state from file if not already present
if 'password_history' not in st.session_state:
    st.session_state.password_history = load_password_history()

if 'show_history' not in st.session_state:
    st.session_state.show_history = False

if 'passcode_input' not in st.session_state:
    st.session_state.passcode_input = ""

def generate_password(word, total_length=8, enforce_rules=False, keep_phrase_intact=False):
    if total_length < len(word):
        raise ValueError(f"Total password length must be at least the length of the input word ({len(word)} characters).")

    lower_pool = string.ascii_lowercase
    upper_pool = string.ascii_uppercase
    digits_pool = string.digits
    special_pool = string.punctuation

    all_pools = lower_pool + upper_pool + digits_pool + special_pool
    remaining_length = total_length - len(word)

    if enforce_rules:
        required_elements = [
            random.choice(lower_pool),
            random.choice(upper_pool),
            random.choice(digits_pool),
            random.choice(special_pool)
        ]
        remaining_length -= len(required_elements)
        if remaining_length < 0:
            raise ValueError(f"Total length must be at least {len(word) + 4} to satisfy all rules.")
    else:
        required_elements = []

    random_characters = [random.choice(all_pools) for _ in range(remaining_length)]

    if keep_phrase_intact:
        password = word + ''.join(random_characters + required_elements)
    else:
        password = list(word + ''.join(random_characters + required_elements))
        random.shuffle(password)
        password = ''.join(password)

    return password

st.title("Password Generator App")

word = st.text_input("Enter a word or phrase to include in the password:")
total_length = st.number_input(f"Enter total desired password length (must be at least {len(word)}):", min_value=len(word), value=len(word)+4)
enforce_rules = st.checkbox("Enforce the 5 standard rules (lowercase, uppercase, digit, special character)")
keep_phrase_intact = st.checkbox("Keep the phrase intact (not shuffled in the password)")
account_name = st.text_input("Enter the account name for which this password is generated:")

if st.button("Generate Password"):
    try:
        password = generate_password(word, total_length, enforce_rules, keep_phrase_intact)
        st.success(f"Generated password: {password}")
        
        if account_name:
            st.session_state.password_history.append({"account": account_name, "password": password})
        else:
            st.session_state.password_history.append({"account": "No account specified", "password": password})

        # Save the updated password history to the file
        save_password_history()

    except ValueError as e:
        st.error(e)

# Display password history or passcode input
if st.session_state.show_history:
    if st.session_state.password_history:
        st.subheader("Password History:")
        for idx, entry in enumerate(st.session_state.password_history, 1):
            st.write(f"{idx}. Account: {entry['account']} | Password: {entry['password']}")
        if st.button("Close History"):
            st.session_state.show_history = False
            st.session_state.passcode_input = ""  # Clear the passcode field
    else:
        st.write("No passwords have been generated yet.")
else:
    passcode = st.text_input("Enter the owner passcode to view history:", type="password")

    if st.button("Access Password History"):
        if passcode == OWNER_PASSCODE:
            st.session_state.show_history = True
            st.session_state.passcode_input = ""  # Clear the passcode field
            st.success("Passcode correct. History will now be displayed.")
            st.success("Please click again the 'Access Password History' button.")
        else:
            st.error("Incorrect passcode! Access denied.")

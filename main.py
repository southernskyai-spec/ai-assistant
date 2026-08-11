# main.py - command-line chat with the assistant

import sys
from assistant import get_reply

# Windows terminals default to an older text encoding that can't display
# some characters the AI uses (em dashes, curly quotes, etc), turning them
# into "?" or garbage symbols. This switches output to UTF-8, which can.
sys.stdout.reconfigure(encoding="utf-8")

# This list holds the entire conversation so far. Without it, every message
# to the AI is standalone and it has no idea what was said earlier.
conversation = []

while True:
    user_input = input("You: ")

    if user_input.lower() == "quit":
        print("Assistant: Goodbye!")
        break

    reply = get_reply(conversation, user_input)
    print("Assistant:", reply)

# app.py - a simple web UI for the assistant, using Flask
#
# Flask is a Python framework for building web servers. Instead of your
# program running top-to-bottom once (like main.py), it stays running and
# waits, responding every time a browser asks it for something.

import os
import secrets
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from assistant import get_reply

load_dotenv()

app = Flask(__name__)
# Flask uses this key to cryptographically sign the session cookie it gives
# each visitor's browser, so it can trust the cookie wasn't tampered with.
# Without it, sessions (and our password gate) wouldn't work at all.
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

ASSISTANT_PASSWORD = os.environ.get("ASSISTANT_PASSWORD")

# Maps each visitor's session ID to THEIR OWN conversation history, so two
# different people using the site at the same time don't see each other's
# messages (fixing the single shared `conversation` list from before).
conversations = {}


def is_logged_in():
    return session.get("logged_in") is True


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # request.form reads fields submitted by an HTML <form>, same idea
        # as request.json but for regular form submissions instead of JSON.
        if request.form.get("password") == ASSISTANT_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("home"))
        return render_template("login.html", error="Wrong password")
    return render_template("login.html")


@app.route("/")
def home():
    if not is_logged_in():
        return redirect(url_for("login"))
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    if not is_logged_in():
        return jsonify({"error": "Not logged in"}), 401

    # Give this visitor's session a random ID the first time we see them,
    # then always use it to look up (or create) THEIR conversation history.
    if "id" not in session:
        session["id"] = secrets.token_hex(8)
    conversation = conversations.setdefault(session["id"], [])

    user_input = request.json["message"]
    reply = get_reply(conversation, user_input)
    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True)

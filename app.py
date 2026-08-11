# app.py - a simple web UI for the assistant, using Flask
#
# Flask is a Python framework for building web servers. Instead of your
# program running top-to-bottom once (like main.py), it stays running and
# waits, responding every time a browser asks it for something.

from flask import Flask, request, jsonify, render_template
from assistant import get_reply

app = Flask(__name__)

# One shared conversation, kept in memory on the server. This is fine for
# a single person using this locally - a real multi-user site would need
# a separate conversation per visitor instead of one global list.
conversation = []


# This decorator (@app.route) registers a URL: whenever a browser requests
# "/" (the homepage), Flask calls the function right below it and sends
# back whatever it returns.
@app.route("/")
def home():
    # Looks for templates/index.html and returns it as the page.
    return render_template("index.html")


# methods=["POST"] means this URL only responds to POST requests (sending
# data), not just a browser visiting a link - same POST concept from your
# earlier requests.post() lessons, just on the receiving end this time.
@app.route("/chat", methods=["POST"])
def chat():
    # request.json reads the JSON body the page's JavaScript sent us,
    # same shape as the dicts we've been building with requests.post().
    user_input = request.json["message"]
    reply = get_reply(conversation, user_input)
    # jsonify converts a Python dict into a JSON HTTP response.
    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True)

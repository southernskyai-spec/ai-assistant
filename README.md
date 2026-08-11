# AI Assistant

An AI assistant built in Python using the Anthropic (Claude) API, available both as a command-line chat and a web UI. Supports multi-turn conversation memory and real tool/function calling, so the AI can take real actions instead of only generating text.

## Features

- Persistent conversation history — the assistant remembers earlier turns in the same session
- Real tool/function calling, routed through a dispatch table so new tools are a one-line addition:
  - `get_weather(city)` — live weather via wttr.in (no API key required)
  - `save_note(note)` — appends a note/reminder to `notes.txt`
  - `add_task(task)` — stores structured to-do items (with a `done` flag) in `tasks.json`
- Two interfaces sharing the same AI logic (`assistant.py`): a CLI (`main.py`) and a web UI (`app.py`, built with Flask)
- Secrets kept out of source code via `.env` + `python-dotenv`
- Custom system prompt to set the assistant's persona

## Setup

1. Clone this repo and install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Create a `.env` file in the project root with your own Anthropic API key (get one at console.anthropic.com):
   ```
   ANTHROPIC_API_KEY=your-key-here
   ```

## Running it

**Command line:**
```
python main.py
```
Type `quit` to exit.

**Web UI:**
```
python app.py
```
Then open `http://127.0.0.1:5000` in your browser.

## Example

```
You: What's the weather like in Chicago right now?
Assistant: Right now in Chicago, it's 86°F and sunny.
```

## How tool calling works

The AI can't execute code itself. When it needs live data, it responds with a request to call a specific tool (e.g. `get_weather`, with `city="Chicago"`). The Python script executes that function for real, sends the result back to the API, and the AI incorporates the real result into its final answer. This request → pause → execute → resume pattern is the core mechanism behind AI agents and automation tools.

## Project structure

- `assistant.py` — the AI logic: tool definitions, dispatch table, and the conversation loop. Shared by both interfaces.
- `main.py` — command-line interface
- `app.py` + `templates/index.html` — web interface (Flask)

## Built with

Python, [Anthropic API](https://docs.anthropic.com/), Flask, `requests`, `python-dotenv`

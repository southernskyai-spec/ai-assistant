# AI Assistant (CLI)

A command-line AI assistant built in Python using the Anthropic (Claude) API. Supports multi-turn conversation memory and real tool/function calling, so the AI can take real actions (currently: check live weather) instead of only generating text.

## Features

- Persistent conversation history — the assistant remembers earlier turns in the same session
- Real tool/function calling — the AI can call `get_weather(city)` (via wttr.in, no API key required) and use the real result in its answer
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
3. Run it:
   ```
   python main.py
   ```
4. Type `quit` to exit.

## Example

```
You: What's the weather like in Chicago right now?
Assistant: Right now in Chicago, it's 86°F and sunny.
```

## How tool calling works

The AI can't execute code itself. When it needs live data, it responds with a request to call a specific tool (e.g. `get_weather`, with `city="Chicago"`). The Python script executes that function for real, sends the result back to the API, and the AI incorporates the real result into its final answer. This request → pause → execute → resume pattern is the core mechanism behind AI agents and automation tools.

## Built with

Python, [Anthropic API](https://docs.anthropic.com/), `requests`, `python-dotenv`

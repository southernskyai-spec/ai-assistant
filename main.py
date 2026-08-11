# main.py - our AI assistant

import os
import sys
import json
import requests
from dotenv import load_dotenv
import anthropic

# Windows terminals default to an older text encoding that can't display
# some characters the AI uses (em dashes, curly quotes, etc), turning them
# into "?" or garbage symbols. This switches output to UTF-8, which can.
sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = "You are a helpful, concise AI automation assistant."


def get_weather(city):
    """A real Python function the AI can trigger. Free API, no key needed."""
    response = requests.get(f"https://wttr.in/{city}?format=j1", timeout=5)
    current = response.json()["current_condition"][0]
    return f"{current['temp_F']}F and {current['weatherDesc'][0]['value']} in {city}"


def save_note(note):
    """A second real function - appends a note to notes.txt for later."""
    with open("notes.txt", "a", encoding="utf-8") as f:
        f.write(note + "\n")
    return f"Saved note: {note}"


TASKS_FILE = "tasks.json"


def add_task(task):
    """A third function - stores tasks as structured JSON instead of plain
    text, so each one can carry extra info (here, a done/not-done flag)
    that later code could update, unlike a plain line of text."""
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            tasks = json.load(f)   # turns the JSON file's text back into a Python list
    else:
        tasks = []

    tasks.append({"task": task, "done": False})

    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2)   # turns the Python list back into JSON text

    return f"Added task: {task}"


# This describes each function to the AI in a format it understands: a name,
# a description (how the AI decides WHEN to use it), and an input_schema
# (what arguments it must provide). The AI never runs these Python functions
# itself - it just tells us it wants to, with what arguments, and we're the
# ones who actually call them below.
tools = [
    {
        "name": "get_weather",
        "description": "Get the current real-world weather for a specific city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name, e.g. 'Austin' or 'Tokyo'"}
            },
            "required": ["city"]
        }
    },
    {
        "name": "save_note",
        "description": "Save a short note or reminder to a persistent notes file for later.",
        "input_schema": {
            "type": "object",
            "properties": {
                "note": {"type": "string", "description": "The note text to save"}
            },
            "required": ["note"]
        }
    },
    {
        "name": "add_task",
        "description": "Add a new to-do item to the persistent task list.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "The task description, e.g. 'follow up with recruiter'"}
            },
            "required": ["task"]
        }
    }
]

# A dispatch table: maps each tool's NAME (a string, matching "name" above)
# to the ACTUAL Python function that should run when the AI asks for it.
# This is what lets the tool-handling loop below call the right function
# for ANY tool by name, instead of hardcoding "if name == get_weather, else
# if name == save_note, else ..." - adding a third tool later just means
# adding one more entry here, nothing else changes.
TOOL_FUNCTIONS = {
    "get_weather": get_weather,
    "save_note": save_note,
    "add_task": add_task
}

# This list holds the entire conversation so far. Without it, every message
# to the API is standalone and the AI has no idea what was said earlier.
conversation = []


def ask_claude():
    """Sends the full conversation so far and returns Claude's response."""
    return client.messages.create(
        model="claude-sonnet-5",
        max_tokens=300,
        system=SYSTEM_PROMPT,
        tools=tools,
        messages=conversation
    )


while True:
    user_input = input("You: ")

    if user_input.lower() == "quit":
        print("Assistant: Goodbye!")
        break

    conversation.append({"role": "user", "content": user_input})
    response = ask_claude()

    # stop_reason tells us WHY the AI stopped generating. "tool_use" means
    # it didn't answer yet - it wants to call one of our tools first and
    # see the result before it can give a real answer. We loop because it
    # could even chain multiple tool calls before it's ready to reply.
    while response.stop_reason == "tool_use":
        # Record exactly what the AI sent (including its tool request) as
        # its turn in the conversation, so it stays consistent going forward.
        conversation.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                function = TOOL_FUNCTIONS[block.name]
                # block.input is a dict like {"city": "Chicago"} or
                # {"note": "buy milk"}. The ** unpacks it into matching
                # keyword arguments, e.g. function(city="Chicago") -
                # this works because our input_schema property names
                # (Piece 3) match each function's real parameter names.
                result = function(**block.input)
                # tool_use_id links our answer back to this specific request,
                # since the AI could technically ask for several tools at once.
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })

        # Tool results are sent back as a "user" turn - from the API's
        # perspective, this is us responding on the tool's behalf.
        conversation.append({"role": "user", "content": tool_results})
        response = ask_claude()

    reply = next(block.text for block in response.content if block.type == "text")
    print("Assistant:", reply)
    conversation.append({"role": "assistant", "content": reply})

# assistant.py - the AI logic itself, shared by both main.py (CLI)
# and app.py (web UI). Neither of those files talks to Claude directly -
# they both just call get_reply() from here.

import os
import json
import requests
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = "You are a helpful, concise AI automation assistant."


def get_weather(city):
    response = requests.get(f"https://wttr.in/{city}?format=j1", timeout=5)
    current = response.json()["current_condition"][0]
    return f"{current['temp_F']}F and {current['weatherDesc'][0]['value']} in {city}"


def save_note(note):
    with open("notes.txt", "a", encoding="utf-8") as f:
        f.write(note + "\n")
    return f"Saved note: {note}"


TASKS_FILE = "tasks.json"


def add_task(task):
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            tasks = json.load(f)
    else:
        tasks = []

    tasks.append({"task": task, "done": False})

    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2)

    return f"Added task: {task}"


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

TOOL_FUNCTIONS = {
    "get_weather": get_weather,
    "save_note": save_note,
    "add_task": add_task
}


def ask_claude(conversation):
    return client.messages.create(
        model="claude-sonnet-5",
        max_tokens=300,
        system=SYSTEM_PROMPT,
        tools=tools,
        messages=conversation
    )


def get_reply(conversation, user_input):
    """Sends user_input, runs any tool calls Claude asks for, and returns
    its final text reply. Appends every step to `conversation` in place,
    so whoever called this (CLI or web) sees the updated history too."""
    conversation.append({"role": "user", "content": user_input})
    response = ask_claude(conversation)

    while response.stop_reason == "tool_use":
        conversation.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                function = TOOL_FUNCTIONS[block.name]
                result = function(**block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })

        conversation.append({"role": "user", "content": tool_results})
        response = ask_claude(conversation)

    reply = next(block.text for block in response.content if block.type == "text")
    conversation.append({"role": "assistant", "content": reply})
    return reply

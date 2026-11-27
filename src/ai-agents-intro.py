"""
A simple AI agent from scratch (no framework)
==============================================

Agent = LLM (brain) + tools (hands) + memory (messages) + a loop.

The loop:
    1. Send the conversation + tool list to the LLM
    2. If the LLM asks for a tool -> run it, add the result to memory, go to 1
    3. If the LLM answers in plain text -> done
"""

import ast
import json
import operator
import os
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

MODEL = 'gpt-4o-mini'

MAX_STEPS = 8 #saftey limit so the agent can never loop forever



# 1.Tools Normal python function the agent can use 
_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.USub: operator.neg,
    ast.Mod: operator.mod,
}

def calculator(expression:str)-> str:
    """Safety evaluate basic math like '23 * 3 + 4'. No eval(), so code injection"""
    def _eval(node):
        if isinstance(node,ast.Constant) and isinstance(node.value,(int,float)):
            return node.value
        if isinstance(node,ast.BinOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](_eval(node.left),_eval(node.right))
        if isinstance(node,ast.UnaryOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](_eval(node.operand))
        raise ValueError("Only numbers and + - * / % ** are allowed")
    try:
        return str(_eval(ast.parse(expression,mode="eval").body))
    except Exception as e:
        return f"Error:{e}"


 # pretend weather API, so the demo works without another key
FAKE_WEATHER = { 
    "delhi": "28°C, hazy",
    "mumbai": "31°C, humid",
    "bangalore": "24°C, cloudy",
}

def get_weather(city:str) -> str:
    """Return the Fake current Wheatther for a city"""
    return FAKE_WEATHER.get(city.lower(),f"No Wheather data for a {city}")

def get_current_time()-> str:
    """Return today's date and the current time"""
    return datetime.now().strftime("%d %B %Y, %A, %I:%M %p")

TOOL_FUNCTIONS = {
    "calculator":calculator,
    "get_weather":get_weather,
    "get_current_time":get_current_time,
}

TOOLS = [
    {
        "type":"function",
        "function":{
            "name":"calculator",
            "description":"Evaluate a maths expression. use it for any arithmetic",
            "parameters":{
                "type":"object",
                "properties":{
                    "expression":{"type":"string","description":"e.g.'24*3'"}
                },
                "required":["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for an Indian city.",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        },
    },
    {
         "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get today's date, weekday and current time.",
            "parameters": {"type": "object", "properties": {}},
        },
    }
]

SYSTEM_PROMPT = "You are a helpful assistant agent. Use tools whenever they help: always use the calculator for arithmetic, never do maths in your head. When you have everything you need, give a short final answer."

# ---------------------------------------------------------------------------
# 2. THE AGENT LOOP
# ---------------------------------------------------------------------------

def run_agent(user_goal, client=None, verbose=True):
    if client is None:
        from openai import OpenAI
        client = OpenAI()

    # Memory: the whole conversation, sent every step (the API is stateless)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_goal},
    ]

    for step in range(1, MAX_STEPS + 1):
        # THINK: the LLM decides what to do next
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOLS, temperature=0
        )
        msg = response.choices[0].message

        # DONE: no tool requested -> this is the final answer
        if not msg.tool_calls:
            if verbose:
                print(f"\n[step {step}] Final answer")
            return msg.content

        # ACT: run every tool the LLM asked for
        messages.append(msg)
        for call in msg.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments or "{}")
            func = TOOL_FUNCTIONS.get(name)
            result = func(**args) if func else f"Error: unknown tool {name}"

            if verbose:
                print(f"[step {step}] Tool: {name}({args}) -> {result}")

            # OBSERVE: give the result back to the LLM
            messages.append(
                {"role": "tool", "tool_call_id": call.id, "content": str(result)}
            )

    return "Stopped: reached the step limit without a final answer."




if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        print("OPENAI_API_KEY is not set. Add it to your .env file and run again.")
        print("\nTools work without a key, try them:")
        print("  calculator('(20 + 4) * 3') ->", calculator("(20 + 4) * 3"))
        print("  get_weather('Delhi')        ->", get_weather("Delhi"))
        print("  get_current_time()          ->", get_current_time())
    else:
        goal = (
            "What day is it today? Also, what's the weather in Delhi and Mumbai, "
            "and what is the temperature difference between them?"
        )
        print("GOAL:", goal)
        print(run_agent(goal))

        print("\n" + "=" * 60)
        print("Your turn. Type a goal (or 'exit').")
        while True:
            goal = input("\nYou: ").strip()
            if goal.lower() in {"exit", "quit", ""}:
                break
            print("Agent:", run_agent(goal))






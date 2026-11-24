import json

from weather_agent.client import get_client_and_model
from weather_agent.prompts import build_system_prompt
from weather_agent.schemas import TOOLS_MENU
from weather_agent.tools import TOOLS_FUNCTION


def run_agent_turns(messages: list, max_turn: int = 10) -> str:
    """Run the tool loop. `messages` is the chat history (user/assistant only);
    the final answer is appended to it and returned."""
    client, model, _ = get_client_and_model()

    working = [
        {"role": "system", "content": build_system_prompt()},
        *messages,
    ]

    for _ in range(max_turn):
        response = client.chat.completions.create(
            model=model,
            messages=working,         
            tools=TOOLS_MENU,
        )
        message = response.choices[0].message

        # No tool calls → final answer
        if not message.tool_calls:
            answer = message.content or ""
            messages.append({"role": "assistant", "content": answer})
            return answer

        # Record the assistant's tool-call message exactly as the model sent it
        working.append(message.model_dump(exclude_none=True))

        # Run each tool and send its result back
        for call in message.tool_calls:
            name = call.function.name
            fn = TOOLS_FUNCTION.get(name)
            if fn is None:
                tool_result = {"error": f"Unknown tool: {name}"}
            else:
                try:
                    arguments = json.loads(call.function.arguments or "{}")
                    tool_result = fn(**arguments)
                except Exception as e:
                    tool_result = {"error": f"{type(e).__name__}: {e}"}

            working.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": tool_result if isinstance(tool_result, str)
                           else json.dumps(tool_result, default=str),
            })

    fallback = f"Stopped after hitting max_turn ({max_turn}) without a final answer."
    messages.append({"role": "assistant", "content": fallback})
    return fallback
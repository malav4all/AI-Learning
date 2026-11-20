import json
import os
from openai import OpenAI
from yahoo_finance_tools import get_stock_price
from dotenv import load_dotenv

load_dotenv() 

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  

TOOLS_DEFINITION = [{
    "type": "function",
    "function": {
        "name": "get_stock_price",
        "description": "Fetch the current price of a stock given its ticker symbol, e.g. AAPL, TSLA.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker_symbol": {"type": "string", "description": "Stock ticker symbol, e.g. AAPL"}
            },
            "required": ["ticker_symbol"],
        },
    },
}]

SYSTEM_PROMPT = (
    "You are a helpful stock market assistant. "
    "ALWAYS call the get_stock_price tool to get a price. Never guess or reuse prices from memory. "
    "If the user gives a company name, convert it to its ticker symbol first."
)

AVAILABLE_TOOLS = {"get_stock_price": get_stock_price}


def run_agent(user_query: str) -> None:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query},
    ]
    print("-" * 50, "\nUser Query:", user_query, "\n" + "-" * 50)

    while True:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS_DEFINITION,
            tool_choice="auto",
        )
        choice = response.choices[0]
        msg = choice.message
        messages.append(msg.model_dump(exclude_none=True))

        if not msg.tool_calls:  # final answer
            print("Assistant:", msg.content)
            break

        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments)
            print(f"Tool Call: {tc.function.name}({args})")
            fn = AVAILABLE_TOOLS.get(tc.function.name)
            try:
                result = fn(**args) if fn else {"error": f"unknown tool {tc.function.name}"}
            except Exception as e:
                result = {"error": str(e)}
            print("Tool Result:", result)
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(result, default=str), 
            })


def main():
    print("Stock Price Tool Agent is running...\n" + "-" * 50)
    while True:
        query = input("Ask about a stock (or 'exit'): ").strip()
        if not query or query.lower() == "exit":
            break
        run_agent(query)


if __name__ == "__main__":
    main()
lookup_weather_schema = {
    "type": "function",
    "function": {
        "name": "lookup_weather",
        "description": (
            "Look up the current live weather for a place using the Open-Meteo API. "
            "Use this whenever the user asks about the weather in a location, such as "
            "temperature, wind speed or sky condition. The location can be a city, "
            "country or any other place name."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The name of the location to look up weather for, e.g. 'New Delhi'.",
                }
            },
            "required": ["location"],
        },
    },
}

TOOLS_MENU = [lookup_weather_schema]


def tool_catalog() -> list[dict[str, str]]:
    return [
        {
            "name": schema["function"]["name"],
            "description": schema["function"]["description"],
        }
        for schema in TOOLS_MENU
    ]
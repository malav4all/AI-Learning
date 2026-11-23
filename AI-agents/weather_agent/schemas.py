lookup_weather_schema = {
    "type": "object",
    "function":{
        "name":"lookup_weather",
        "description":(
            "Lookup the current live weather for a place using Open-Meteo Api.",
            "Use this whenever the user asks for the  weather in a location,for wind speed,sky condition or temperature. The location can be a city, country or any other place name."
        ),
        "parameters":{
            "type":"object",
            "properties":{
                "location":{
                    "type":"string",
                    "description":"The name of the location to lookup weather for."   
                }
            },
            "required":["location"],
        }
    }
}

TOOLS_MENU = [lookup_weather_schema]
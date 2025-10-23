"""Tool calling examples for ullm."""

import json

import ullm


def get_weather(location: str) -> dict:
    """Mock function to get weather."""
    # In a real app, this would call a weather API
    return {"location": location, "temperature": 72, "condition": "sunny", "humidity": 65}


def search_web(query: str) -> dict:
    """Mock function to search the web."""
    # In a real app, this would call a search API
    return {"query": query, "results": ["Result 1", "Result 2", "Result 3"]}


# Example 1: Single tool
print("=== Example 1: Single Tool ===")

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "The city and state, e.g. San Francisco, CA"}
                },
                "required": ["location"],
            },
        },
    }
]

response = ullm.completion(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": "What's the weather like in San Francisco?"}],
    tools=tools,
    max_tokens=200,
)

message = response.choices[0].message
print(f"Assistant: {message.content}")

if message.tool_calls:
    for tool_call in message.tool_calls:
        print(f"\nTool called: {tool_call.function.name}")
        print(f"Arguments: {tool_call.function.arguments}")

        # Execute the tool
        if tool_call.function.name == "get_weather":
            args = json.loads(tool_call.function.arguments)
            result = get_weather(**args)
            print(f"Result: {result}")

# Example 2: Multiple tools
print("\n=== Example 2: Multiple Tools ===")

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {"location": {"type": "string"}},
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for information",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "The search query"}},
                "required": ["query"],
            },
        },
    },
]

response = ullm.completion(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": "Search for 'best restaurants in Paris'"}],
    tools=tools,
    max_tokens=200,
)

message = response.choices[0].message

if message.tool_calls:
    for tool_call in message.tool_calls:
        print(f"Tool called: {tool_call.function.name}")
        print(f"Arguments: {tool_call.function.arguments}")

        # Execute the appropriate tool
        args = json.loads(tool_call.function.arguments)
        if tool_call.function.name == "get_weather":
            result = get_weather(**args)
        elif tool_call.function.name == "search_web":
            result = search_web(**args)

        print(f"Result: {result}\n")

# Example 3: Tool choice control
print("=== Example 3: Tool Choice Control ===")

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather",
            "parameters": {"type": "object", "properties": {"location": {"type": "string"}}, "required": ["location"]},
        },
    }
]

# Force tool use
response = ullm.completion(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": "What's the temperature?"}],
    tools=tools,
    tool_choice="required",  # Force the model to use a tool
    max_tokens=200,
)

message = response.choices[0].message
if message.tool_calls:
    print(f"Tool was forced to be called: {message.tool_calls[0].function.name}")
else:
    print("No tool call (model may not have enough context)")

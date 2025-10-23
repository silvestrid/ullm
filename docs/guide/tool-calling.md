# Tool Calling

Use functions and tools with LLMs.

```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get weather",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string"}
            }
        }
    }
}]

response = ullm.completion(
    model="gpt-4o-mini",
    messages=[...],
    tools=tools
)
```

*(More details coming soon)*

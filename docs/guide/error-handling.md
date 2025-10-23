# Error Handling

Handle errors and configure retry logic.

```python
try:
    response = ullm.completion(model="gpt-4o-mini", messages=[...])
except ullm.AuthenticationError:
    print("Invalid API key")
except ullm.RateLimitError:
    print("Rate limited")
except ullm.APIError as e:
    print(f"Error: {e}")
```

*(More details coming soon)*

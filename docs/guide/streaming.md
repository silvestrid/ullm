# Streaming

Stream responses token-by-token.

## Basic Streaming

```python
for chunk in ullm.completion(
    model="gpt-4o-mini",
    messages=[...],
    stream=True
):
    print(chunk.choices[0].delta.content, end="")
```

## Async Streaming

```python
async for chunk in await ullm.acompletion(
    model="gpt-4o-mini",
    messages=[...],
    stream=True
):
    print(chunk.choices[0].delta.content, end="")
```

*(More details coming soon)*

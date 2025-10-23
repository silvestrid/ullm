# Working with Providers

ullm supports four LLM providers. Each has its own quirks and capabilities.

## OpenAI

```python
response = ullm.completion(
    model="openai/gpt-4o-mini",
    messages=[...]
)
```

## Anthropic

```python
response = ullm.completion(
    model="anthropic/claude-3-5-sonnet-20241022",
    messages=[...]
)
```

## Groq

```python
response = ullm.completion(
    model="groq/llama-3.1-70b-versatile",
    messages=[...]
)
```

## AWS Bedrock

Requires `pip install ullm[aws]`

```python
response = ullm.completion(
    model="bedrock/anthropic.claude-3-sonnet",
    messages=[...]
)
```

*(More details coming soon)*

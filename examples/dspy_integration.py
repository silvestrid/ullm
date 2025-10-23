"""Example of using ullm with DSPy as a drop-in replacement for litellm."""

# This example shows how ullm can replace litellm in DSPy
#
# In your DSPy code, you would typically do:
#   import litellm
#   response = litellm.completion(model="openai/gpt-4", messages=[...])
#
# With ullm, simply replace:
#   import ullm
#   response = ullm.completion(model="openai/gpt-4", messages=[...])
#
# The API is compatible!

import ullm

# Example: Basic completion (same as litellm)
print("=== DSPy-style Completion ===")

response = ullm.completion(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": "What is machine learning?"}],
    temperature=0.7,
    max_tokens=200,
    num_retries=3,
    retry_strategy="exponential_backoff_retry",
)

print(f"Response: {response.choices[0].message.content}")
print(f"Usage: {response.usage.total_tokens} tokens\n")

# Example: With caching parameter (for DSPy compatibility)
print("=== With Cache Parameter (DSPy compatibility) ===")

# DSPy passes cache parameter - ullm accepts it for compatibility
# but doesn't cache internally (DSPy handles caching)
response = ullm.completion(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}],
    cache={"no-cache": True, "no-store": True},  # Accepted but ignored
    max_tokens=50,
)

print(f"Response: {response.choices[0].message.content}\n")

# Example: Model name formats
print("=== Model Name Formats ===")

# Provider/model format (recommended)
response1 = ullm.completion(model="openai/gpt-4o-mini", messages=[{"role": "user", "content": "Hi"}], max_tokens=10)

# Just model name (auto-detects provider)
response2 = ullm.completion(model="gpt-4o-mini", messages=[{"role": "user", "content": "Hi"}], max_tokens=10)

print("Both formats work!")
print(f"Format 1: {response1.choices[0].message.content}")
print(f"Format 2: {response2.choices[0].message.content}\n")

# Example: Different model types (chat, text, responses)
print("=== Different Model Types ===")

# Chat completion (default)
response = ullm.completion(model="openai/gpt-4o-mini", messages=[{"role": "user", "content": "Test"}], max_tokens=10)
print(f"Chat: {response.choices[0].message.content}")

# Responses API format (OpenAI Responses API)
response = ullm.responses(
    model="openai/gpt-4o-mini", input=[{"role": "user", "content": [{"type": "text", "text": "Test"}]}], max_tokens=10
)
print(f"Responses: {response.choices[0].message.content}\n")

print("=== ullm is ready to replace litellm in DSPy! ===")
print("Benefits:")
print("- 100x smaller memory footprint (~2MB vs ~200MB)")
print("- 24x faster import time")
print("- Same API as litellm")
print("- Focused on core providers (OpenAI, Anthropic, Groq, Bedrock)")

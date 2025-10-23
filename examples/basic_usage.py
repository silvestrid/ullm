"""Basic usage examples for ullm."""

import ullm

# Example 1: Simple completion
print("=== Example 1: Simple Completion ===")
response = ullm.completion(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": "What is the capital of France?"}],
    max_tokens=50,
)
print(f"Response: {response.choices[0].message.content}")
print(f"Tokens used: {response.usage.total_tokens}\n")

# Example 2: Different providers
print("=== Example 2: Different Providers ===")

# OpenAI
response = ullm.completion(
    model="openai/gpt-4o-mini", messages=[{"role": "user", "content": "Say hello in French"}], max_tokens=20
)
print(f"OpenAI: {response.choices[0].message.content}")

# Anthropic (requires ANTHROPIC_API_KEY)
# response = ullm.completion(
#     model="anthropic/claude-3-5-haiku-20241022",
#     messages=[{"role": "user", "content": "Say hello in French"}],
#     max_tokens=20
# )
# print(f"Anthropic: {response.choices[0].message.content}")

# Groq (requires GROQ_API_KEY)
# response = ullm.completion(
#     model="groq/llama-3.1-8b-instant",
#     messages=[{"role": "user", "content": "Say hello in French"}],
#     max_tokens=20
# )
# print(f"Groq: {response.choices[0].message.content}")

# Example 3: Streaming
print("\n=== Example 3: Streaming ===")
response = ullm.completion(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": "Write a haiku about coding"}],
    stream=True,
    max_tokens=100,
)

print("Streaming response: ", end="")
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
print("\n")

# Example 4: Temperature control
print("=== Example 4: Temperature Control ===")

# Creative (high temperature)
response = ullm.completion(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": "Complete this: Once upon a time"}],
    temperature=1.5,
    max_tokens=50,
)
print(f"Creative (temp=1.5): {response.choices[0].message.content}")

# Focused (low temperature)
response = ullm.completion(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": "What is 2+2?"}],
    temperature=0.1,
    max_tokens=20,
)
print(f"Focused (temp=0.1): {response.choices[0].message.content}")

# Example 5: System messages
print("\n=== Example 5: System Messages ===")
response = ullm.completion(
    model="openai/gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a pirate. Always respond like a pirate."},
        {"role": "user", "content": "What's the weather like?"},
    ],
    max_tokens=100,
)
print(f"Response: {response.choices[0].message.content}")

# Example 6: Auto provider detection
print("\n=== Example 6: Auto Provider Detection ===")
# You can omit the provider prefix for common models
response = ullm.completion(
    model="gpt-4o-mini",  # Automatically detected as OpenAI
    messages=[{"role": "user", "content": "Hello!"}],
    max_tokens=20,
)
print(f"Response: {response.choices[0].message.content}")

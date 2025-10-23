"""Async usage examples for ullm."""

import asyncio

import ullm


async def main():
    # Example 1: Basic async completion
    print("=== Example 1: Async Completion ===")
    response = await ullm.acompletion(
        model="openai/gpt-4o-mini", messages=[{"role": "user", "content": "What is async programming?"}], max_tokens=100
    )
    print(f"Response: {response.choices[0].message.content}\n")

    # Example 2: Multiple concurrent requests
    print("=== Example 2: Concurrent Requests ===")
    questions = [
        "What is the capital of France?",
        "What is the capital of Germany?",
        "What is the capital of Italy?",
    ]

    tasks = [
        ullm.acompletion(model="openai/gpt-4o-mini", messages=[{"role": "user", "content": q}], max_tokens=20)
        for q in questions
    ]

    responses = await asyncio.gather(*tasks)

    for question, response in zip(questions, responses):
        print(f"Q: {question}")
        print(f"A: {response.choices[0].message.content}\n")

    # Example 3: Async streaming
    print("=== Example 3: Async Streaming ===")
    response = await ullm.acompletion(
        model="openai/gpt-4o-mini",
        messages=[{"role": "user", "content": "Count from 1 to 5"}],
        stream=True,
        max_tokens=50,
    )

    print("Streaming: ", end="")
    async for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            print(content, end="", flush=True)
    print("\n")

    # Example 4: Error handling
    print("=== Example 4: Error Handling ===")
    try:
        response = await ullm.acompletion(
            model="openai/gpt-4", messages=[{"role": "user", "content": "Hello"}], api_key="invalid", max_tokens=10
        )
    except ullm.AuthenticationError as e:
        print(f"Authentication failed: {e.message}")
    except ullm.UllmException as e:
        print(f"API error: {e.message}")


if __name__ == "__main__":
    asyncio.run(main())

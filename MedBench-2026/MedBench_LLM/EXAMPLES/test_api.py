#!/usr/bin/env python3
"""
Quick test script to verify POE API connection
"""

import openai
import os
import sys


def test_poe_api(api_key: str, model: str = "claude-sonnet-4.5"):
    """Test POE API connection with a simple query"""

    print(f"Testing POE API connection...")
    print(f"Model: {model}")
    print("-" * 60)

    try:
        client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.poe.com/v1",
        )

        # Simple test query
        test_question = "Hello! Please confirm you can respond. What is 2+2?"

        print(f"\nSending test query: {test_question}")

        chat = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": test_question}]
        )

        response = chat.choices[0].message.content

        print(f"\n✓ Success! API is working.")
        print(f"\nResponse from {model}:")
        print("-" * 60)
        print(response)
        print("-" * 60)

        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nPlease check:")
        print("1. Your API key is correct")
        print("2. Your API key has sufficient credits")
        print("3. You have internet connection")
        print("4. The model name is correct")
        return False


def main():
    # Get API key
    api_key = os.getenv("POE_API_KEY")

    if len(sys.argv) > 1:
        api_key = sys.argv[1]

    if not api_key:
        print("Error: No API key provided!")
        print("\nUsage:")
        print("  python test_api.py YOUR_API_KEY")
        print("  OR set POE_API_KEY environment variable")
        print("\nExample:")
        print("  export POE_API_KEY='your-key-here'")
        print("  python test_api.py")
        sys.exit(1)

    # Test with different models (optional)
    models = ["claude-sonnet-4.5"]  # Add more models if needed: "gpt-5.1", "gemini-3-pro"

    for model in models:
        success = test_poe_api(api_key, model)
        if not success:
            sys.exit(1)
        print("\n")

    print("All tests passed! You're ready to submit answers.")


if __name__ == "__main__":
    main()

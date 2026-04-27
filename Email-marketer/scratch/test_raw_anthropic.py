import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

def test_raw_anthropic():
    client = anthropic.Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )
    print(f"Testing with model: {os.getenv('ANTHROPIC_MODEL')}")
    try:
        message = client.messages.create(
            model=os.getenv("ANTHROPIC_MODEL"),
            max_tokens=1024,
            messages=[
                {"role": "user", "content": "Hello, Claude"}
            ]
        )
        print(f"Response: {message.content[0].text}")
    except Exception as e:
        print(f"Raw anthropic error: {e}")

if __name__ == "__main__":
    test_raw_anthropic()

import asyncio
import os
from dotenv import load_dotenv

# Mock settings since we want to test with current environment
load_dotenv()

from app.services.ai_service import AIService

async def test_ai():
    service = AIService()
    print(f"Service using model: {service.llm.model}")
    print(f"Service using key (partially): {str(service.llm.anthropic_api_key.get_secret_value())[:15]}...")
    try:
        content = await service.generate_email_content("Hello, this is a test.")
        print(f"Result: {content}")
    except Exception as e:
        print(f"Caught exception in test script: {e}")

if __name__ == "__main__":
    asyncio.run(test_ai())

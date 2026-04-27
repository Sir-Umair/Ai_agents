import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

def list_anthropic_models():
    client = anthropic.Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )
    print("Listing available models...")
    try:
        # Some versions of the library have .models.list()
        if hasattr(client, 'models'):
            models = client.models.list()
            for model in models.data:
                print(f"- {model.id}")
        else:
            print("Client does not have 'models' attribute. Trying legacy names...")
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    list_anthropic_models()

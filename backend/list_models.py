import google.generativeai as genai
from app.core.config import settings

def list_available_models():
    """
    Lists the available models for the configured Google API key.
    """
    try:
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        print("Available models:")
        for model in genai.list_models():
            print(f"- {model.name}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    list_available_models()

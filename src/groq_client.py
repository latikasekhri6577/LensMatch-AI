import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

def get_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set. Please add it to your .env file.")
    return Groq(api_key=api_key)

def get_model_name():
    return os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
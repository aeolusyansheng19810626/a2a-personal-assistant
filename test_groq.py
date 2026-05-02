from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GROQ_API_KEY')
print(f'API Key found: {api_key[:20]}...' if api_key else 'API Key not found')

try:
    client = Groq(api_key=api_key)
    print('[OK] Groq client created successfully')
except Exception as e:
    print(f'[ERROR] Error creating Groq client: {e}')

# Made with Bob

import os
import requests
from dotenv import load_dotenv

load_dotenv()

gemini_key = os.getenv('GEMINI_API_KEY')

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={gemini_key}"
response = requests.get(url)
models = response.json()
if 'models' in models:
    for m in models['models']:
        print(m['name'])
else:
    print(models)

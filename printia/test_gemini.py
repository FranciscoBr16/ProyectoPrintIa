import os
import requests
from dotenv import load_dotenv

load_dotenv()

gemini_key = os.getenv('GEMINI_API_KEY')

url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
headers = {"Content-Type": "application/json"}
params = {"key": gemini_key}

payload = {
    "systemInstruction": {
        "parts": [{"text": "You are a 3D printing expert."}]
    },
    "contents": [
        {
            "role": "user",
            "parts": [
                {
                    "text": "Analiza visualmente este modelo 3D y dame recomendaciones técnicas detalladas para imprimirlo en FDM."
                }
            ]
        }
    ],
    "generationConfig": {
        "temperature": 0.4,
        "maxOutputTokens": 1500,
        "topP": 0.9
    }
}

try:
    response = requests.post(url, headers=headers, params=params, json=payload, timeout=45)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        texto_generado = (
            data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
                .strip()
        )
        print("Generated Text:", texto_generado)
except Exception as e:
    print(e)

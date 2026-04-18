import os
import requests
from dotenv import load_dotenv

load_dotenv()
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
ELEVEN_VOICE_ID = os.getenv("ELEVEN_VOICE_ID")
text = "Testing eleven labs"

print(f"Key: {ELEVEN_API_KEY[:5]}... Voice: {ELEVEN_VOICE_ID}")

url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_VOICE_ID}"
headers = {"xi-api-key": ELEVEN_API_KEY, "Content-Type": "application/json"}
data = {"text": text, "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}}

response = requests.post(url, headers=headers, json=data)
print(response.status_code)
if response.status_code != 200:
    print(response.json())

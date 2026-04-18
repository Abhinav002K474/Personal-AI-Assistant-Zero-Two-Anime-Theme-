import requests, os
from dotenv import load_dotenv
load_dotenv()
url = 'https://api.elevenlabs.io/v1/voices'
headers = {'xi-api-key': os.getenv('ELEVEN_API_KEY')}
res = requests.get(url, headers=headers)
print(res.status_code)
if res.status_code == 200:
    for v in res.json().get('voices', []):
        print(f"{v.get('name')}: {v.get('voice_id')}")
else:
    print(res.json())

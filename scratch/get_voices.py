import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_keys = os.getenv("ELEVENLABS_API_KEYS", "").split(',')
if not api_keys or not api_keys[0]:
    api_keys = [os.getenv("ELEVENLABS_API_KEY")]

key = api_keys[0].strip()

url = "https://api.elevenlabs.io/v1/voices"
headers = {"xi-api-key": key}
response = requests.get(url, headers=headers)

if response.status_code == 200:
    voices = response.json().get('voices', [])
    for v in voices:
        print(f"Name: {v.get('name')}, ID: {v.get('voice_id')}, Labels: {v.get('labels')}")
else:
    print("Error fetching voices:", response.text)

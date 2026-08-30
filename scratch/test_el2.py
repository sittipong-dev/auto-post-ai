import os
import requests
import sys
from dotenv import load_dotenv
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

load_dotenv()
api_keys_str = os.getenv("ELEVENLABS_API_KEYS") or os.getenv("ELEVENLABS_API_KEY")
api_keys = [k.strip(" '\"") for k in api_keys_str.split(',')]
key = api_keys[0]

voices = {
    "Alice": "Xb7hH8MSUJpSbSDYk0k2",
    "Brian": "nPczCjzI2devNBz1zQrb"
}

text = "สวัสดีครับ ทดสอบระบบเสียงพากย์ภาษาไทย"

for name, voice_id in voices.items():
    print(f"Testing {name} (ID: {voice_id})...")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        output_file = f"scratch/test_{name}.mp3"
        with open(output_file, 'wb') as f:
            f.write(response.content)
        print(f"Success! {name} works perfectly.")
    else:
        print(f"Failed! Status Code: {response.status_code}")
        print(f"Response: {response.text}")

import os, requests
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("ELEVENLABS_API_KEY").strip(" '\"").encode('ascii', 'ignore').decode('ascii')
res = requests.get("https://api.elevenlabs.io/v1/models", headers={"xi-api-key": api_key})
for m in res.json():
    if m['model_id'] in ['eleven_multilingual_v2', 'eleven_turbo_v2_5']:
        print(f"--- {m['model_id']} ---")
        languages = m.get('languages', [])
        for lang in languages:
            print(lang.get('name'))

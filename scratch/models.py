import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("ELEVENLABS_API_KEY").strip(" '\"").encode('ascii', 'ignore').decode('ascii')
url = "https://api.elevenlabs.io/v1/models"
headers = {"xi-api-key": api_key}

res = requests.get(url, headers=headers)
for m in res.json():
    print(m['model_id'], m['name'])

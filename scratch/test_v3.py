import os, requests, json
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("ELEVENLABS_API_KEY").strip(" '\"").encode('ascii', 'ignore').decode('ascii')
url = "https://api.elevenlabs.io/v1/text-to-speech/Xb7hH8MSUJpSbSDYk0k2"
headers = {"Content-Type": "application/json", "xi-api-key": api_key}
data = {"text": "สวัสดีค่ะ ทดสอบเสียงภาษาไทยด้วยระบบใหม่ล่าสุด", "model_id": "eleven_multilingual_v2"}
# Let's try eleven_v3
data["model_id"] = "eleven_v3"
payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
res = requests.post(url, data=payload, headers=headers)
print(res.status_code)
if res.status_code == 200:
    print("Success V3!")
else:
    print(res.text)

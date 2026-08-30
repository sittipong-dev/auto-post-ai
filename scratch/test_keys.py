import os, sys, requests
from dotenv import load_dotenv

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

load_dotenv()
api_keys_str = os.getenv("ELEVENLABS_API_KEYS") or os.getenv("ELEVENLABS_API_KEY")

if not api_keys_str:
    print("ไม่พบ ELEVENLABS_API_KEYS ในไฟล์ .env")
    exit(1)

raw_keys = api_keys_str.split(',')
api_keys = [k.strip(" '\"").encode('ascii', 'ignore').decode('ascii') for k in raw_keys if k.strip()]

print(f"พบกุญแจทั้งหมด {len(api_keys)} ดอกใน .env\n")

for i, key in enumerate(api_keys, 1):
    url = "https://api.elevenlabs.io/v1/user/subscription"
    headers = {"xi-api-key": key}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            data = res.json()
            used = data.get("character_count", 0)
            total = data.get("character_limit", 10000)
            remaining = total - used
            print(f"ดอกที่ {i}: ใช้งานได้! (โควต้าคงเหลือ: {remaining:,} / {total:,} ตัวอักษร)")
        elif res.status_code == 401:
            print(f"ดอกที่ {i}: ใช้งานไม่ได้ (Error 401: กุญแจผิด หรือ ถูกระงับ)")
        else:
            print(f"ดอกที่ {i}: เกิดข้อผิดพลาด {res.status_code}")
    except Exception as e:
        print(f"ดอกที่ {i}: เชื่อมต่อไม่สำเร็จ ({e})")

import os
import requests
from dotenv import load_dotenv

def generate_voice_elevenlabs(text, output_path, voice_id="21m00Tcm4TlvDq8ikWAM"):
    """
    สร้างเสียงพากย์ด้วย ElevenLabs API
    """
    load_dotenv()
    
    # ดึงคีย์แบบหลายอัน (พวงกุญแจ) หรือแบบอันเดียวเผื่อไว้
    api_keys_str = os.getenv("ELEVENLABS_API_KEYS") or os.getenv("ELEVENLABS_API_KEY")
    if not api_keys_str:
        print("❌ ข้อผิดพลาด: ไม่พบ ELEVENLABS_API_KEYS ในไฟล์ .env")
        print("กรุณาเพิ่ม ELEVENLABS_API_KEYS=รหัส1,รหัส2,... ในไฟล์ .env")
        return False
        
    # แยกคีย์ด้วยลูกน้ำ ลบช่องว่าง และกรองเฉพาะ ASCII
    raw_keys = api_keys_str.split(',')
    api_keys = []
    for k in raw_keys:
        clean_k = k.strip(" '\"").encode('ascii', 'ignore').decode('ascii')
        if clean_k:
            api_keys.append(clean_k)
            
    if not api_keys:
        print("❌ ข้อผิดพลาด: ไม่มีกุญแจที่ใช้งานได้เลย")
        return False

    print(f"🎙️ กำลังเตรียมพากย์เสียง ElevenLabs (Voice ID: {voice_id})")
    print(f"🔑 พบกุญแจในพวงทั้งหมด {len(api_keys)} ดอก")
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    import json
    data = {
        "text": text,
        "model_id": "eleven_v3",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    # แปลงเป็น JSON แบบบังคับให้เป็นภาษาไทย (UTF-8)
    payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
    
    for i, api_key in enumerate(api_keys, 1):
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json; charset=utf-8",
            "xi-api-key": api_key
        }
        
        print(f"⏳ กำลังลองไขด้วยกุญแจดอกที่ {i}...")
        try:
            response = requests.post(url, data=payload, headers=headers)
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                print(f"✅ ดาวน์โหลดเสียงจาก ElevenLabs สำเร็จ (ด้วยกุญแจดอกที่ {i})!")
                return True
            elif response.status_code == 401:
                print(f"⚠️ กุญแจดอกที่ {i} โควต้าเต็มหรือใช้งานไม่ได้! กำลังสลับไปดอกถัดไป...")
                continue
            else:
                print(f"❌ ElevenLabs API Error ({response.status_code}) ด้วยกุญแจดอกที่ {i}: {response.text}")
                continue
        except Exception as e:
            print(f"❌ ข้อผิดพลาดในการเชื่อมต่อด้วยกุญแจดอกที่ {i}: {str(e)}")
            continue

    print("❌ ล้มเหลว: ใช้กุญแจจนหมดพวงแล้ว แต่ก็ยังสร้างเสียงพากย์ไม่ได้ (โควต้าน่าจะเต็มหมดครับ)")
    return False

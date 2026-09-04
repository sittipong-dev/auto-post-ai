import os
import sys
import time
import subprocess
from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

# แก้ปัญหาการพิมพ์ภาษาไทยใน Windows CMD (CP874)
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# โหลด API Key จากไฟล์ .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("Error: ไม่พบ GEMINI_API_KEY ในไฟล์ .env")
    sys.exit(1)

genai.configure(api_key=GEMINI_API_KEY)

def generate_script(product_name, price, tone="ตื่นเต้น ป้ายยา", voice_gender="female", max_retries=3):
    """ส่งข้อมูลให้ Gemini คิดสคริปต์พูด 15 วินาที พร้อมปรับอารมณ์ตามที่เลือก"""
    model = genai.GenerativeModel('gemini-3.5-flash-lite')
    
    gender_word = "ผู้ชาย (ต้องลงท้ายด้วย ครับ/นะครับ เสมอ)" if voice_gender == "male" else "ผู้หญิง (ต้องลงท้ายด้วย ค่ะ/นะคะ เสมอ)"
    
    prompt = f"""
    คุณคือนักป้ายยาบน TikTok และ Facebook Reels ที่พูดเป็นธรรมชาติ
    คุณกำลังสวมบทบาทเป็น: {gender_word}
    
    สินค้าที่เราจะป้ายยาคือ: {product_name}
    ราคาประมาณ: {price} บาท
    
    น้ำเสียง/คำพูด: {tone}
    
    เขียนสคริปต์คำพูดสำหรับพากย์เสียงวิดีโอ (ความยาวประมาณ 10-15 วินาที)
    กติกา:
    1. ภาษาพูดเป็นธรรมชาติ สอดคล้องกับน้ำเสียงที่กำหนด
    2. มีประโยค Hook เปิดคลิปดึงดูดใจใน 3 วินาทีแรก
    3. 🌟 สำคัญมาก: เนื่องจากระบบพากย์เสียงอ่านตัวเลขและภาษาอังกฤษไม่ออก คุณต้องแปลง "ตัวเลข" และ "ภาษาอังกฤษ" ทั้งหมดเป็น "คำอ่านภาษาไทย" (เช่น 45W เขียนเป็น สี่สิบห้าวัตต์, 199 บาท เขียนเป็น หนึ่งร้อยเก้าสิบเก้าบาท, iPhone เขียนเป็น ไอโฟน)
    4. ห้ามมีวงเล็บ (เช่น [ยิ้ม], [หัวเราะ]) เพราะระบบจะพากย์ออกเสียงวงเล็บด้วย
    5. พิมพ์อีโมจิได้ตามปกติ (ระบบพากย์เสียงจะถูกตั้งค่าให้ข้ามอีโมจิเอง)
    6. 🌟 สำคัญมาก: เนื่องจากคุณเป็น {gender_word} ให้จบประโยคสุดท้ายด้วยคำลงท้ายของคุณเสมอ ห้ามจบห้วนๆ เด็ดขาด (เช่น ห้ามจบด้วยคำว่า "ตะกร้า") เพื่อป้องกันระบบพากย์เสียงลากเสียงยาวผิดปกติ
    7. 🌟 สำคัญมาก: สำหรับคำทับศัพท์ภาษาอังกฤษ ให้สะกดเป็นคำอ่านภาษาไทยแบบตรงมาตราตัวสะกดที่สุด (เช่น ห้ามเขียน ปิคนิค ให้เขียน "ปิกนิก", ห้ามเขียน สมาร์ท ให้เขียน "สมาต", ห้ามเขียน อิเล็กทรอนิกส์ ให้เขียน "อิเล็กทรอนิก") เพื่อให้ระบบพากย์เสียงอ่านได้ถูกต้อง
    
    สคริปต์ของคุณ:
    """
    
    # ระบบ Exponential Backoff
    for attempt in range(max_retries):
        try:
            print(f"กำลังเรียกสมองกล Gemini (ความพยายามครั้งที่ {attempt+1}/{max_retries})...")
            # ปิด Safety Filters ทั้งหมด
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
            response = model.generate_content(prompt, safety_settings=safety_settings)
            
            if response.parts:
                return response.text.strip()
            else:
                print(f"⚠️ AI ปฏิเสธการตอบคำถาม (Finish Reason: {response.candidates[0].finish_reason})")
                return None
        except ResourceExhausted:
            wait_time = (attempt + 1) * 30
            print(f"⚠️ ติด Rate Limit, พักหายใจ {wait_time} วินาทีแล้วลองใหม่...")
            time.sleep(wait_time)
        except Exception as e:
            print(f"❌ Gemini Error: {e}")
            break
            
    return None

def generate_voice(text, output_path, voice_gender="female"):
    """แปลงข้อความเป็นเสียงพากย์ด้วย Edge-TTS พร้อมเลือกเสียงเพศชาย/หญิง"""
    voice_name = "คุณเปรมวดี (หญิง)" if voice_gender == "female" else "คุณนิวัฒน์ (ชาย)"
    print(f"กำลังให้ Edge-TTS สร้างเสียงพากย์ภาษาไทย ด้วยเสียง {voice_name}...")
    try:
        # เลือกเสียงตามที่ผู้ใช้กำหนด
        voice = "th-TH-PremwadeeNeural" if voice_gender == "female" else "th-TH-NiwatNeural"
        
        temp_txt = output_path + ".txt"
        with open(temp_txt, "w", encoding="utf-8") as f:
            f.write(text)
            
        command = [
            "edge-tts",
            "--voice", voice,
            "--file", temp_txt,
            "--write-media", output_path
        ]
        
        # ใช้ subprocess เรียก CLI (เอา PIPE ออกเพื่อกันโปรแกรมค้าง)
        subprocess.run(command, check=True)
        
        # ลบไฟล์ temp ทิ้งเมื่อเสร็จ
        if os.path.exists(temp_txt):
            os.remove(temp_txt)
            
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ TTS Error: เกิดข้อผิดพลาดในการสร้างเสียงพากย์ (No Audio Received)")
        return False
    except FileNotFoundError:
        print("❌ ไม่พบคำสั่ง edge-tts (ยังไม่ได้ติดตั้ง?)")
        return False

if __name__ == "__main__":
    # ทดสอบกับสินค้า HOCO Powerbank (รหัส: 26962408187) ที่เราดูดรูปมาเมื่อกี้
    product_id = "26962408187"
    product_name = "พาวเวอร์แบงก์ แบตสำรอง HOCO A10 B10 E10 Power Bank 10000mAh 20000mAh 30000mAh มีสายชาร์จในตัว"
    price = "389"
    
    save_dir = os.path.join("assets", "products", product_id)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    script_path = os.path.join(save_dir, "script.txt")
    audio_path = os.path.join(save_dir, "voice.mp3")
    
    print("--- 🧠 เริ่มกระบวนการ AI Brain & TTS ---")
    script = generate_script(product_name, price)
    
    if script:
        print("\n====================")
        print("🎤 สคริปต์ที่ AI แต่งให้:")
        print(script)
        print("====================\n")
        
        # เซฟสคริปต์เก็บไว้เป็น Text File
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script)
            
        # สร้างเสียงพากย์
        success = generate_voice(script, audio_path)
        if success:
            print(f"Success: สร้างไฟล์เสียง MP3 สำเร็จ! 🎵")
            print(f"ไฟล์ถูกจัดเก็บอยู่ที่: {audio_path}")
        else:
            print("Failed: สร้างเสียงพากย์ไม่สำเร็จ")
    else:
        print("Failed: สร้างสคริปต์ไม่สำเร็จ")

import json

def generate_broll_script(topic, tone="สารคดีให้ความรู้", voice_gender="female", max_retries=3):
    """สร้างสคริปต์แบบแบ่งฉากสำหรับ Auto B-Roll"""
    # [เซฟโควต้า]
    script_file = os.path.join("data", "review_script.txt")
    if os.path.exists(script_file):
        print("\n♻️ [เซฟโควต้า] นำสคริปต์เดิมมาใช้...")
        scenes_data = []
        current_scene = {}
        with open(script_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("--- ฉากที่"):
                    if current_scene: scenes_data.append(current_scene)
                    current_scene = {"scene_number": len(scenes_data) + 1}
                elif line.startswith("[คำค้นหาภาพ (ไทย)]"): current_scene["search_keyword_th"] = line.split(":", 1)[1].strip()
                elif line.startswith("[Search Keyword (ENG)]"): current_scene["search_keyword_en"] = line.split(":", 1)[1].strip()
                elif line.startswith("[บทพูด]:"): current_scene["text"] = line.replace("[บทพูด]:", "").strip()
        if current_scene: scenes_data.append(current_scene)
        if scenes_data: return scenes_data

    model = genai.GenerativeModel('gemini-3.7-flash')
    
    gender_word = "ค่ะ/นะคะ" if voice_gender == "female" else "ครับ/นะครับ"
    
    prompt = f"""
คุณคือผู้กำกับวิดีโอและนักเขียนสคริปต์ระดับมืออาชีพ
หน้าที่ของคุณคือเขียนสคริปต์วิดีโอสั้น (ประมาณ 45-60 วินาที) สำหรับลง Reels/TikTok 
หัวข้อ: "{topic}"
อารมณ์และสไตล์: {tone}

คำสั่งพิเศษ:
1. การลงท้ายประโยค ให้ใช้คำว่า '{gender_word}' ให้เป็นธรรมชาติ
2. คุณต้องแบ่งสคริปต์ออกเป็น 4-6 ฉาก (Scenes)
3. สำหรับแต่ละฉาก ให้คิด 'คีย์เวิร์ดภาษาอังกฤษ' 1-2 คำ เพื่อใช้ค้นหาวิดีโอประกอบฉากนั้นๆ จากเว็บ Pexels
4. กฎเหล็ก: คีย์เวิร์ดค้นหาภาพ 'ต้อง' มีคำว่า "Asian" หรือ "Thailand" ประกอบอยู่ด้วยเสมอ เพื่อให้ภาพออกมาเป็นคนเอเชีย (เช่น "Asian doctor", "Thailand street food", "Asian family eating")
5. ห้ามมีคำอธิบายอื่นๆ ให้ส่งผลลัพธ์เป็น JSON Array เท่านั้น โดยมีโครงสร้างดังนี้:

[
  {{
    "scene_number": 1,
    "text": "บทพูดของฉากที่ 1",
    "search_keyword": "Asian doctor"
  }},
  {{
    "scene_number": 2,
    "text": "บทพูดของฉากที่ 2",
    "search_keyword": "Asian hospital"
  }}
]
"""

    for i in range(max_retries):
        try:
            print(f"กำลังขอให้ Gemini คิดบทและแบ่งฉากให้ (ครั้งที่ {i+1})...")
            response = model.generate_content(prompt)
            
            # ทำความสะอาดและแปลงเป็น JSON
            text_response = response.text.strip()
            if text_response.startswith('`json'):
                text_response = text_response.replace('`json', '')
            if text_response.startswith('`'):
                text_response = text_response.replace('`', '')
            if text_response.endswith('`'):
                text_response = text_response[:-3]
                
            scenes_data = json.loads(text_response.strip())
            return scenes_data
        except Exception as e:
            print(f"⚠️ เกิดข้อผิดพลาดจาก Gemini: {e}")
            import time
            time.sleep(2)
            
    return None

def generate_coupon_caption(raw_text, affiliate_link):
    import os
    import sys
    import google.generativeai as genai
    
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=GEMINI_API_KEY)
    
    model = genai.GenerativeModel('gemini-3.5-flash-lite')
    
    prompt = f"""
คุณคือก๊อปปี้ไรท์เตอร์สายช้อปปิ้งออนไลน์ 
ฉันมีข้อความดิบที่ดูดมาจากหน้าแคมเปญส่วนลดของ Shopee (ซึ่งจะมีขยะปนอยู่เยอะ)
ข้อมูลดิบ:
'''
{raw_text[:2000]}
'''

หน้าที่ของคุณ:
1. คัดกรองหา "โปรโมชั่นเด็ด" "โค้ดส่วนลด" "เงื่อนไข" เช่น โค้ดส่งฟรี โค้ดลด 50% หรือเงินคืน
2. นำมาเขียนเป็นแคปชั่น Facebook สไตล์เพจโปรโมชั่น แจกวาร์ป โทนตื่นเต้น ดึงดูด
3. ใส่ Emoji ให้น่าอ่าน
4. ต้องจบแคปชั่นด้วยการบอกให้คนกดลิงก์นี้เพื่อไปเก็บโค้ด: {affiliate_link} (ใส่ลิงก์นี้แค่บรรทัดเดียวและครั้งเดียวเท่านั้น ห้ามใส่ลิงก์ซ้ำกัน 2 บรรทัดเด็ดขาด)
5. ไม่ต้องเกริ่นนำใดๆ ตอบเป็นแคปชั่น Facebook มาเลย
"""
    try:
        response = model.generate_content(prompt)
        text = response.text
        # เช็คว่า Gemini เผลอใส่ลิงก์ซ้ำมาหรือไม่
        if text.count(affiliate_link) > 1:
            # ลบลิงก์ที่ซ้ำออกทั้งหมด
            text = text.replace(affiliate_link, "")
            # เอาช่องว่างส่วนเกินด้านล่างออก
            text = text.rstrip()
            # เติมลิงก์กลับเข้าไปทีเดียวตอนจบ
            text += f"\n👉 {affiliate_link}"
        return text
    except Exception as e:
        print(f"⚠️ เกิดข้อผิดพลาดจาก Gemini: {e}")
        return f"🔥 รวมโค้ดลับ Shopee ประจำวัน!\nกดเก็บโค้ดด่วนก่อนหมดโควต้า: {affiliate_link}"

def generate_video_caption(product_name, product_desc, affiliate_link, tone="น่าสนใจ"):
    import os
    import google.generativeai as genai
    import re
    
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        print("❌ ไม่พบ GEMINI_API_KEY")
        return f"{product_name}\n\n👉 พิกัดสั่งซื้อ: {affiliate_link}"
        
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-3.5-flash-lite')
    
    prompt = f"""
คุณคือก๊อปปี้ไรท์เตอร์มืออาชีพสำหรับเขียนแคปชั่นขายของบน Facebook เพจ
ฉันมีวิดีโอรีวิวสินค้า 1 คลิป และต้องการแคปชั่นสำหรับโพสต์คู่วิดีโอนี้

ชื่อสินค้า: {product_name}
รายละเอียด:
'''
{product_desc[:2000]}
'''

หน้าที่ของคุณ:
1. เขียนแคปชั่นสไตล์ "{tone}" ดึงดูดให้คนอยากดูคลิปและกดสั่งซื้อ
2. สรุปจุดเด่นของสินค้าให้อ่านง่าย สบายตา (ใช้ bullet point แบบอิโมจิ)
3. ใส่ Hashtag ที่เกี่ยวข้องประมาณ 3-5 แท็ก ไว้บรรทัดล่างสุด
4. **ห้าม** ใส่ลิงก์ใดๆ ลงในข้อความที่คุณเขียนเด็ดขาด (ฉันจะเติมลิงก์ Shopee ให้เองในภายหลัง)
5. **ห้าม** พิมพ์คำว่า "ลิงก์" หรือ "Link" ทิ้งไว้ให้เติม

ขอแคปชั่นล้วนๆ พร้อมโพสต์ได้เลย
"""
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Remove any stray URLs
        text = re.sub(r'https?://[^\s]+', '', text).strip()
        final_caption = f"{text}\n\n📍 พิกัดสั่งซื้อราคาพิเศษ กดลิงก์นี้ได้เลยครับ 👇\n👉 {affiliate_link}"
        return final_caption
    except Exception as e:
        print(f"❌ Gemini API Error: {e}")
        return f"{product_name}\n\n📍 พิกัดสั่งซื้อ: {affiliate_link}"

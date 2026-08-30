import os
import sys
import time
import glob
import pandas as pd

# นำเข้าเครื่องมือจากโมดูลต่างๆ ที่เราสร้างไว้
from scraper import scrape_shopee_images, download_image, ensure_dir, resolve_affiliate_link
from ai_gen import generate_script, generate_voice
from video_maker import make_video
from fb_poster import post_to_facebook

# แก้ปัญหาภาษาไทยใน CMD
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

HISTORY_FB_FILE = "data/history_facebook.txt"

def get_latest_csv(folder_path="data"):
    """ค้นหาไฟล์ CSV ล่าสุดในโฟลเดอร์ที่กำหนด"""
    ensure_dir(folder_path)
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    if not csv_files:
        return None
    # เลือกล่าสุดจากการเทียบเวลาสร้าง (ctime) และเวลาแก้ไข (mtime)
    return max(csv_files, key=lambda f: max(os.path.getmtime(f), os.path.getctime(f)))

def load_history():
    """โหลดประวัติรหัสสินค้าที่เคยทำคลิป/โพสต์ไปแล้ว"""
    ensure_dir("data")
    if not os.path.exists(HISTORY_FB_FILE):
        return set()
    with open(HISTORY_FB_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def save_history(product_id):
    """บันทึกรหัสสินค้าลงในประวัติ"""
    with open(HISTORY_FB_FILE, "a", encoding="utf-8") as f:
        f.write(f"{product_id}\n")

def process_single_product(product_id, product_name, price, product_url, affiliate_url, image_mode="slideshow", voice_gender="female", tone="ตื่นเต้น ป้ายยา", audio_mode="voice_only", tts_engine="edge", f5_ref_voice=""):
    """ฟังก์ชันจัดการสินค้า 1 ชิ้น ตั้งแต่ต้นจนจบ"""
    save_dir = os.path.join("assets", "products", str(product_id))
    ensure_dir(save_dir)
    
    output_video_path = os.path.join("output", f"reels_{product_id}.mp4")
    use_cache = False
    
    # เช็คว่ามีวิดีโอเดิมอยู่หรือไม่
    if os.path.exists(output_video_path):
        print(f"\n♻️ พบวิดีโอเดิมของสินค้านี้ ({os.path.basename(output_video_path)}) ถูกสร้างไว้แล้วในเครื่อง")
        while True:
            cache_input = input("❓ ต้องการใช้คลิปเดิม หรือสร้างคลิปใหม่? (1=ใช้คลิปเดิม, 2=สร้างใหม่): ").strip()
            if cache_input in ['1', '2']:
                break
            print("⚠️ กรุณาพิมพ์ 1 หรือ 2 เท่านั้น")
            
        if cache_input == '1':
            use_cache = True
            print("🚀 เลือกใช้คลิปเดิม! ข้ามขั้นตอนการสร้างวิดีโอ มุ่งหน้าสู่การโพสต์...")
            
    if not use_cache:
        # -----------------------------------------
        # 1. 🕷️ ดึงข้อมูลและรูปภาพจาก Shopee
        # -----------------------------------------
        # ตรวจสอบว่ามีไฟล์ดิบ (รูป/วิดีโอ) อยู่แล้วหรือไม่ ถ้ามีให้ข้ามการดึงข้อมูลเพื่อป้องกันการโดนแบน
        old_covers = glob.glob(os.path.join(save_dir, "cover_*.jpg"))
        has_video = os.path.exists(os.path.join(save_dir, "original.mp4"))
        
        # ถ้าระบบต้องการวิดีโอ และมีวิดีโออยู่แล้ว หรือ ถ้าระบบต้องการรูป และมีรูปครบแล้ว -> ข้ามการดึงข้อมูล
        skip_scraping = False
        if image_mode == "video" and has_video:
            skip_scraping = True
            print("♻️ พบไฟล์วิดีโอต้นฉบับในเครื่องแล้ว ข้ามขั้นตอนการดึงข้อมูลจาก Shopee (ป้องกันการโดนบล็อก)")
        elif image_mode != "video" and len(old_covers) > 0:
            skip_scraping = True
            print(f"♻️ พบรูปภาพต้นฉบับในเครื่องแล้ว {len(old_covers)} รูป ข้ามขั้นตอนการดึงข้อมูลจาก Shopee")
            
        if not skip_scraping:
            print("\n[1/4] 🕷️ กำลังดึงรูปภาพสินค้า...")
            downloaded_count = 0
            
            if image_mode == "video":
                from scraper import scrape_shopee_video
                print(f"🎥 กำลังค้นหาวิดีโอต้นฉบับจาก Shopee...")
                vid_url = scrape_shopee_video(product_url)
                
                if vid_url:
                    original_vid_path = os.path.join(save_dir, "original.mp4")
                    print(f"พบลิงก์วิดีโอ! กำลังดาวน์โหลด... (อาจใช้เวลาสักครู่)")
                    # ดาวน์โหลดไฟล์ MP4
                    try:
                        res = __import__('requests').get(vid_url, stream=True, timeout=30)
                        if res.status_code == 200:
                            with open(original_vid_path, 'wb') as f:
                                for chunk in res.iter_content(chunk_size=8192):
                                    f.write(chunk)
                            print("✅ ดาวน์โหลดวิดีโอต้นฉบับสำเร็จ!")
                            downloaded_count = 1
                        else:
                            print("❌ ดาวน์โหลดวิดีโอไม่สำเร็จ (Server Error)")
                    except Exception as e:
                        print(f"❌ ดาวน์โหลดวิดีโอพัง: {e}")
                        
                if downloaded_count == 0:
                    print("⚠️ ไม่พบวิดีโอต้นฉบับ หรือดาวน์โหลดล้มเหลว! ระบบจะสลับไปดึง 'สไลด์โชว์ 5 รูป' แทนอัตโนมัติ")
                    image_mode = "slideshow" # Fallback
                    
            if image_mode != "video":
                max_img = 1 if image_mode == "single" else 20
                target_count = 1 if image_mode == "single" else 5
                
                image_urls = scrape_shopee_images(product_url, max_images=max_img)
                
                if not image_urls:
                    print("❌ ข้ามสินค้านี้: ดึงรูปภาพหน้าปกไม่สำเร็จ (อาจติดบล็อกชั่วคราว)")
                    return False
                    
                print(f"พบลิงก์รูปภาพทั้งหมด {len(image_urls)} ลิงก์ กำลังคัดกรองและดาวน์โหลด...")
                for img_url in image_urls:
                    cover_path = os.path.join(save_dir, f"cover_{downloaded_count+1}.jpg")
                    if download_image(img_url, cover_path):
                        downloaded_count += 1
                        if downloaded_count >= target_count:
                            break
                            
            if downloaded_count == 0:
                 print("❌ ข้ามสินค้านี้: เซฟภาพ/วิดีโอลงเครื่องไม่สำเร็จเลย")
                 return False
            else:
                 print(f"✅ จัดเตรียมวัตถุดิบสำเร็จ")
                 
        else:
            # ข้ามการดึงข้อมูล แปลว่ามีไฟล์ดิบพร้อมแล้ว
            downloaded_count = 1
            print(f"✅ จัดเตรียมวัตถุดิบสำเร็จ (ใช้ไฟล์เดิม)")
             
        # -----------------------------------------
        # 2. สร้างสคริปต์และเสียงพากย์ (AI Gen)
        # -----------------------------------------
        print("\n[2/4] 🧠 กำลังให้ AI แต่งสคริปต์และพากย์เสียง...")
        script_path = os.path.join(save_dir, "script.txt")
        audio_path = os.path.join(save_dir, "voice.mp3" if tts_engine in ["edge", "elevenlabs"] else "voice.wav")
        
        script = generate_script(product_name, price, tone=tone, voice_gender=voice_gender)
        if not script:
            print("❌ ข้ามสินค้านี้: AI คิดไม่ออก หรือโควต้า API เต็ม")
            return False
            
        # เซฟสคริปต์
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script)
            
        if audio_mode != "bgm_only":
            if tts_engine == "elevenlabs":
                print("💎 กำลังใช้ ElevenLabs สร้างเสียงพากย์ระดับโลก...")
                from elevenlabs_gen import generate_voice_elevenlabs
                # For ElevenLabs, f5_ref_voice acts as the voice_id
                if not generate_voice_elevenlabs(script, audio_path, voice_id=f5_ref_voice):
                    print("❌ ข้ามสินค้านี้: สร้างเสียงพากย์ ElevenLabs ไม่สำเร็จ")
                    return False
            elif tts_engine == "f5":
                print("🧠 กำลังใช้ F5-TTS สร้างเสียงพากย์ระดับพรีเมียม (อาจใช้เวลาสักครู่)...")
                # Import here to avoid loading PyTorch globally if not needed
                from f5_tts_gen import generate_voice_f5
                ref_audio_path = os.path.join("assets", "voices", f5_ref_voice)
                
                # Check if reference voice exists
                if not os.path.exists(ref_audio_path):
                    print(f"❌ ไม่พบไฟล์เสียงต้นแบบ: {ref_audio_path}")
                    return False
                    
                if not generate_voice_f5(script, audio_path, ref_audio_path):
                    print("❌ ข้ามสินค้านี้: สร้างเสียงพากย์ F5-TTS ไม่สำเร็จ")
                    return False
            else:
                if not generate_voice(script, audio_path, voice_gender=voice_gender):
                    print("❌ ข้ามสินค้านี้: สร้างเสียงพากย์ Edge-TTS ไม่สำเร็จ")
                    return False
        else:
            print("⏭️ ข้ามการสร้างเสียงพากย์ (เลือกโหมดดนตรีอย่างเดียว)")
            
        # -----------------------------------------
        # 3. ตัดต่อวิดีโอ (Video Maker)
        # -----------------------------------------
        print("\n[3/4] 🎬 กำลังตัดต่อและเรนเดอร์วิดีโอ...")
        try:
            make_video(str(product_id), image_mode=image_mode, audio_mode=audio_mode, audio_path=audio_path)
        except Exception as e:
            print(f"❌ ข้ามสินค้านี้: ระบบตัดต่อวิดีโอพัง ({e})")
            return False
            
        if not os.path.exists(output_video_path):
            print("❌ ข้ามสินค้านี้: หาวิดีโอที่ตัดต่อเสร็จไม่พบ")
            return False
            
    # -----------------------------------------
    # 4. โพสต์ลง Facebook (Auto Poster & Auto Comment)
    # -----------------------------------------
    print("\n[4/4] 🚀 กำลังเตรียมโพสต์ลง Facebook Reels...")
    
    # แคปชั่น (ลบลิงก์ออกเพื่อป้องกันโดนบล็อก + ชี้เป้าไปที่คอมเมนต์)
    clean_product_name = product_name.split("(รายละเอียด:")[0].strip()
    caption = f"{clean_product_name}\n\n📍 พิกัดสั่งซื้อราคาพิเศษ: จิ้มดูที่คอมเมนต์แรกด้านล่างได้เลยครับ 👇\n\n(กดลิงก์ในคอมเมนต์เพื่อรับโปรโมชั่นและส่งฟรี)\n\n#ShopeeTH #รีวิวช้อปปี้ #ของดีบอกต่อ #โปรเด็ดอัปเดตทุกวัน"
    
    print(f"\n🎬 วิดีโอพร้อมแล้ว! เชิญตรวจสอบได้ที่: {output_video_path}")
    print(f"📝 แคปชั่นที่จะโพสต์:\n{caption}\n")
    
    while True:
        user_input = input("❓ คุณต้องการโพสต์วิดีโอนี้ลง Facebook หรือไม่? (y/n): ").strip().lower()
        if user_input in ['y', 'yes', 'n', 'no']:
            break
        print("⚠️ กรุณาพิมพ์ y (เพื่อโพสต์) หรือ n (เพื่อข้าม)")
        
    if user_input in ['y', 'yes']:
        print("🚀 กำลังส่งคำสั่งโพสต์ไปยัง Facebook...")
        success = post_to_facebook(output_video_path, caption, affiliate_url)
        if success:
             print(f"✅ สำเร็จ! โพสต์วิดีโอป้ายยาสินค้า {product_id} พร้อมคอมเมนต์เรียบร้อยแล้ว")
             return True # คืนค่า True เพื่อให้ระบบนำรหัสไปจดในสมุดประวัติ
        else:
             print("❌ การโพสต์ Facebook ล้มเหลว (เช็คคุกกี้ หรือปัญหาเน็ต)")
             return False
    else:
        print(f"⏭️ ข้ามการโพสต์สินค้ารหัส {product_id} ตามคำสั่ง (วิดีโอถูกเก็บไว้ที่เครื่องแล้ว)")
        return False # คืนค่า False เพื่อไม่ให้จดประวัติ (รอบหน้าจะได้กลับมาโพสต์ใหม่ได้)

def main():
    print("========================================")
    print("🚀 เริ่มระบบ Auto Post AI (Smart Fallback Mode)")
    print("========================================\n")
    
    print("เลือกลักษณะคลิปวิดีโอที่ต้องการสร้าง:")
    print("1. รูปปกเดี่ยว (ภาพนิ่ง 1 ภาพ)")
    print("2. สไลด์โชว์ 5 ภาพ (ภาพเลื่อน 5 ภาพ)")
    print("3. 🎥 ดูดวิดีโอต้นฉบับ Shopee (พากย์เสียงทับวิดีโอจริง!)")
    while True:
        mode_input = input("👉 พิมพ์ 1, 2 หรือ 3: ").strip()
        if mode_input in ['1', '2', '3']:
            if mode_input == '1': image_mode = "single"
            elif mode_input == '2': image_mode = "slideshow"
            elif mode_input == '3': image_mode = "video"
            break
        print("⚠️ กรุณาพิมพ์ 1, 2 หรือ 3 เท่านั้น")
    print("\n----------------------------------------")
    print("เลือกระบบสร้างเสียงพากย์ (TTS Engine):")
    print("1. 💎 ElevenLabs (พรีเมียมขั้นสุด, เนียน 100%, ใช้ API Key)")
    print("2. ⚡ Edge-TTS (รวดเร็ว, เบาเครื่อง, เสียงมาตรฐาน)")
    print("3. 🌟 F5-TTS (พรีเมียม, ธรรมชาติสูง, โคลนนิ่งเสียงได้)")
    while True:
        tts_input = input("👉 พิมพ์ 1, 2 หรือ 3: ").strip()
        if tts_input in ['1', '2', '3']:
            if tts_input == '1': tts_engine = "elevenlabs"
            elif tts_input == '2': tts_engine = "edge"
            elif tts_input == '3': tts_engine = "f5"
            break
        print("⚠️ กรุณาพิมพ์ 1, 2 หรือ 3 เท่านั้น")
    print("\n----------------------------------------")
    
    voice_gender = "female"
    f5_ref_voice = ""
    
    if tts_engine == "edge":
        print("เลือกเสียงพากย์ (Edge-TTS):")
        print("1. เสียงผู้หญิง (คุณเปรมวดี - นุ่มนวล น่าฟัง)")
        print("2. เสียงผู้ชาย (คุณนิวัฒน์ - เข้มแข็ง น่าเชื่อถือ)")
        while True:
            voice_input = input("👉 พิมพ์ 1 หรือ 2: ").strip()
            if voice_input in ['1', '2']:
                voice_gender = "female" if voice_input == '1' else "male"
                break
            print("⚠️ กรุณาพิมพ์ 1 หรือ 2 เท่านั้น")
        print("\n----------------------------------------")
    elif tts_engine == "elevenlabs":
        print("เลือกเสียงพากย์ (ElevenLabs):")
        print("1. 👱‍♀️ Alice (ผู้หญิง เสียงใส น่าฟัง ชัดเจน)")
        print("2. 👦 Liam (ผู้ชาย พลังล้น เหมาะกับป้ายยาคลิปสั้น)")
        print("3. 🌟 กำหนดรหัสเสียงเอง (Custom Voice ID)")
        while True:
            el_input = input("👉 พิมพ์ 1, 2 หรือ 3: ").strip()
            if el_input == '1': 
                f5_ref_voice = "Xb7hH8MSUJpSbSDYk0k2"
                voice_gender = "female"
                break
            elif el_input == '2': 
                f5_ref_voice = "TX3LPaxmHKxFdv7VOQHJ"
                voice_gender = "male"
                break
            elif el_input == '3':
                f5_ref_voice = input("👉 วางรหัส Voice ID จากเว็บ ElevenLabs: ").strip()
                # Default to female or we can ask, let's assume female for custom
                voice_gender = "female"
                break
            print("⚠️ กรุณาพิมพ์ 1, 2 หรือ 3 เท่านั้น")
        print("\n----------------------------------------")
    else:
        print("เลือกเสียงต้นแบบ (F5-TTS Voice Clone):")
        print("1. 👱‍♀️ เสียงผู้หญิง (สดใส น่ารัก)")
        print("2. 👩‍💼 เสียงผู้หญิง (ทางการ ผู้ใหญ่)")
        print("3. 👦 เสียงผู้ชาย (วัยรุ่น น่ารัก)")
        print("4. 👨‍💼 เสียงผู้ชาย (นุ่มลึก น่าเชื่อถือ)")
        print("5. 🌟 เสียงกำหนดเอง (Custom Voice - ใช้ไฟล์ที่โหลดมาเอง)")
        while True:
            f5_input = input("👉 พิมพ์เลข 1 ถึง 5: ").strip()
            if f5_input == '1': 
                f5_ref_voice = "female_cute.wav"
                voice_gender = "female"
                break
            elif f5_input == '2': 
                f5_ref_voice = "female_formal.wav"
                voice_gender = "female"
                break
            elif f5_input == '3': 
                f5_ref_voice = "male_cute.wav"
                voice_gender = "male"
                break
            elif f5_input == '4': 
                f5_ref_voice = "male_deep.wav"
                voice_gender = "male"
                break
            elif f5_input == '5': 
                f5_ref_voice = input("👉 พิมพ์ชื่อไฟล์เสียงต้นแบบ (ต้องอยู่ในโฟลเดอร์ assets/voices/ เช่น myvoice.wav): ").strip()
                voice_gender = "female"
                break
            print("⚠️ กรุณาพิมพ์เลข 1 ถึง 5 เท่านั้น")
        print("\n----------------------------------------")
    
    print("เลือกอารมณ์และสไตล์การเขียนสคริปต์ (Tone):")
    print("1. 🤩 ตื่นเต้น ป้ายยาหนักๆ (กระตุ้นให้รีบซื้อ)")
    print("2. 👔 ทางการ น่าเชื่อถือ (สำหรับสินค้าไฮเอนด์/อิเล็กทรอนิกส์)")
    print("3. 🤪 วัยรุ่น ตลกๆ กวนๆ (เป็นกันเองสุดๆ)")
    print("4. 🩺 สายสุขภาพ/ความงาม (อ่อนโยน ห่วงใย ให้คำปรึกษา)")
    print("5. 🧹 สายแม่บ้าน/ของใช้ (เน้นความคุ้มค่า รีวิวจากการใช้จริง)")
    print("6. 🔥 สายดุดัน ฮาร์ดคอร์ (ขายแบบตะโกน ดุดันไม่เกรงใจใคร)")
    print("7. 🥺 สายออดอ้อน (น่ารักๆ อ้อนคนดูให้ซื้อ)")
    while True:
        tone_input = input("👉 พิมพ์เลข 1 ถึง 7: ").strip()
        if tone_input == '1':
            tone = "ตื่นเต้น ป้ายยาหนักๆ ให้รีบซื้อทันที"
            break
        elif tone_input == '2':
            tone = "ทางการ น่าเชื่อถือ รีวิวแบบผู้เชี่ยวชาญ"
            break
        elif tone_input == '3':
            tone = "วัยรุ่น ตลก กวนๆ เป็นกันเองเหมือนเพื่อนป้ายยาเพื่อน"
            break
        elif tone_input == '4':
            tone = "อ่อนโยน ห่วงใยสุขภาพและความงาม ให้คำปรึกษาแบบใจดี"
            break
        elif tone_input == '5':
            tone = "แม่บ้าน/พ่อบ้าน รีวิวจากการใช้งานจริง เน้นความคุ้มค่า ประหยัดเงิน"
            break
        elif tone_input == '6':
            tone = "ดุดัน ฮาร์ดคอร์ ตะโกนขายแบบจริงจัง พลังเยอะๆ ดุดันไม่เกรงใจใคร"
            break
        elif tone_input == '7':
            tone = "ออดอ้อน น่ารักๆ พูดจาหวานๆ อ้อนให้คนดูใจอ่อนจนต้องกดซื้อ"
            break
        print("⚠️ กรุณาพิมพ์เลข 1 ถึง 7 เท่านั้น")
    print("\n----------------------------------------")
    
    print("เลือกระบบเสียง (Audio Mode):")
    print("1. 🗣️ เสียงพากย์ AI อย่างเดียว")
    print("2. 🎵 เสียงดนตรีประกอบ (BGM) อย่างเดียว (ไม่มีคนพูด)")
    print("3. 🗣️+🎵 เสียงพากย์ AI + เสียงดนตรีคลอเบาๆ (15%)")
    while True:
        audio_input = input("👉 พิมพ์ 1, 2 หรือ 3: ").strip()
        if audio_input == '1':
            audio_mode = "voice_only"
            break
        elif audio_input == '2':
            audio_mode = "bgm_only"
            break
        elif audio_input == '3':
            audio_mode = "voice_and_bgm"
            break
        print("⚠️ กรุณาพิมพ์ 1, 2 หรือ 3 เท่านั้น")
    print("\n----------------------------------------")
    
    # โหลดประวัติการโพสต์
    posted_history = load_history()
    print(f"📜 ตรวจพบประวัติการทำคลิปแล้ว {len(posted_history)} รายการ")
    
    # ระบบหยิบไฟล์ล่าสุดอัตโนมัติ
    csv_path = get_latest_csv("data")
    if not csv_path:
        print(f"❌ ไม่พบไฟล์ .csv ใดๆ ในโฟลเดอร์ data เลย กรุณานำไฟล์มาใส่ก่อนครับ")
        return
        
    print(f"📂 เลือกไฟล์ข้อมูลล่าสุดอัตโนมัติ: {os.path.basename(csv_path)}")
    try:
        df = pd.read_csv(csv_path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv(csv_path, encoding="cp874")
    print(f"📋 พบสินค้าในคิวทั้งหมด {len(df)} รายการ\n")
    
    success_count = 0
    total_items = 0
    
    for index, row in df.iterrows():
        # ตรวจสอบว่ามีคอลัมน์ลิงก์ข้อเสนอหรือไม่
        if 'ลิงก์ข้อเสนอ' not in row or pd.isna(row['ลิงก์ข้อเสนอ']):
            continue
            
        total_items += 1
        affiliate_url = str(row['ลิงก์ข้อเสนอ']).strip()
        
        # เช็คว่าเป็นไฟล์เต็ม หรือไฟล์ทำเอง (มีแค่ลิงก์)
        has_full_data = ('ชื่อสินค้า' in row and not pd.isna(row['ชื่อสินค้า'])) and ('รหัสสินค้า' in row and not pd.isna(row['รหัสสินค้า']))
        
        if has_full_data:
            # 🟢 เคสปกติ (ไฟล์จัดเต็ม)
            product_id = str(row['รหัสสินค้า']).strip()
            if product_id.endswith('.0'): product_id = product_id[:-2]
            
            # เช็คประวัติการโพสต์
            if product_id in posted_history:
                print(f"----------------------------------------")
                print(f"⏭️ ข้ามคิวที่ {total_items}: สินค้ารหัส {product_id} (เคยโพสต์ลง Facebook ไปแล้ว!)")
                continue
                
            product_name = str(row['ชื่อสินค้า'])
            price = str(row['ราคา']) if 'ราคา' in row and not pd.isna(row['ราคา']) else "ราคาพิเศษ"
            product_url = str(row['ลิงก์สินค้า']) if 'ลิงก์สินค้า' in row and not pd.isna(row['ลิงก์สินค้า']) else affiliate_url
        else:
            # 🟡 เคสรีบด่วน (Smart Fallback) แกะข้อมูลจากลิงก์
            print(f"----------------------------------------")
            print(f"🕵️‍♂️ [โหมดนักสืบ] กำลังแกะข้อมูลสินค้าจากลิงก์: {affiliate_url}")
            details = resolve_affiliate_link(affiliate_url)
            if not details:
                print(f"❌ ข้ามคิวนี้: แกะลิงก์ไม่สำเร็จ")
                continue
                
            product_id = details['product_id']
            
            # เช็คประวัติการโพสต์หลังจากแกะรหัสสินค้าได้แล้ว
            if product_id in posted_history:
                print(f"⏭️ ข้ามคิวที่ {total_items}: สินค้ารหัส {product_id} (เคยโพสต์ลง Facebook ไปแล้ว!)")
                continue
                
            # แนบรายละเอียดเข้าไปในชื่อสินค้าให้ AI อ่านด้วย
            product_name = f"{details['product_name']} (รายละเอียด: {details['product_desc']})"
            price = "ราคาโปรโมชั่นพิเศษ (ให้คนดูคลิกเช็คในตะกร้า)"
            product_url = details['product_url']
            print(f"✅ แกะข้อมูลสำเร็จ: {details['product_name'][:40]}...")
            
        print(f"----------------------------------------")
        print(f"📦 เริ่มคิวที่ {total_items}: {product_name[:40]}...")
        print(f"----------------------------------------")
        
        # สั่งประมวลผล
        result = process_single_product(
            product_id, product_name, price, product_url, affiliate_url, 
            image_mode=image_mode, voice_gender=voice_gender, tone=tone, audio_mode=audio_mode,
            tts_engine=tts_engine, f5_ref_voice=f5_ref_voice
        )
        
        if result:
            success_count += 1
            posted_history.add(product_id)
            save_history(product_id)
            
        if total_items < len(df):
            print(f"\n⏳ พักหายใจ 1 นาที ก่อนเริ่มสินค้าตัวถัดไป... (ป้องกัน Facebook บล็อก)")
            time.sleep(60)
        
    print("\n========================================")
    print(f"🎉 กระบวนการทั้งหมดเสร็จสิ้น!")
    print(f"📊 สรุปผลงาน: โพสต์สำเร็จ {success_count} / {total_items} รายการ")
    print("========================================")

if __name__ == "__main__":
    main()

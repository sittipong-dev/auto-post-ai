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
    
    # แคปชั่น (ใส่ลิงก์ตรงๆ ลงไปในโพสต์เลยตามคำสั่ง)
    clean_product_name = product_name.split("(โค้ด:")[0].strip()
    caption = f"{clean_product_name}\n\n📍 พิกัดสั่งซื้อราคาพิเศษ กดลิงก์นี้ได้เลยครับ 👇\n👉 {affiliate_url}\n\n(กดลิงก์เพื่อรับโปรโมชั่นและส่งฟรี)\n\n#ShopeeTH #รีวิวช้อปปี้ #ของดีบอกต่อ #โปรเด็ดอัปเดตทุกวัน"
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


def process_broll_mode(tts_engine, voice_gender, f5_ref_voice, visual_source):
    print("\n========================================")
    print("🎬 เข้าสู่โหมดสร้างคลิปให้ความรู้ (Auto B-Roll)")
    print("========================================")
    
    csv_path = "data/content_maker.csv"
    if not os.path.exists(csv_path):
        import pandas as pd
        df = pd.DataFrame(columns=["หัวข้อ", "ลิงก์ข้อเสนอ"])
        df.loc[0] = ["5 วิธีลดน้ำหนักแบบไม่เครียด", "https://shope.ee/xxx"]
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        print(f"\n❌ ไม่พบไฟล์ {csv_path}")
        print(f"✅ บอทได้สร้างไฟล์ต้นแบบไว้ให้แล้ว กรุณาไปกรอก 'หัวข้อ' ในไฟล์ data/content_maker.csv แล้วรันใหม่ครับ")
        return
        
    import pandas as pd
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    print(f"📋 พบหัวข้อในคิวทั้งหมด {len(df)} รายการ\n")
    
    posted_history = load_history()
    success_count = 0
    total_items = 0
    
    for index, row in df.iterrows():
        topic = str(row.get('หัวข้อ', '')).strip()
        affiliate_url = str(row.get('ลิงก์ข้อเสนอ', '')).strip()
        
        if not topic or pd.isna(row.get('หัวข้อ')):
            continue
            
        total_items += 1
        
        import hashlib
        topic_id = hashlib.md5(topic.encode('utf-8')).hexdigest()[:8]
        
        if topic_id in posted_history:
            print(f"\n⏭️ ข้ามคิวที่ {total_items}: หัวข้อ '{topic}' (เคยทำคลิปและโพสต์ไปแล้ว!)")
            continue
            
        print(f"\n----------------------------------------")
        print(f"🔥 เริ่มคิวที่ {total_items}: สร้างคลิปหัวข้อ '{topic}'")
        print(f"----------------------------------------")
        
        # 1. ให้ AI คิดบทและคีย์เวิร์ด
        from ai_gen import generate_broll_script
        scenes_data = generate_broll_script(topic, voice_gender=voice_gender)
        
        if not scenes_data:
            print("❌ ไม่สามารถสร้างสคริปต์ได้ ข้ามคิวนี้")
            continue
            
        # --- ระบบผู้กำกับตรวจบท (Script Review) ---
        print("\n========================================")
        print("📝 สคริปต์ที่ Gemini คิดมาให้:")
        for idx, sc in enumerate(scenes_data):
            kw_th = sc.get('search_keyword_th', 'ไม่มีคีย์เวิร์ด')
            kw_en = sc.get('search_keyword_en', 'Asian')
            print(f"🎬 ฉากที่ {idx+1}: [ไทย: {kw_th} | ENG: {kw_en}] {sc.get('text', '')}")
        print("========================================")
        
        edit_choice = input("\n👉 ต้องการแก้ไขบทพูดหรือคีย์เวิร์ดภาพไหม? (y = แก้ไข / n = ไม่แก้ ลุยต่อเลย): ").strip().lower()
        if edit_choice == 'y':
            script_file = os.path.join("data", "review_script.txt")
            with open(script_file, "w", encoding="utf-8") as f:
                for idx, sc in enumerate(scenes_data):
                    f.write(f"--- ฉากที่ {idx+1} ---\n")
                    f.write(f"[คำค้นหาภาพ (ไทย)]: {sc.get('search_keyword_th', '')}\n")
                    f.write(f"[Search Keyword (ENG)]: {sc.get('search_keyword_en', '')}\n")
                    f.write(f"[บทพูด]: {sc.get('text', '')}\n\n")
            
            print(f"\n⏳ โปรแกรมกำลังเปิดหน้าต่าง Notepad ขึ้นมา...")
            print(f"⚠️ กรุณาแก้บทใน Notepad -> กด File -> Save -> แล้วกลับมากด Enter ที่หน้าจอดำนี้ครับ")
            import subprocess
            try:
                subprocess.Popen(['notepad.exe', os.path.abspath(script_file)])
            except Exception as e:
                print(f"❌ เปิด Notepad ไม่สำเร็จ: {e}")
            input("\n✅ เซฟใน Notepad เสร็จแล้วใช่ไหมครับ? กด Enter 1 ครั้งเพื่อสร้างวิดีโอต่อได้เลย... ")
            
            # อ่านค่ากลับมา
            new_scenes_data = []
            current_scene = {}
            if os.path.exists(script_file):
                with open(script_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("--- ฉากที่"):
                            if current_scene:
                                new_scenes_data.append(current_scene)
                                current_scene = {}
                            current_scene['scene_number'] = len(new_scenes_data) + 1
                        elif line.startswith("[คำค้นหาภาพ]:"):
                            current_scene['search_keyword'] = line.replace("[คำค้นหาภาพ]:", "").strip()
                        elif line.startswith("[บทพูด]:"):
                            current_scene['text'] = line.replace("[บทพูด]:", "").strip()
                if current_scene:
                    new_scenes_data.append(current_scene)
                    
            if new_scenes_data:
                scenes_data = new_scenes_data
                print("✅ อัปเดตสคริปต์ฉบับแก้ไขเรียบร้อยแล้ว ลุยต่อ!")
            else:
                print("⚠️ อ่านสคริปต์ไม่สำเร็จ ใช้สคริปต์เดิมจาก AI")
        # --- จบระบบผู้กำกับตรวจบท ---
            
        # 2. ตัดต่อวิดีโอ
        from video_maker import make_broll_video
        success = make_broll_video(topic_id, scenes_data, tts_engine=tts_engine, f5_ref_voice=f5_ref_voice, voice_gender=voice_gender, visual_source=visual_source)
        
        if not success:
            print("❌ ตัดต่อวิดีโอไม่สำเร็จ ข้ามคิวนี้")
            continue
            
        output_video_path = os.path.join("output", f"broll_{topic_id}.mp4")
        
        # 3. ให้ Gemini สรุปแคปชั่น
        print(f"\n📝 กำลังให้ Gemini เขียนแคปชั่นโพสต์เฟสบุ๊ค...")
        from ai_gen import generate_script
        model = __import__('google.generativeai').generativeai.GenerativeModel('gemini-3.5-flash-lite')
        prompt_cap = f"เขียนแคปชั่น Facebook ให้ความรู้เรื่อง '{topic}' แนบลิงก์นี้ตอนท้าย: {affiliate_url}"
        try:
            caption = model.generate_content(prompt_cap).text
        except:
            caption = f"คลิปความรู้เรื่อง {topic}\n\nสนใจสินค้าคลิก: {affiliate_url}"
            
        # --- ระบบตรวจวิดีโอก่อนโพสต์ ---
        print(f"\n✅ สร้างวิดีโอเสร็จสมบูรณ์! ไฟล์บันทึกอยู่ที่: {output_video_path}")
        print(f"📝 แคปชั่นที่จะโพสต์:\n{caption}\n")
        
        while True:
            post_choice = input(f"❓ คุณต้องการโพสต์วิดีโอนี้ลง Facebook หรือไม่? (y = โพสต์เลย / n = ขอเก็บไว้ก่อน): ").strip().lower()
            if post_choice in ['y', 'yes', 'n', 'no']:
                break
            print("⚠️ กรุณาพิมพ์ y (เพื่อโพสต์) หรือ n (เพื่อข้าม)")
            
        if post_choice in ['y', 'yes']:
            # 4. โพสต์ลงเพจ
            print(f"\n🌐 กำลังโพสต์ลง Facebook...")
            from fb_poster import post_to_facebook
            post_success = post_to_facebook(output_video_path, caption)
        else:
            print(f"\n⏭️ ยกเลิกการโพสต์ (ไฟล์วิดีโอถูกเก็บไว้ที่เครื่องแล้ว)")
            post_success = False
        
        if post_success:
            print(f"✅ โพสต์ '{topic}' สำเร็จ!")
            success_count += 1
            save_history(topic_id)
            posted_history.add(topic_id)
        else:
            print(f"❌ โพสต์ล้มเหลว")
            
        if total_items < len(df):
            print(f"\n⏳ พักหายใจ 1 นาที ก่อนเริ่มหัวข้อถัดไป...")
            import time
            time.sleep(60)
            
    print("\n========================================")
    print(f"🎉 กระบวนการทั้งหมดเสร็จสิ้น!")
    print(f"📊 สรุปผลงาน: โพสต์สำเร็จ {success_count} / {total_items} รายการ")
    print("========================================")



def run_coupon_hunter_mode():
    from coupon_scraper import scrape_coupon_page
    from ai_gen import generate_coupon_caption
    from fb_poster import post_to_facebook
    
    print("\n--- โหมดนักล่าโปรโมชั่น (Coupon Hunter) ---")
    print("เลือกวิธีล่าโปรโมชั่น:")
    print("1. 🤖 บอทหาให้อัตโนมัติ (กวาดหน้าโค้ดส่งฟรี / แคมเปญหลัก)")
    print("2. 🎯 ป้อนลิงก์เป้าหมายเอง (มีลิงก์แคมเปญพิเศษมาให้)")
    
    while True:
        hunt_mode = input("👉 พิมพ์ 1 หรือ 2: ").strip()
        if hunt_mode in ['1', '2']:
            break
        print("⚠️ กรุณาพิมพ์ 1 หรือ 2 เท่านั้น")
        
    if hunt_mode == '1':
        campaign_url = "https://shopee.co.th/m/avc-fsv-all-vouchers"
        print(f"\n🔗 เป้าหมายอัตโนมัติ: {campaign_url}")
    else:
        campaign_url = input("\n🔗 กรุณาใส่ URL แคมเปญ (ลิงก์ยาว): ").strip()
        if not campaign_url:
            print("❌ ต้องระบุ URL")
            return
            
    aff_url = input("💰 กรุณาใส่ลิงก์ Affiliate ของคุณ (s.shopee): ").strip()
    if not aff_url:
        aff_url = campaign_url
        
    raw_text = scrape_coupon_page(campaign_url)
    if not raw_text:
        print("❌ ไม่สามารถดึงข้อมูลส่วนลดได้")
        return
        
    print("\n📝 กำลังให้ Gemini ร่ายมนต์แต่งแคปชั่นโปรโมชั่น...")
    caption = generate_coupon_caption(raw_text, aff_url)
    print("\n========================================")
    print("✨ แคปชั่นที่แต่งเสร็จแล้ว:")
    print("========================================")
    print(caption)
    print("========================================\n")
    
    while True:
        post_choice = input("❓ ต้องการโพสต์ลง Facebook หรือไม่? (y = โพสต์เลย / n = ยกเลิก): ").strip().lower()
        if post_choice in ['y', 'yes', 'n', 'no']:
            break
            
    if post_choice in ['y', 'yes']:
        print("🚀 กำลังส่งบอทโพสต์ Facebook...")
        success = post_to_facebook(None, caption)
        if success:
            print("🎉 โพสต์โปรโมชั่นขึ้นเพจเรียบร้อย เตรียมรับทรัพย์!")
        else:
            print("❌ โพสต์ไม่สำเร็จ ลองก๊อปปี้ไปโพสต์เองก่อนนะครับ")
    else:
        print("⏭️ ยกเลิกการโพสต์")
def run_media_downloader_mode():
    import os
    import time
    from scraper import scrape_shopee_images, scrape_shopee_video, download_image, resolve_affiliate_link
    import requests
    
    print("\n--- 📥 โหมดที่ 4: ดูดสื่อ Shopee (ดาวน์โหลดภาพและวิดีโอ) ---")
    print("ระบบนี้จะช่วยดูดภาพความละเอียดสูงและวิดีโอจากหน้าสินค้า Shopee")
    print("เพื่อให้คุณนำไปใช้ตัดต่อวิดีโอด้วยตัวเองในโปรแกรมอื่น")
    
    url = input("\n🔗 กรุณาแปะลิงก์สินค้า Shopee: ").strip()
    if not url:
        print("❌ ยกเลิกการดาวน์โหลด (ไม่ได้ระบุ URL)")
        return
        
    folder_name = input("📁 ตั้งชื่อโฟลเดอร์ (กด Enter เพื่อให้ตั้งชื่อตาม รหัสสินค้า-ชื่อสินค้า): ").strip()
    
    print("🔍 กำลังแปลผลลิงก์และตรวจสอบสินค้า...")
    info = resolve_affiliate_link(url)
    if info is None:
        print("❌ ยกเลิกการดาวน์โหลด เนื่องจากสินค้าไม่มีอยู่จริง")
        return
        
    # ใช้ URL เต็มแทน URL ย่อ เพื่อให้โปรแกรมดูดภาพได้สำเร็จ
    if info and info['product_url']:
        url = info['product_url']
        
    if not folder_name:
        if info and info['product_id']:
            # เอาอักขระพิเศษออกให้ปลอดภัยกับชื่อโฟลเดอร์
            safe_name = "".join(c for c in info['product_name'] if c.isalnum() or c in (' ', '-', '_')).strip()
            # ตัดชื่อยาวเกินไป
            safe_name = safe_name[:50]
            folder_name = f"{info['product_id']}-{safe_name}"
        else:
            folder_name = f"shopee_media_{int(time.time())}"
            
    save_dir = os.path.abspath(os.path.join("midea", "downloads", folder_name))
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    print(f"\n🚀 กำลังค้นหาข้อมูลจากลิงก์: {url}")
    
    # 1. ดูดวิดีโอ
    print("🎥 กำลังค้นหาวิดีโอ...")
    video_url = scrape_shopee_video(url)
    if video_url:
        print(f"✅ พบวิดีโอ! กำลังดาวน์โหลด...")
        try:
            video_path = os.path.join(save_dir, "video.mp4")
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(video_url, headers=headers, stream=True)
            if response.status_code == 200:
                with open(video_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk: f.write(chunk)
                print(f"💾 โหลดวิดีโอสำเร็จ! -> {video_path}")
            else:
                print("❌ โหลดวิดีโอไม่สำเร็จ (เซิร์ฟเวอร์ปฏิเสธ)")
        except Exception as e:
            print(f"❌ โหลดวิดีโอพัง: {e}")
    else:
        print("⚠️ ไม่พบวิดีโอในสินค้านี้")
        
    # 2. ดูดรูปภาพ
    print("\n🖼️ กำลังค้นหารูปภาพ...")
    image_urls = scrape_shopee_images(url, max_images=15)
    
    if image_urls:
        print(f"✅ พบรูปภาพ {len(image_urls)} รูป! กำลังดาวน์โหลด...")
        count = 0
        for i, img_url in enumerate(image_urls):
            img_path = os.path.join(save_dir, f"image_{i+1}.jpg")
            success = download_image(img_url, img_path)
            if success:
                count += 1
                print(f"  [{count}] เซฟรูปสำเร็จ -> image_{i+1}.jpg")
        print(f"💾 โหลดรูปภาพสำเร็จทั้งหมด {count} รูป!")
    else:
        print("⚠️ ไม่พบรูปภาพ หรือเว็บปิดกั้นการดูดข้อมูล")
        
    print(f"\n========================================")
    print(f"🎉 ดาวน์โหลดสื่อเสร็จสมบูรณ์!")
    print(f"📂 ไฟล์ทั้งหมดถูกเก็บไว้ที่:\n{save_dir}")
    print(f"========================================")
    
    # เปิดโฟลเดอร์ให้ผู้ใช้ดูเลย
    try:
        os.startfile(save_dir)
    except:
        pass

def main():

    print("========================================")
    print("🚀 เริ่มระบบ Auto Post AI")
    print("========================================\n")
    
    print("เลือกโหมดการทำงาน:")
    print("1. 🛒 โหมดเซลส์แมน (Shopee Affiliate)")
    print("2. 🎓 โหมดครีเอเตอร์ให้ความรู้ (Auto B-Roll Pexels)")
    print("3. ✂️ โหมดนักล่าโปรโมชั่น (Coupon Hunter)")
    print("4. 📥 โหมดดูดสื่อ Shopee (ดาวน์โหลดภาพและวิดีโอเพียวๆ)")
    print("5. 🧹 โหมดผู้คุม (เช็คและลบโพสต์ลิงก์ตายบนเฟสบุ๊ค)")
    
    while True:
        work_mode = input("👉 พิมพ์เลข 1-5: ").strip()
        if work_mode in ['1', '2', '3', '4', '5']:
            break
        print("⚠️ กรุณาพิมพ์เลข 1-5 เท่านั้น")
        
    if work_mode == '3':
        run_coupon_hunter_mode()
        sys.exit(0)
    elif work_mode == '4':
        run_media_downloader_mode()
        sys.exit(0)
    elif work_mode == '5':
        from fb_cleaner import clean_dead_links
        page_url = input("\n🔗 กรุณาใส่ URL หน้าเพจ Facebook ของคุณ: ").strip()
        if page_url:
            clean_dead_links(page_url)
        else:
            print("❌ ยกเลิกการสแกน (ไม่ได้ระบุลิงก์เพจ)")
        sys.exit(0)
        
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
        print("1. เสียงผู้หญิง (คุณเปรมวดี)")
        print("2. เสียงผู้ชาย (คุณนิวัฒน์)")
        while True:
            voice_input = input("👉 พิมพ์ 1 หรือ 2: ").strip()
            if voice_input in ['1', '2']:
                voice_gender = "female" if voice_input == '1' else "male"
                break
            print("⚠️ กรุณาพิมพ์ 1 หรือ 2 เท่านั้น")
    elif tts_engine == "elevenlabs":
        print("เลือกเสียงพากย์ (ElevenLabs):")
        print("1. 👱‍♀️ Alice (ผู้หญิง เสียงใส)")
        print("2. 👦 Brian (ผู้ชาย พลังล้น)")
        print("3. 🌟 กำหนดรหัสเสียงเอง")
        while True:
            voice_input = input("👉 พิมพ์ 1, 2 หรือ 3: ").strip()
            if voice_input == '1':
                f5_ref_voice = "Xb7hH8MSUJpSbSDYk0k2"
                voice_gender = "female"
                break
            elif voice_input == '2':
                f5_ref_voice = "nPczCjzI2devNBz1zQrb"
                voice_gender = "male"
                break
            elif voice_input == '3':
                f5_ref_voice = input("👉 พิมพ์ Voice ID ของ ElevenLabs: ").strip()
                voice_gender = "female"
                break
            print("⚠️ กรุณาพิมพ์ 1, 2 หรือ 3 เท่านั้น")
            
    print("\n----------------------------------------")
    
    if work_mode == '2':
        print("\n----------------------------------------")
        print("เลือกแหล่งวัตถุดิบภาพประกอบคลิป:")
        print("1. 🎥 วิดีโอสต็อก (Pexels) - ภาพสากล หรูหรา (ใช้คีย์เวิร์ดอังกฤษ)")
        print("2. 🖼️ ค้นหาภาพอัจฉริยะ (Web Image) - ค้นหาจากอินเทอร์เน็ตด้วยคีย์เวิร์ดภาษาไทย + เอฟเฟกต์ภาพซูม")
        while True:
            vis_input = input("👉 พิมพ์ 1 หรือ 2: ").strip()
            if vis_input in ['1', '2']:
                visual_source = "pexels" if vis_input == '1' else "web_image"
                break
        process_broll_mode(tts_engine, voice_gender, f5_ref_voice, visual_source)
        return
        
    print("เลือกอารมณ์และสไตล์การเขียนสคริปต์ (Tone):")
    print("1. 🤩 ตื่นเต้น ป้ายยาหนักๆ (กระตุ้นให้รีบซื้อ)")
    print("2. 👔 ทางการ น่าเชื่อถือ (สำหรับสินค้าไฮเอนด์)")
    print("3. 🤪 วัยรุ่น ตลกๆ กวนๆ (เป็นกันเองสุดๆ)")
    print("4. 🩺 สายสุขภาพ/ความงาม (อ่อนโยน ห่วงใย)")
    while True:
        tone_input = input("👉 พิมพ์เลข 1 ถึง 4: ").strip()
        if tone_input == '1': tone = "ตื่นเต้น ป้ายยาหนักๆ ให้รีบซื้อทันที"; break
        elif tone_input == '2': tone = "ทางการ น่าเชื่อถือ รีวิวแบบผู้เชี่ยวชาญ"; break
        elif tone_input == '3': tone = "วัยรุ่น ตลก กวนๆ"; break
        elif tone_input == '4': tone = "อ่อนโยน ห่วงใยสุขภาพ"; break
        print("⚠️ กรุณาพิมพ์เลข 1 ถึง 4 เท่านั้น")
        
    print("\n----------------------------------------")
    print("เลือกลักษณะคลิปวิดีโอ (โหมด Shopee):")
    print("1. รูปปกเดี่ยว (ภาพนิ่ง 1 ภาพ)")
    print("2. สไลด์โชว์ 5 ภาพ (ภาพเลื่อน 5 ภาพ)")
    print("3. 🎥 ดูดวิดีโอต้นฉบับ Shopee")
    while True:
        mode_input = input("👉 พิมพ์ 1, 2 หรือ 3: ").strip()
        if mode_input in ['1', '2', '3']:
            if mode_input == '1': image_mode = "single"
            elif mode_input == '2': image_mode = "slideshow"
            elif mode_input == '3': image_mode = "video"
            break
            
    audio_mode = "voice_only"
    
    posted_history = load_history()
    csv_path = get_latest_csv("data")
    if not csv_path:
        print(f"❌ ไม่พบไฟล์ .csv เลย กรุณานำไฟล์มาใส่ก่อนครับ")
        return
        
    import pandas as pd
    try:
        df = pd.read_csv(csv_path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv(csv_path, encoding="cp874")
        
    success_count = 0
    total_items = 0
    
    for index, row in df.iterrows():
        if 'ลิงก์ข้อเสนอ' not in row or pd.isna(row['ลิงก์ข้อเสนอ']):
            continue
            
        total_items += 1
        affiliate_url = str(row['ลิงก์ข้อเสนอ']).strip()
        
        has_full_data = ('ชื่อสินค้า' in row and not pd.isna(row['ชื่อสินค้า'])) and ('รหัสสินค้า' in row and not pd.isna(row['รหัสสินค้า']))
        
        if has_full_data:
            product_id = str(row['รหัสสินค้า']).strip()
            if product_id.endswith('.0'): product_id = product_id[:-2]
            
            if product_id in posted_history:
                continue
                
            product_name = str(row['ชื่อสินค้า'])
            price = str(row['ราคา']) if 'ราคา' in row and not pd.isna(row['ราคา']) else "ราคาพิเศษ"
            product_url = str(row['ลิงก์สินค้า']) if 'ลิงก์สินค้า' in row and not pd.isna(row['ลิงก์สินค้า']) else affiliate_url
        else:
            from scraper import resolve_affiliate_link
            details = resolve_affiliate_link(affiliate_url)
            if not details: continue
            product_id = details['product_id']
            if product_id in posted_history: continue
            product_name = details['product_name']
            price = "ราคาโปร"
            product_url = details['product_url']
            
        result = process_single_product(
            product_id, product_name, price, product_url, affiliate_url, 
            image_mode=image_mode, voice_gender=voice_gender, tone=tone, audio_mode=audio_mode,
            tts_engine=tts_engine, f5_ref_voice=f5_ref_voice
        )
        
        if result:
            success_count += 1
            posted_history.add(product_id)
            save_history(product_id)
            
    print(f"🎉 โพสต์สำเร็จ {success_count} / {total_items}")

if __name__ == "__main__":
    main()

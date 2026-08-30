import os

with open('scratch/main_backup.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
in_main = False
for line in lines:
    if line.startswith('def main():'):
        break
    new_lines.append(line)

new_main = """
def process_broll_mode(tts_engine, voice_gender, f5_ref_voice):
    print("\\n========================================")
    print("🎬 เข้าสู่โหมดสร้างคลิปให้ความรู้ (Auto B-Roll)")
    print("========================================")
    
    csv_path = "data/content_maker.csv"
    if not os.path.exists(csv_path):
        import pandas as pd
        df = pd.DataFrame(columns=["หัวข้อ", "ลิงก์ข้อเสนอ"])
        df.loc[0] = ["5 วิธีลดน้ำหนักแบบไม่เครียด", "https://shope.ee/xxx"]
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        print(f"\\n❌ ไม่พบไฟล์ {csv_path}")
        print(f"✅ บอทได้สร้างไฟล์ต้นแบบไว้ให้แล้ว กรุณาไปกรอก 'หัวข้อ' ในไฟล์ data/content_maker.csv แล้วรันใหม่ครับ")
        return
        
    import pandas as pd
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    print(f"📋 พบหัวข้อในคิวทั้งหมด {len(df)} รายการ\\n")
    
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
            print(f"\\n⏭️ ข้ามคิวที่ {total_items}: หัวข้อ '{topic}' (เคยทำคลิปและโพสต์ไปแล้ว!)")
            continue
            
        print(f"\\n----------------------------------------")
        print(f"🔥 เริ่มคิวที่ {total_items}: สร้างคลิปหัวข้อ '{topic}'")
        print(f"----------------------------------------")
        
        # 1. ให้ AI คิดบทและคีย์เวิร์ด
        from ai_gen import generate_broll_script
        scenes_data = generate_broll_script(topic, voice_gender=voice_gender)
        
        if not scenes_data:
            print("❌ ไม่สามารถสร้างสคริปต์ได้ ข้ามคิวนี้")
            continue
            
        # 2. ตัดต่อวิดีโอ
        from video_maker import make_broll_video
        success = make_broll_video(topic_id, scenes_data, tts_engine=tts_engine, f5_ref_voice=f5_ref_voice, voice_gender=voice_gender)
        
        if not success:
            print("❌ ตัดต่อวิดีโอไม่สำเร็จ ข้ามคิวนี้")
            continue
            
        output_video_path = os.path.join("output", f"broll_{topic_id}.mp4")
        
        # 3. ให้ Gemini สรุปแคปชั่น
        print(f"\\n📝 กำลังให้ Gemini เขียนแคปชั่นโพสต์เฟสบุ๊ค...")
        from ai_gen import generate_script
        model = __import__('google.generativeai').generativeai.GenerativeModel('gemini-1.5-flash')
        prompt_cap = f"เขียนแคปชั่น Facebook ให้ความรู้เรื่อง '{topic}' แนบลิงก์นี้ตอนท้าย: {affiliate_url}"
        try:
            caption = model.generate_content(prompt_cap).text
        except:
            caption = f"คลิปความรู้เรื่อง {topic}\\n\\nสนใจสินค้าคลิก: {affiliate_url}"
            
        # 4. โพสต์ลงเพจ
        print(f"\\n🌐 กำลังโพสต์ลง Facebook...")
        from fb_poster import post_to_facebook
        post_success = post_to_facebook(output_video_path, caption)
        
        if post_success:
            print(f"✅ โพสต์ '{topic}' สำเร็จ!")
            success_count += 1
            save_history(topic_id)
            posted_history.add(topic_id)
        else:
            print(f"❌ โพสต์ล้มเหลว")
            
        if total_items < len(df):
            print(f"\\n⏳ พักหายใจ 1 นาที ก่อนเริ่มหัวข้อถัดไป...")
            import time
            time.sleep(60)
            
    print("\\n========================================")
    print(f"🎉 กระบวนการทั้งหมดเสร็จสิ้น!")
    print(f"📊 สรุปผลงาน: โพสต์สำเร็จ {success_count} / {total_items} รายการ")
    print("========================================")


def main():
    print("========================================")
    print("🚀 เริ่มระบบ Auto Post AI")
    print("========================================\\n")
    
    print("เลือกโหมดการทำงาน:")
    print("1. 🛒 โหมดเซลส์แมน (Shopee Affiliate)")
    print("2. 🎓 โหมดครีเอเตอร์ให้ความรู้ (Auto B-Roll Pexels)")
    
    while True:
        work_mode = input("👉 พิมพ์ 1 หรือ 2: ").strip()
        if work_mode in ['1', '2']:
            break
        print("⚠️ กรุณาพิมพ์ 1 หรือ 2 เท่านั้น")
    print("\\n----------------------------------------")
    
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
    print("\\n----------------------------------------")
    
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
                f5_ref_voice = "alice"
                voice_gender = "female"
                break
            elif voice_input == '2':
                f5_ref_voice = "brian"
                voice_gender = "male"
                break
            elif voice_input == '3':
                f5_ref_voice = input("👉 พิมพ์ Voice ID ของ ElevenLabs: ").strip()
                voice_gender = "female"
                break
            print("⚠️ กรุณาพิมพ์ 1, 2 หรือ 3 เท่านั้น")
            
    print("\\n----------------------------------------")
    
    if work_mode == '2':
        process_broll_mode(tts_engine, voice_gender, f5_ref_voice)
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
        
    print("\\n----------------------------------------")
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
"""

new_lines.append(new_main)

with open('src/main.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Rewrite complete")

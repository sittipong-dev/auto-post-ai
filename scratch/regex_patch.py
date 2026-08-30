import re

with open('src/video_maker.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the fetching part
content = re.sub(
    r'# 2\. ค้นหาและดาวน์โหลดวิดีโอจาก Pexels.*?video_clip = video_clip\.subclipped\(0, duration\)',
    r'''# 2. ค้นหาและดาวน์โหลดวัตถุดิบ (ภาพ หรือ วิดีโอ)
        keyword_th = scene.get("search_keyword_th", scene.get("search_keyword", "คนเอเชีย"))
        keyword_en = scene.get("search_keyword_en", scene.get("search_keyword", "Asian"))
        
        if visual_source == "web_image":
            media_path = os.path.join(temp_dir, f"media_{scene_num}.jpg")
            print(f"   🖼️ กำลังค้นหาภาพจากอินเทอร์เน็ตด้วยคำว่า: '{keyword_th}' ...")
            from web_image_api import search_and_download_image
            success_img = search_and_download_image(keyword_th, media_path)
            if not success_img:
                print(f"   ⚠️ ไม่พบภาพ ลองคำกว้างๆ...")
                search_and_download_image("คนเอเชีย", media_path)
        else:
            media_path = os.path.join(temp_dir, f"video_{scene_num}.mp4")
            print(f"   🎥 กำลังค้นหาวิดีโอ Pexels ด้วยคำว่า: '{keyword_en}' ...")
            videos = search_pexels_video(keyword_en)
            if not videos:
                print(f"   ⚠️ ไม่พบวิดีโอ ลองค้นหาด้วยคำว่า 'Asian' แทน...")
                videos = search_pexels_video("Asian")
            if videos:
                best_link = get_best_video_link(videos[0])
                if best_link:
                    print(f"   ⬇️ กำลังดาวน์โหลดวิดีโอประกอบ...")
                    download_pexels_video(best_link, media_path)
                    
        if not os.path.exists(media_path):
            print(f"   ❌ ดาวน์โหลดวัตถุดิบไม่สำเร็จ ข้ามฉากนี้")
            continue
            
        # 3. ตัดต่อและประกอบร่าง (Audio Sync)
        try:
            print(f"   ✂️ กำลังซิงค์เสียงกับภาพ/วิดีโอ...")
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            
            if visual_source == "web_image":
                from moviepy import ImageClip
                # โหลดภาพนิ่ง ทำ Ken Burns effect (ซูมเข้าช้าๆ)
                img_clip = ImageClip(media_path).with_duration(duration)
                
                # ปรับขนาดภาพให้ครอบคลุม 1080x1920
                if img_clip.h < 1920 or img_clip.w < 1080:
                    img_clip = img_clip.resized(height=1920)
                    if img_clip.w < 1080:
                        img_clip = img_clip.resized(width=1080)
                else:
                    img_clip = img_clip.resized(height=1920)
                    if img_clip.w < 1080:
                        img_clip = img_clip.resized(width=1080)
                    
                # ใส่เอฟเฟกต์ซูม (Ken Burns)
                video_clip = img_clip.with_effects([vfx.Resize(lambda t: 1.0 + 0.1 * (t / duration))])
                
                # ตัดขอบให้เป็น 9:16 ตรงกลาง
                video_clip = video_clip.cropped(x_center=video_clip.w/2, y_center=video_clip.h/2, width=1080, height=1920)
            else:
                video_clip = VideoFileClip(media_path).without_audio()
                # ถ้าวิดีโอสั้นกว่าเสียง ให้ Loop วิดีโอ
                if video_clip.duration < duration:
                    video_clip = video_clip.with_effects([vfx.Loop(duration=duration)])
                else:
                    # ถ้าวิดีโอยาวกว่า ให้ตัดให้พอดีเสียง
                    video_clip = video_clip.subclipped(0, duration)''',
    content, flags=re.DOTALL
)

with open('src/video_maker.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Regex patch applied to video_maker.py")

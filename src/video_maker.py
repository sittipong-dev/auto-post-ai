import os
import sys
import requests
import glob
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
import textwrap

# แก้ปัญหาภาษาไทยใน CMD
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def download_font(font_path):
    if os.path.exists(font_path):
        return True
    print("กำลังดาวน์โหลดฟอนต์ Kanit-Bold.ttf จากระบบ...")
    url = "https://github.com/googlefonts/kanit/raw/main/fonts/Kanit-Bold.ttf"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            with open(font_path, 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f"Error downloading font: {e}")
    return False

def create_video_frame(image_path, text, font_path, output_frame_path):
    # ขนาดวิดีโอ Reels/TikTok (1080x1920)
    W, H = 1080, 1920
    try:
        original = Image.open(image_path).convert("RGB")
        
        # 1. ทำพื้นหลังแบบเบลอ
        bg_height = int(original.height * (W / original.width))
        bg = original.resize((W, bg_height))
        bg = bg.resize((W, H))
        bg = bg.filter(ImageFilter.GaussianBlur(radius=40))
        
        # 2. แปะภาพสินค้าตรงกลาง
        new_h = int(original.height * (W / original.width))
        fg = original.resize((W, new_h))
        fg_y = (H - new_h) // 2
        bg.paste(fg, (0, fg_y))
        
        # 3. วาดข้อความพาดหัว
        draw = ImageDraw.Draw(bg)
        try:
            font = ImageFont.truetype(font_path, 80)
        except Exception:
            font = ImageFont.load_default()
            
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            if len(current_line) + len(word) > 20:
                lines.append(current_line)
                current_line = word
            else:
                current_line += " " + word if current_line else word
        if current_line:
            lines.append(current_line)
            
        if len(lines) == 1 and len(text) > 20:
            lines = textwrap.wrap(text, width=22)
            
        text_y = fg_y - (len(lines) * 110) - 50
        if text_y < 100:
            text_y = 100
            
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_w = bbox[2] - bbox[0]
            x = (W - text_w) / 2
            
            stroke = 4
            draw.text((x-stroke, text_y), line, font=font, fill="black")
            draw.text((x+stroke, text_y), line, font=font, fill="black")
            draw.text((x, text_y-stroke), line, font=font, fill="black")
            draw.text((x, text_y+stroke), line, font=font, fill="black")
            draw.text((x, text_y), line, font=font, fill="#FFE600")
            text_y += 110
            
        bg.save(output_frame_path)
        return True
    except Exception as e:
        print(f"Error creating frame {image_path}: {e}")
        return False

def make_video(product_id, image_mode="slideshow", audio_mode="voice_only", audio_path=None):
    product_dir = os.path.join("assets", "products", product_id)
    if audio_path is None:
        audio_path = os.path.join(product_dir, "voice.mp3")
        if not os.path.exists(audio_path):
            audio_path = os.path.join(product_dir, "voice.wav")
            
    script_path = os.path.join(product_dir, "script.txt")
    font_path = os.path.join("assets", "Kanit-Bold.ttf")
    output_path = os.path.join("output", f"reels_{product_id}.mp4")
    
    ensure_dir("assets")
    ensure_dir("output")
    download_font(font_path)
    
    # ดึงประโยคพาดหัว
    first_sentence = "ของดีบอกต่อ ห้ามพลาด!"
    try:
        if os.path.exists(script_path):
            with open(script_path, "r", encoding="utf-8") as f:
                full_text = f.read().strip()
                parts = full_text.split("!")
                if len(parts) > 1:
                    first_sentence = parts[0] + "!"
                else:
                    first_sentence = full_text[:40] + "..."
    except Exception:
        pass

    # Helper function สำหรับผสมเสียง
    def prepare_audio(base_duration=None):
        from moviepy import AudioFileClip, CompositeAudioClip
        import moviepy.audio.fx as afx
        import random
        
        voice_clip = None
        bgm_clip = None
        
        # 1. โหลดเสียงพูด
        if audio_mode in ["voice_only", "voice_and_bgm"] and os.path.exists(audio_path):
            voice_clip = AudioFileClip(audio_path)
            if base_duration is None:
                base_duration = voice_clip.duration
                
        if base_duration is None:
            base_duration = 15.0 # ค่าเริ่มต้นสำหรับ bgm_only แบบรูปภาพ
            
        # 2. โหลด BGM
        if audio_mode in ["bgm_only", "voice_and_bgm"]:
            bgm_dir = os.path.join("assets", "bgm")
            if os.path.exists(bgm_dir):
                bgms = [os.path.join(bgm_dir, f) for f in os.listdir(bgm_dir) if f.endswith(".mp3")]
                if bgms:
                    bgm_clip = AudioFileClip(random.choice(bgms))
                    if bgm_clip.duration < base_duration:
                        bgm_clip = bgm_clip.with_effects([afx.AudioLoop(duration=base_duration)])
                    bgm_clip = bgm_clip.subclipped(0, base_duration)
                    
                    vol = 0.15 if audio_mode == "voice_and_bgm" else 1.0
                    bgm_clip = bgm_clip.with_effects([afx.MultiplyVolume(vol)])
                    
        # 3. รวมเสียง
        if audio_mode == "voice_and_bgm" and voice_clip and bgm_clip:
            return CompositeAudioClip([bgm_clip, voice_clip]), base_duration
        elif audio_mode == "bgm_only" and bgm_clip:
            if voice_clip: voice_clip.close()
            return bgm_clip, base_duration
        elif voice_clip:
            if bgm_clip: bgm_clip.close()
            return voice_clip, base_duration
            
        return None, base_duration

    # โหมดดูดวิดีโอต้นฉบับ
    if image_mode == "video":
        original_vid_path = os.path.join(product_dir, "original.mp4")
        if not os.path.exists(original_vid_path):
            print("❌ ไม่พบวิดีโอต้นฉบับ (original.mp4) สำหรับทำคลิป")
            return
            
        print("🎬 กำลังส่งให้ MoviePy เรนเดอร์วิดีโอต้นฉบับ...")
        try:
            from moviepy import VideoFileClip, vfx
            
            video_clip = VideoFileClip(original_vid_path).without_audio()
            vid_dur = video_clip.duration
            
            # เตรียมเสียง (ในโหมดวิดีโอ ถ้าไม่มีเสียงพากย์ ให้ยึดความยาวตามวิดีโอ)
            target_aud_dur = None
            if audio_mode != "bgm_only":
                final_audio, aud_dur = prepare_audio(base_duration=None)
            else:
                final_audio, aud_dur = prepare_audio(base_duration=vid_dur)
            
            if not final_audio:
                print("❌ ไม่สามารถโหลดเสียงได้เลย")
                return
                
            print(f"ความยาววิดีโอ: {vid_dur:.1f} วิ | ความยาวเสียง: {aud_dur:.1f} วิ")
            
            if vid_dur < aud_dur:
                video_clip = video_clip.with_effects([vfx.Loop(duration=aud_dur)])
                print("🔄 วิดีโอสั้นกว่าเสียง -> ทำการเล่นวนซ้ำ (Loop) อัตโนมัติ")
            else:
                video_clip = video_clip.subclipped(0, aud_dur)
                print("✂️ วิดีโอยาวกว่าเสียง -> ทำการตัดส่วนเกินทิ้งอัตโนมัติ")
                
            final_video = video_clip.with_audio(final_audio)
            
            final_video.write_videofile(
                output_path, 
                fps=24, 
                codec="libx264", 
                audio_codec="aac",
                logger=None
            )
            print(f"✅ SUCCESS! เรนเดอร์วิดีโอต้นฉบับผสมเสียงเสร็จสมบูรณ์!")
            print(f"ไฟล์อยู่ที่: {output_path}")
            
            video_clip.close()
            final_audio.close()
            return
            
        except Exception as e:
            print(f"❌ Video Maker Error (โหมดวิดีโอ): {e}")
            return
            
    # โหมดปกติ (ภาพเดี่ยว หรือ สไลด์โชว์)
    image_files = sorted(glob.glob(os.path.join(product_dir, "cover_*.jpg")))
    if not image_files and os.path.exists(os.path.join(product_dir, "cover.jpg")):
        image_files = [os.path.join(product_dir, "cover.jpg")]
        
    if image_mode == "single" and image_files:
        image_files = [image_files[0]]
        
    if not image_files:
        print("❌ ไม่พบรูปภาพสำหรับทำวิดีโอ")
        return

    print(f"พบรูปภาพวัตถุดิบทั้งหมด {len(image_files)} รูป")
    
    frame_paths = []
    for idx, img_path in enumerate(image_files):
        out_frame = os.path.join(product_dir, f"frame_{idx}.jpg")
        if create_video_frame(img_path, first_sentence, font_path, out_frame):
            frame_paths.append(out_frame)
            
    if not frame_paths:
        print("❌ สร้างเฟรมภาพไม่สำเร็จเลยสักรูป")
        return

    print("🎬 กำลังส่งให้ MoviePy เรนเดอร์วิดีโอจากภาพ...")
    try:
        from moviepy import ImageClip, concatenate_videoclips
        final_audio, total_duration = prepare_audio(base_duration=None)
        
        if not final_audio:
            print("❌ ไม่สามารถโหลดเสียงได้เลย")
            return
            
        duration_per_image = total_duration / len(frame_paths)
        print(f"คลิปยาว {total_duration:.1f} วิ | โชว์รูปละ {duration_per_image:.1f} วิ")
        
        video_clips = []
        for fpath in frame_paths:
            clip = ImageClip(fpath).with_duration(duration_per_image)
            video_clips.append(clip)
            
        final_video = concatenate_videoclips(video_clips, method="compose")
        final_video = final_video.with_audio(final_audio)
        
        final_video.write_videofile(
            output_path, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac",
            logger=None
        )
        print(f"✅ SUCCESS! เรนเดอร์วิดีโอแบบรูปภาพผสมเสียงเสร็จสมบูรณ์!")
        print(f"ไฟล์อยู่ที่: {output_path}")
        
        final_audio.close()
        
    except Exception as e:
        print(f"❌ Video Maker Error: {e}")

if __name__ == "__main__":
    print("--- เริ่มกระบวนการ Video Maker ---")
    make_video("26962408187")

def make_broll_video(product_id, scenes_data, tts_engine="elevenlabs", f5_ref_voice="", voice_gender="female", visual_source="pexels"):
    import os
    import time
    from pexels_api import search_pexels_video, get_best_video_link, download_pexels_video
    
    # We need TTS generators here to generate voice per scene
    from elevenlabs_gen import generate_voice_elevenlabs
    
    try:
        from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips, vfx
    except ImportError:
        print("❌ กรุณาติดตั้ง moviepy v2: pip install moviepy")
        return False
        
    font_path = os.path.join("assets", "Kanit-Bold.ttf")
    download_font(font_path)
    
    temp_dir = os.path.join("assets", "temp_broll", product_id)
    ensure_dir(temp_dir)
    
    final_clips = []
    
    print(f"🎬 กำลังสร้างวิดีโอแบบแบ่งฉากทั้งหมด {len(scenes_data)} ฉาก...")
    
    for idx, scene in enumerate(scenes_data):
        scene_num = scene.get("scene_number", idx + 1)
        text = scene.get("text", "")
        keyword = scene.get("search_keyword", "Asian")
        
        print(f"\n▶️ [ฉากที่ {scene_num}] กำลังประมวลผล...")
        print(f"   บทพูด: {text[:30]}...")
        print(f"   คีย์เวิร์ดค้นหาภาพ: {keyword}")
        
        # 1. สร้างเสียงพากย์สำหรับฉากนี้
        audio_path = os.path.join(temp_dir, f"voice_{scene_num}.mp3")
        
        if tts_engine == "elevenlabs":
            print(f"   🎙️ กำลังสร้างเสียงด้วย ElevenLabs...")
            success = generate_voice_elevenlabs(text, audio_path, voice_id=f5_ref_voice)
        else:
            # Fallback to Edge TTS if not ElevenLabs
            print(f"   🎙️ กำลังสร้างเสียงด้วย Edge-TTS...")
            from ai_gen import generate_voice
            success = generate_voice(text, audio_path, voice_gender)
            
        if not success or not os.path.exists(audio_path):
            print(f"   ❌ สร้างเสียงไม่สำเร็จ ข้ามฉากนี้")
            continue
            
        # 2. ค้นหาและดาวน์โหลดวัตถุดิบ (ภาพ หรือ วิดีโอ)
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
                    video_clip = video_clip.subclipped(0, duration)
                
            # ใส่เสียงเข้าไปในวิดีโอ
            video_clip = video_clip.with_audio(audio_clip)
            
            # (Optional) ใส่ซับไตเติ้ล
            # In moviepy v2, TextClip syntax is different, keeping it simple for now without text to avoid font bugs
            # We can add text later using CompositeVideoClip
            
            final_clips.append(video_clip)
            print(f"   ✅ ฉากที่ {scene_num} เสร็จสมบูรณ์ (ความยาว {duration:.1f} วิ)")
            
        except Exception as e:
            print(f"   ❌ เกิดข้อผิดพลาดในการตัดต่อฉากที่ {scene_num}: {e}")
            
    if not final_clips:
        print("❌ ไม่สามารถสร้างคลิปได้เลย")
        return False
        
    print(f"\n🌟 กำลังรวมฉากทั้งหมดเข้าด้วยกัน...")
    try:
        final_video = concatenate_videoclips(final_clips, method="compose")
        output_path = os.path.join("output", f"broll_{product_id}.mp4")
        
        # เรนเดอร์วิดีโอ
        final_video.write_videofile(
            output_path, 
            fps=30, 
            codec="libx264",
            audio_codec="aac",
            preset="ultrafast",
            logger=None
        )
        
        print(f"✅✅✅ เรนเดอร์เสร็จสมบูรณ์! ไฟล์อยู่ที่: {output_path}")
        
        # ปิด clips เพื่อคืน memory
        for clip in final_clips:
            clip.close()
        final_video.close()
        
        return True
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการรวมคลิป: {e}")
        return False

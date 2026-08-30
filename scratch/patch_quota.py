import os
import json

def patch_ai_gen():
    with open('src/ai_gen.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    old_start = """def generate_broll_script(topic, tone="สารคดีให้ความรู้", voice_gender="female", max_retries=3):
    """"""สร้างสคริปต์แบบแบ่งฉากสำหรับ Auto B-Roll"""""""""
    
    new_start = """def generate_broll_script(topic, tone="สารคดีให้ความรู้", voice_gender="female", max_retries=3):
    """"""สร้างสคริปต์แบบแบ่งฉากสำหรับ Auto B-Roll""""""
    
    # [เซฟโควต้า] เช็คว่ามีไฟล์ review_script.txt เดิมอยู่ไหม ถ้ามีให้อ่านจากไฟล์เลย
    script_file = os.path.join("data", "review_script.txt")
    if os.path.exists(script_file):
        print("\\n♻️ [เซฟโควต้า] ตรวจพบไฟล์สคริปต์เดิมในเครื่อง กำลังดึงมาใช้โดยไม่เรียก Gemini...")
        scenes_data = []
        current_scene = {}
        with open(script_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("--- ฉากที่"):
                    if current_scene:
                        scenes_data.append(current_scene)
                        current_scene = {}
                    current_scene['scene_number'] = len(scenes_data) + 1
                elif line.startswith("[คำค้นหาภาพ]:"):
                    current_scene['search_keyword'] = line.replace("[คำค้นหาภาพ]:", "").strip()
                elif line.startswith("[บทพูด]:"):
                    current_scene['text'] = line.replace("[บทพูด]:", "").strip()
        if current_scene:
            scenes_data.append(current_scene)
        if scenes_data:
            return scenes_data"""
            
    if old_start in content:
        content = content.replace(old_start, new_start)
        with open('src/ai_gen.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Patched ai_gen.py to save quota.")
    else:
        print("Could not find insertion point.")

patch_ai_gen()

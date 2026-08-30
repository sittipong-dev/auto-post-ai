import os

with open('src/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_block = """        if not scenes_data:
            print("❌ ไม่สามารถสร้างสคริปต์ได้ ข้ามคิวนี้")
            continue"""

new_block = """        if not scenes_data:
            print("❌ ไม่สามารถสร้างสคริปต์ได้ ข้ามคิวนี้")
            continue
            
        # --- ระบบผู้กำกับตรวจบท (Script Review) ---
        print("\\n========================================")
        print("📝 สคริปต์ที่ Gemini คิดมาให้:")
        for idx, sc in enumerate(scenes_data):
            print(f"🎬 ฉากที่ {idx+1}: [{sc.get('search_keyword', 'Asian')}] {sc.get('text', '')}")
        print("========================================")
        
        edit_choice = input("\\n👉 ต้องการแก้ไขบทพูดหรือคีย์เวิร์ดภาพไหม? (y = แก้ไข / n = ไม่แก้ ลุยต่อเลย): ").strip().lower()
        if edit_choice == 'y':
            script_file = os.path.join("data", "review_script.txt")
            with open(script_file, "w", encoding="utf-8") as f:
                for idx, sc in enumerate(scenes_data):
                    f.write(f"--- ฉากที่ {idx+1} ---\\n")
                    f.write(f"[คำค้นหาภาพ]: {sc.get('search_keyword', '')}\\n")
                    f.write(f"[บทพูด]: {sc.get('text', '')}\\n\\n")
            
            print(f"\\n⏳ โปรแกรมกำลังเปิดหน้าต่าง Notepad ขึ้นมา...")
            print(f"⚠️ กรุณาแก้บทใน Notepad -> กด File -> Save -> แล้วกลับมากด Enter ที่หน้าจอดำนี้ครับ")
            os.system(f'notepad "{script_file}"')
            input("\\n✅ เซฟใน Notepad เสร็จแล้วใช่ไหมครับ? กด Enter 1 ครั้งเพื่อสร้างวิดีโอต่อได้เลย... ")
            
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
        # --- จบระบบผู้กำกับตรวจบท ---"""

new_content = content.replace(old_block, new_block)

with open('src/main.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Injected script review feature.")

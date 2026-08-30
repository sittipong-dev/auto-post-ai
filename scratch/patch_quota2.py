with open('src/ai_gen.py', 'r', encoding='utf-8') as f:
    content = f.read()

import re
content = re.sub(
    r'(def generate_broll_script.*?:[\r\n]+\s+.*[\r\n]+)', 
    r'\1    # [เซฟโควต้า]\n    script_file = os.path.join("data", "review_script.txt")\n    if os.path.exists(script_file):\n        print("\\n♻️ [เซฟโควต้า] นำสคริปต์เดิมมาใช้...")\n        scenes_data = []\n        current_scene = {}\n        with open(script_file, "r", encoding="utf-8") as f:\n            for line in f:\n                line = line.strip()\n                if line.startswith("--- ฉากที่"):\n                    if current_scene: scenes_data.append(current_scene)\n                    current_scene = {"scene_number": len(scenes_data) + 1}\n                elif line.startswith("[คำค้นหาภาพ]:"): current_scene["search_keyword"] = line.replace("[คำค้นหาภาพ]:", "").strip()\n                elif line.startswith("[บทพูด]:"): current_scene["text"] = line.replace("[บทพูด]:", "").strip()\n        if current_scene: scenes_data.append(current_scene)\n        if scenes_data: return scenes_data\n\n',
    content, 
    count=1
)

with open('src/ai_gen.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Patched.")

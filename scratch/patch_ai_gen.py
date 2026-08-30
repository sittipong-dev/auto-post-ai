import re

with open('src/ai_gen.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the prompt section for broll
old_prompt = """  4. กฎเหล็ก: คีย์เวิร์ดค้นหาภาพ 'ต้อง' มีคำว่า "Asian" หรือ "Thailand" ประกอบอยู่ด้วยเสมอ เพื่อให้ภาพออกมาเป็นคนเอเชีย (เช่น "Asian doctor", "Thailand street food", "Asian family eating")
  5. ห้ามมีคำอธิบายอื่นๆ ให้ส่งผลลัพธ์เป็น JSON Array เท่านั้น โดยมีโครงสร้างดังนี้:
  
  [
    {
      "scene_number": 1,
      "text": "บทพูดของฉากที่ 1",
      "search_keyword": "Asian doctor"
    },"""

new_prompt = """  4. กฎเหล็ก: คุณต้องคิดคำค้นหาภาพ 2 รูปแบบคือ (1) แบบภาษาไทยเจาะจง และ (2) แบบภาษาอังกฤษที่มีคำว่า Asian เพื่อให้ภาพออกมาเป็นคนเอเชีย
  5. ห้ามมีคำอธิบายอื่นๆ ให้ส่งผลลัพธ์เป็น JSON Array เท่านั้น โดยมีโครงสร้างดังนี้:
  
  [
    {
      "scene_number": 1,
      "text": "บทพูดของฉากที่ 1",
      "search_keyword_th": "หมอผู้หญิงคนไทยกำลังตรวจคนไข้",
      "search_keyword_en": "Asian female doctor hospital"
    },"""

content = content.replace(old_prompt, new_prompt)

# Also update where the JSON is parsed into the text file!
old_parse = """                f.write(f"[คำค้นหาภาพ]: {sc.get('search_keyword', '')}\\n")"""
new_parse = """                f.write(f"[คำค้นหาภาพ (ไทย)]: {sc.get('search_keyword_th', '')}\\n")
                f.write(f"[Search Keyword (ENG)]: {sc.get('search_keyword_en', '')}\\n")"""
content = content.replace(old_parse, new_parse)

# Update the cache reader (เซฟโควต้า) logic to support dual keywords
old_cache = """                elif line.startswith("[คำค้นหาภาพ]:"): current_scene["search_keyword"] = line.replace("[คำค้นหาภาพ]:", "").strip()"""
new_cache = """                elif line.startswith("[คำค้นหาภาพ (ไทย)]"): current_scene["search_keyword_th"] = line.split(":", 1)[1].strip()
                elif line.startswith("[Search Keyword (ENG)]"): current_scene["search_keyword_en"] = line.split(":", 1)[1].strip()"""
content = content.replace(old_cache, new_cache)

with open('src/ai_gen.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Patched ai_gen.py for dual keywords")

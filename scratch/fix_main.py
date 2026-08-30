content = '''--- ฉากที่ 1 ---
[คำค้นหาภาพ (ไทย)]: หมอผู้หญิงคนไทยกำลังให้คำปรึกษา
[Search Keyword (ENG)]: Asian female doctor
[บทพูด]: คุณกำลังเสี่ยงเป็นเบาหวานโดยไม่รู้ตัวอยู่หรือเปล่าครับ? โรคนี้มักเริ่มต้นอย่างเงียบๆ แต่ร่างกายมักจะส่งสัญญาณเตือนออกมาเสมอครับ

--- ฉากที่ 2 ---
[คำค้นหาภาพ (ไทย)]: ภาพคนตาพร่ามัว มองไม่ค่อยชัด
[Search Keyword (ENG)]: blurred vision
[บทพูด]: สัญญาณแรกคือ เริ่มปัสสาวะบ่อยผิดปกติ โดยเฉพาะตอนกลางคืน และรู้สึกคอแห้ง หิวน้ำตลอดเวลาแม้จะดื่มน้ำไปเยอะแล้วก็ตามนะครับ

--- ฉากที่ 3 ---
[คำค้นหาภาพ (ไทย)]: ผู้ป่วยคนไทยมีอาการอ่อนเพลีย เหนื่อยล้า
[Search Keyword (ENG)]: tired Asian person
[บทพูด]: สัญญาณต่อมาคือ ทานอาหารเยอะขึ้นแต่น้ำหนักตัวกลับลดลงอย่างรวดเร็ว พร้อมกับมีอาการอ่อนเพลีย เหนื่อยง่ายตลอดวันครับ

--- ฉากที่ 4 ---
[คำค้นหาภาพ (ไทย)]: แผลที่เท้าหายช้า
[Search Keyword (ENG)]: diabetic wound healing
[บทพูด]: นอกจากนี้ หากเริ่มมีอาการตาพร่ามัวมองเห็นไม่ชัด หรือเป็นแผลแล้วหายช้าผิดปกติ นี่ก็เป็นสัญญาณเตือนที่สำคัญมากเช่นกันครับ

--- ฉากที่ 5 ---
[คำค้นหาภาพ (ไทย)]: เครื่องเจาะน้ำตาลปลายนิ้วเบาหวาน
[Search Keyword (ENG)]: blood sugar test
[บทพูด]: หากคุณมีสัญญาณเตือนเหล่านี้ อย่าปล่อยทิ้งไว้นะครับ แนะนำให้รีบไปตรวจระดับน้ำตาลในเลือดที่โรงพยาบาลเพื่อความมั่นใจครับ
'''

with open('data/review_script.txt', 'w', encoding='utf-8') as f:
    f.write(content)
print("Recreated review_script.txt")

import re
with open('src/main.py', 'r', encoding='utf-8') as f:
    main_content = f.read()

old_print = '''        print("📝 สคริปต์ที่ Gemini คิดมาให้:")
        for idx, sc in enumerate(scenes_data):
            print(f"🎬 ฉากที่ {idx+1}: [{sc.get('search_keyword', 'Asian')}] {sc.get('text', '')}")
        print("========================================")'''
new_print = '''        print("📝 สคริปต์ที่ Gemini คิดมาให้:")
        for idx, sc in enumerate(scenes_data):
            kw_th = sc.get('search_keyword_th', 'ไม่มีคีย์เวิร์ด')
            kw_en = sc.get('search_keyword_en', 'Asian')
            print(f"🎬 ฉากที่ {idx+1}: [ไทย: {kw_th} | ENG: {kw_en}] {sc.get('text', '')}")
        print("========================================")'''
main_content = main_content.replace(old_print, new_print)

old_write = '''                    f.write(f"[คำค้นหาภาพ]: {sc.get('search_keyword', '')}\\n")'''
new_write = '''                    f.write(f"[คำค้นหาภาพ (ไทย)]: {sc.get('search_keyword_th', '')}\\n")
                    f.write(f"[Search Keyword (ENG)]: {sc.get('search_keyword_en', '')}\\n")'''
main_content = main_content.replace(old_write, new_write)

with open('src/main.py', 'w', encoding='utf-8') as f:
    f.write(main_content)
print("Patched main.py to fix script review overwrite.")

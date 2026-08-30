import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv

try: sys.stdout.reconfigure(encoding='utf-8')
except: pass

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

prompt = """
คุณคือคนเขียนสคริปต์เสียง
จงเขียนสคริปต์ขายของ 1 ประโยค (ป้ายยากล้องวงจรปิด)
กติกา: ให้เขียนเป็น "คำอ่านภาษาไทยแบบตรงมาตราตัวสะกด" ทั้งหมด เพื่อให้หุ่นยนต์อ่านง่ายที่สุด
(ตัวอย่างเช่น: "สวัสดีครับ กล้องสมาร์ทโฮม" -> "สะ หวัด ดี คับ กล้อง สมาต โฮม")
เขียนแบบแยกพยางค์ได้เลย แต่ไม่ต้องใส่เครื่องหมายใดๆ
สคริปต์ของคุณ:
"""
model = genai.GenerativeModel('gemini-3.5-flash-lite')
response = model.generate_content(prompt)
print(response.text)

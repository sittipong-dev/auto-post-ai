import os
import sys

# แก้ปัญหาพิมพ์ภาษาไทยใน console Windows
try: sys.stdout.reconfigure(encoding='utf-8')
except: pass

# เพิ่ม path ให้ import โมดูลจาก src/ ได้
sys.path.append(os.path.abspath("src"))

from scraper import get_shopee_product_info
from main import process_single_product

link = "https://s.shopee.co.th/5foJ0Q4FR1"
print(f"กำลังดึงข้อมูลจากลิงก์: {link}")

info = get_shopee_product_info(link)
if not info:
    print("❌ ดึงข้อมูลไม่สำเร็จ")
    sys.exit(1)

product_name = info['product_name']
price = info['price']
product_id = info['product_id']
long_url = info['long_url']
affiliate_url = link

print(f"สินค้า: {product_name}")
print(f"ราคา: {price}")
print(f"ID: {product_id}")

# ลบวิดีโอผลลัพธ์เก่าทิ้งถ้ามี
out_vid = os.path.join("output", f"reels_{product_id}.mp4")
if os.path.exists(out_vid):
    os.remove(out_vid)

# ลบสคริปต์เก่าทิ้งเพื่อบังคับให้ Gemini แต่งใหม่
script_file = os.path.join("assets", "products", product_id, "script.txt")
if os.path.exists(script_file):
    os.remove(script_file)

print("\n🚀 เริ่มสร้างวิดีโอแบบเต็มระบบด้วยเสียง female_cute (สายป้ายยา)...")
result = process_single_product(
    product_id=product_id,
    product_name=product_name,
    price=price,
    product_url=long_url,
    affiliate_url=affiliate_url,
    image_mode="video",
    voice_gender="female",
    tone="ตื่นเต้น ป้ายยาหนักๆ ให้รีบซื้อทันที",
    audio_mode="voice_only",
    tts_engine="f5",
    f5_ref_voice="female_cute.wav"
)

if result:
    print(f"\n🎉 วิดีโอเสร็จสมบูรณ์! ลองไปดูไฟล์ที่: {out_vid}")
else:
    print("\n❌ สร้างวิดีโอไม่สำเร็จ")

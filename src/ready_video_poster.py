import os
import sys
import time
import pandas as pd
from scraper import resolve_affiliate_link
from ai_gen import generate_video_caption
from fb_poster import post_to_facebook

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def clean_path(path_str):
    path_str = path_str.strip()
    # ตัด & ที่ PowerShell ชอบแถมมาเวลาลากไฟล์
    if path_str.startswith("& "):
        path_str = path_str[2:].strip()
    if path_str.startswith('"') and path_str.endswith('"'):
        path_str = path_str[1:-1]
    if path_str.startswith("'") and path_str.endswith("'"):
        path_str = path_str[1:-1]
    return path_str

def process_single_ready_video(video_path, affiliate_url, tone="ตื่นเต้น ป้ายยาหนักๆ ให้รีบซื้อทันที"):
    video_path = clean_path(video_path)
    
    if not os.path.exists(video_path):
        print(f"❌ ไม่พบไฟล์วิดีโอที่: {video_path}")
        return False
        
    print("\n[1/3] 🔍 กำลังดึงข้อมูลสินค้าจาก Shopee...")
    info = resolve_affiliate_link(affiliate_url)
    
    if not info:
        print("❌ ดึงข้อมูลไม่สำเร็จ หรือสินค้านี้โดนลบไปแล้ว")
        return False
        
    product_name = info.get('title', 'สินค้าขายดี')
    product_desc = info.get('desc', 'ดูรายละเอียดเพิ่มเติมคลิกที่ลิงก์')
    
    print(f"✅ พบสินค้า: {product_name}")
    print("\n[2/3] 🧠 ให้ AI (Gemini) เขียนแคปชั่นโพสต์...")
    
    caption = generate_video_caption(product_name, product_desc, affiliate_url, tone)
    
    print("\n✅ แคปชั่นที่ได้:")
    print("--------------------------------------------------")
    print(caption)
    print("--------------------------------------------------")
    
    print("\n[3/3] 📤 กำลังอัปโหลดวิดีโอลง Facebook...")
    
    if post_to_facebook(video_path, caption):
        print("🎉 โพสต์วิดีโอสำเร็จ!")
        return True
    else:
        print("❌ เกิดข้อผิดพลาดในการโพสต์")
        return False

def run_ready_video_single():
    print("\n--- 🎬 โหมดโพสต์ทีละคลิป (Single Post) ---")
    
    affiliate_url = input("🔗 วางลิงก์ Shopee (Affiliate): ").strip()
    if not affiliate_url:
        print("❌ ยกเลิกการโพสต์")
        return
        
    print("\n📂 ลากไฟล์วิดีโอ (.mp4) มาวางในหน้าต่างนี้ แล้วกด Enter:")
    video_path = input("👉 ไฟล์วิดีโอ: ").strip()
    
    if not video_path:
        print("❌ ยกเลิกการโพสต์")
        return
        
    print("\nเลือกสไตล์การเขียนแคปชั่น (Tone):")
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
        
    process_single_ready_video(video_path, affiliate_url, tone)

def run_ready_video_batch():
    print("\n--- 📦 โหมดโพสต์แบบเหมาๆ (Batch Post) ---")
    data_dir = "data"
    ensure_dir(data_dir)
    csv_path = os.path.join(data_dir, "ready_to_post.csv")
    videos_dir = os.path.join("assets", "ready_videos")
    ensure_dir(videos_dir)
    
    if not os.path.exists(csv_path):
        print(f"\n⚠️ ไม่พบไฟล์ {csv_path}")
        print("จอมกำลังสร้างไฟล์ต้นแบบให้ครับ...")
        
        df_template = pd.DataFrame({
            "ชื่อวิดีโอ (รวมนามสกุล)": ["video1.mp4", "video2.mp4"],
            "ลิงก์ Shopee": ["https://s.shopee.co.th/xxx", "https://s.shopee.co.th/yyy"]
        })
        df_template.to_csv(csv_path, index=False, encoding="utf-8-sig")
        
        print(f"✅ สร้างไฟล์สำเร็จ!")
        print(f"👉 กรุณาไปที่โฟลเดอร์ '{data_dir}' แล้วเปิดไฟล์ 'ready_to_post.csv' เพื่อใส่ข้อมูล")
        print(f"👉 และอย่าลืมนำไฟล์วิดีโอทั้งหมด ไปใส่ไว้ในโฟลเดอร์ '{videos_dir}' ด้วยนะครับ")
        return
        
    try:
        df = pd.read_csv(csv_path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv(csv_path, encoding="cp874")
        
    if "ชื่อวิดีโอ (รวมนามสกุล)" not in df.columns or "ลิงก์ Shopee" not in df.columns:
        print("❌ ไฟล์ CSV ไม่ถูกต้อง! ต้องมีคอลัมน์ 'ชื่อวิดีโอ (รวมนามสกุล)' และ 'ลิงก์ Shopee'")
        return
        
    print(f"\nพบข้อมูลทั้งหมด {len(df)} รายการ")
    success_count = 0
    
    for index, row in df.iterrows():
        video_name = str(row["ชื่อวิดีโอ (รวมนามสกุล)"]).strip()
        affiliate_url = str(row["ลิงก์ Shopee"]).strip()
        
        if not video_name or video_name == 'nan' or not affiliate_url or affiliate_url == 'nan':
            continue
            
        video_path = os.path.join(videos_dir, video_name)
        
        print(f"\n========================================")
        print(f"▶️ กำลังประมวลผลคลิปที่ {index+1}: {video_name}")
        
        if process_single_ready_video(video_path, affiliate_url):
            success_count += 1
            # พัก 5 นาทีถ้ายังไม่หมด
            if index < len(df) - 1:
                print("\n⏳ พัก 5 นาทีก่อนโพสต์คลิปถัดไป (ป้องกันการโดนบล็อก)...")
                for i in range(300, 0, -1):
                    mins, secs = divmod(i, 60)
                    sys.stdout.write(f"\rรออีก {mins:02d}:{secs:02d} นาที")
                    sys.stdout.flush()
                    time.sleep(1)
                print()
                
    print(f"\n🎉 สรุปผล: โพสต์สำเร็จ {success_count}/{len(df)} คลิป")

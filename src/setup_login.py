import os
import time
from playwright.sync_api import sync_playwright

def setup_profiles():
    # เปลี่ยนชื่อโปรไฟล์ใหม่เพื่อป้องกันปัญหาล็อกหรือไฟล์ค้าง
    PROFILE_DIR = os.path.join(os.getcwd(), "data", "browser_profile_new")
    
    print("\n==========================================")
    print("[INFO] เปิดเบราว์เซอร์สำหรับล็อกอินครั้งแรก...")
    print(f"[INFO] คุกกี้จะถูกบันทึกไว้ที่: {PROFILE_DIR}")
    print("==========================================\n")
    
    try:
        with sync_playwright() as p:
            print("[STEP 1] กำลังเปิด Facebook... กรุณาล็อกอินให้เรียบร้อย")
            
            context = p.chromium.launch_persistent_context(
                user_data_dir=PROFILE_DIR,
                headless=False,
                channel="chrome",
                args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
                viewport={'width': 1280, 'height': 720}
            )
            
            page1 = context.pages[0]
            page1.goto("https://www.facebook.com/")
            
            print("[STEP 2] กำลังเปิด Shopee Affiliate แท็บใหม่... กรุณาล็อกอินให้เรียบร้อย")
            page2 = context.new_page()
            page2.goto("https://affiliate.shopee.co.th/")
            
            print("\n*** สิ่งที่คุณต้องทำ ***")
            print("1. ล็อกอินเข้า Facebook ในแท็บแรก")
            print("2. ล็อกอินเข้า Shopee Affiliate ในแท็บที่สอง")
            print("3. เมื่อเสร็จทั้ง 2 เว็บ ให้กดกากบาท (X) ปิดเบราว์เซอร์ได้เลยครับ")
            print("\nกำลังรอให้คุณปิดเบราว์เซอร์...")
            
            # รอจนกว่า User จะปิดเบราว์เซอร์ด้วยตัวเอง
            while len(context.pages) > 0:
                time.sleep(1)
                
            print("\n✅ บันทึกโปรไฟล์เสร็จสมบูรณ์! คุณสามารถรันบอทหลัก (main.py) ได้เลย")
            
    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    setup_profiles()

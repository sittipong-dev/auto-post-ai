from playwright.sync_api import sync_playwright
import os
import sys

# บังคับใช้ UTF-8 เพื่อแก้ปัญหาการแสดงผลภาษาไทยบน Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

PROFILE_DIR = os.path.join(os.getcwd(), "data", "browser_profile")

def setup_login():
    print("[INFO] เปิดเบราว์เซอร์สำหรับล็อกอินครั้งแรก...")
    print(f"[INFO] คุกกี้จะถูกบันทึกไว้ที่: {PROFILE_DIR}")
    
    with sync_playwright() as p:
        # เปิดเบราว์เซอร์แบบให้คนมองเห็น (headless=False) และจำโปรไฟล์
        context = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        # ปกติ persistent_context จะมีหน้าต่างเปล่ามาให้ 1 หน้า
        page_fb = context.pages[0]
        
        print("\n[STEP 1] กำลังเปิด Facebook... กรุณาล็อกอินให้เรียบร้อย")
        page_fb.goto("https://www.facebook.com/")
        
        print("[STEP 2] กำลังเปิด Shopee Affiliate แท็บใหม่... กรุณาล็อกอินให้เรียบร้อย")
        page_shopee = context.new_page()
        page_shopee.goto("https://affiliate.shopee.co.th/")
        
        print("\n*** สิ่งที่คุณต้องทำ ***")
        print("1. ล็อกอินเข้า Facebook ในแท็บแรก")
        print("2. ล็อกอินเข้า Shopee Affiliate ในแท็บที่สอง")
        print("3. เมื่อเสร็จทั้ง 2 เว็บ ให้กดกากบาท (X) ปิดเบราว์เซอร์ได้เลยครับ")
        print("\nกำลังรอให้คุณปิดเบราว์เซอร์...")
        
        # วนลูปเช็คว่ายังมีหน้าต่างเปิดอยู่ไหม
        try:
            while len(context.pages) > 0:
                context.pages[0].wait_for_timeout(2000)
        except Exception:
            pass 
        
        print("[SUCCESS] บันทึกคุกกี้เรียบร้อยแล้ว!")

if __name__ == "__main__":
    setup_login()

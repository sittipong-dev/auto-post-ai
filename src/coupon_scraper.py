import os
import time
from playwright.sync_api import sync_playwright

def scrape_coupon_page(url):
    print(f"\n🕵️‍♂️ กำลังส่งบอทไปหน้าเว็บ: {url}")
    
    profile_dir = os.path.abspath(os.path.join("data", "shopee_profile"))
    os.makedirs(profile_dir, exist_ok=True)
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=profile_dir,
                headless=False,
                viewport={'width': 1280, 'height': 720},
                args=['--disable-blink-features=AutomationControlled']
            )
            
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded")
            print("⏳ กำลังโหลดส่วนลด (10 วินาที)...")
            time.sleep(3)
            
            # Check if login is required
            if "login" in page.url:
                print("\n⚠️ Shopee บังคับให้ล็อกอิน!")
                print("🛑 กรุณาล็อกอิน Shopee ในหน้าต่างบอทที่เปิดอยู่ให้เสร็จ")
                print("🛑 เมื่อล็อกอินเสร็จแล้ว ให้กด Enter ที่นี่เพื่อไปต่อ...")
                input("👉 กด Enter เมื่อล็อกอินสำเร็จ...")
                # After login, go back to the original URL
                page.goto(url, wait_until="domcontentloaded")
                time.sleep(5)
                
            page.evaluate("window.scrollTo(0, 1500);")
            time.sleep(3)
            page.evaluate("window.scrollTo(0, 3000);")
            time.sleep(2)
            
            print("📝 กำลังดูดข้อความออกมา...")
            raw_text = page.locator("body").inner_text()
            
            browser.close()
            
            if len(raw_text) < 50:
                print("❌ ดึงข้อความได้น้อยมาก อาจจะติดระบบกันบอท")
                return None
                
            print(f"✅ ดูดสำเร็จ! ได้ข้อความมา {len(raw_text)} ตัวอักษร")
            return raw_text
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการดูดเว็บ: {e}")
        return None

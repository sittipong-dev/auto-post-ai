import os
import sys
import time
import re
from playwright.sync_api import sync_playwright

# แก้ปัญหาภาษาไทยใน CMD
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def post_to_facebook(video_path, caption, affiliate_url=None):
    profile_dir = os.path.abspath(os.path.join("data", "browser_profile"))
    
    if not os.path.exists(profile_dir):
        print("❌ ไม่พบโฟลเดอร์คุกกี้ (Profile) กรุณารัน setup_login.py ก่อนครับ")
        return False
        
    print("🤖 กำลังปลุกบอทนักโพสต์ (รันเบื้องหลังแบบโหมดล่องหน)...")
    
    try:
        with sync_playwright() as p:
            # รันแบบมองไม่เห็น (Headless=True)
            browser = p.chromium.launch_persistent_context(
                user_data_dir=profile_dir,
                headless=True,
                viewport={'width': 1920, 'height': 1080},
                args=['--disable-blink-features=AutomationControlled']
            )
            
            page = browser.new_page()
            
            print("กำลังตรวจสอบสถานะคุกกี้ Facebook...")
            page.goto("https://www.facebook.com/", wait_until="domcontentloaded")
            time.sleep(5)
            
            if "login" in page.url or "checkpoint" in page.url:
                print("❌ คุกกี้หมดอายุ กรุณารัน src/setup_login.py เพื่อล็อกอินใหม่อีกครั้ง")
                browser.close()
                return False
                
            print("✅ ยืนยันคุกกี้ใช้งานได้!")
            
            print("กำลังตรงไปที่หน้า Facebook Reels...")
            page.goto("https://www.facebook.com/reels/create", wait_until="domcontentloaded")
            time.sleep(5)
            
            # 1. อัปโหลดวิดีโอ
            print(f"กำลังอัปโหลดไฟล์วิดีโอ: {os.path.basename(video_path)}")
            file_input = page.locator('input[type="file"]')
            if file_input.count() > 0:
                file_input.first.set_input_files(video_path)
                print("✅ ใส่ไฟล์วิดีโอเข้าระบบสำเร็จ! รอกระบวนการอัปโหลดของ Facebook 60 วินาที...")
                time.sleep(60)
            else:
                print("❌ ไม่พบปุ่มอัปโหลด หยุดการทำงาน")
                browser.close()
                return False

            # 2. กดปุ่ม Next 2 ครั้ง (ผ่านหน้า Trim)
            print("กำลังกดปุ่ม ถัดไป (Next)...")
            for _ in range(2):
                try:
                    next_btn = page.get_by_role("button", name=re.compile(r"Next|ถัดไป", re.IGNORECASE)).last
                    if next_btn.is_visible():
                        next_btn.click()
                        time.sleep(3)
                except Exception:
                    pass
            
            # 3. พิมพ์แคปชั่น
            print("กำลังพิมพ์แคปชั่น...")
            try:
                textbox = page.locator('div[contenteditable="true"]').first
                textbox.fill(caption)
                time.sleep(2)
            except Exception as e:
                print(f"⚠️ หาช่องแคปชั่นไม่เจอ (Facebook อาจเปลี่ยนโครงสร้าง): {e}")

            # 4. กดปุ่ม Publish
            print("กำลังกดปุ่ม เผยแพร่ (Publish)...")
            try:
                publish_btn = page.get_by_role("button", name=re.compile(r"Publish|เผยแพร่|Post|โพสต์|Share|แชร์", re.IGNORECASE)).last
                publish_btn.click(timeout=90000)
                print("✅ สั่งเผยแพร่แล้ว! ระบบกำลังประมวลผลคลิป...")
                
                # รอให้ Facebook ประมวลผล Reels จนเสร็จก่อนไปคอมเมนต์
                print("⏳ รอเฟสบุ๊คอัปโหลดวิดีโอ 60 วินาที (เพื่อให้คลิปโผล่บนหน้าเพจ)...")
                time.sleep(60)
                
            except Exception as e:
                print(f"❌ หาปุ่ม Publish ไม่เจอ: {e}")
                browser.close()
                return False

            # 5. ไปหน้าโปรไฟล์และปักหมุดคอมเมนต์
            if affiliate_url:
                print("กำลังวิ่งไปที่หน้าโปรไฟล์เพื่อคอมเมนต์ปักตะกร้า...")
                page.goto("https://www.facebook.com/me", wait_until="domcontentloaded")
                
                # วนลูปรอจนกว่าคลิปจะโผล่ (เพราะคลิปจากการดูดวิดีโอไฟล์ใหญ่กว่ารูปภาพ เฟสบุ๊คประมวลผลนานกว่า 60 วินาที)
                max_retries = 5
                for attempt in range(max_retries):
                    time.sleep(10) # รอโหลดหน้า
                    page.keyboard.press("PageDown")
                    time.sleep(5)
                    
                    print(f"กำลังหาช่องพิมพ์คอมเมนต์บนหน้าไทม์ไลน์ (รอบที่ {attempt + 1}/{max_retries})...")
                    comment_box = page.get_by_role("textbox", name=re.compile(r"comment|ความคิดเห็น", re.IGNORECASE)).first
                    if not comment_box.is_visible():
                        comment_box = page.locator('div[contenteditable="true"]').first
                        
                    if comment_box.is_visible():
                        try:
                            comment_text = f"📍 พิกัดสั่งซื้อราคาพิเศษ คลิกตรงนี้เลยจ้า: {affiliate_url}"
                            comment_box.fill(comment_text, timeout=15000)
                            time.sleep(2)
                            page.keyboard.press("Enter")
                            print("✅ โพสต์คอมเมนต์ Affiliate สำเร็จแล้ว!")
                            time.sleep(5)
                            break # หลุดจากลูปเมื่อคอมเมนต์สำเร็จ
                        except Exception as e:
                            print(f"⚠️ พิมพ์คอมเมนต์ไม่ได้: {e}")
                    else:
                        print("⏳ คลิปอาจจะยังประมวลผลไม่เสร็จ กำลังรีเฟรชหน้าใหม่...")
                        page.reload(wait_until="domcontentloaded")
                else:
                    print("❌ รอมาหลายนาทีแล้วคลิปยังไม่ขึ้นบนหน้าไทม์ไลน์ เลยไม่ได้คอมเมนต์ครับ")
            
            # ถ่ายรูปหน้าโปรไฟล์มาให้ดูว่าโพสต์ขึ้นหรือยัง
            ensure_dir("scratch")
            screenshot_path = os.path.abspath(os.path.join("scratch", "fb_profile_check.png"))
            page.screenshot(path=screenshot_path)
            print(f"📸 ถ่ายรูปหน้าโปรไฟล์เช็คโพสต์ล่าสุดเก็บไว้ที่: {screenshot_path}")

            print("🎉 กระบวนการโพสต์ Facebook เสร็จสมบูรณ์ ปิดเบราว์เซอร์...")
            browser.close()
            return True
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดร้ายแรง: {e}")
        return False

if __name__ == "__main__":
    video_file = os.path.abspath(os.path.join("output", "reels_26962408187.mp4"))
    caption_text = "พาวเวอร์แบงก์ชาร์จเร็ว พกพาง่าย #พาวเวอร์แบงก์ #ของดีบอกต่อ #ShopeeTH"
    fake_url = "https://shope.ee/xxxxx"
    
    print("--- 🌐 เริ่มกระบวนการ Facebook Auto Poster ---")
    if os.path.exists(video_file):
        post_to_facebook(video_file, caption_text, fake_url)
    else:
        print(f"❌ ไม่พบไฟล์วิดีโอ: {video_file} (รัน video_maker.py หรือยัง?)")

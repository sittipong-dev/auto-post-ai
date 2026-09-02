import os
import time
import re
from playwright.sync_api import sync_playwright
from scraper import resolve_affiliate_link

def clean_dead_links(page_url, scroll_limit=15):
    print(f"\n🧹 เริ่มโหมดทำความสะอาดเพจ (ตรวจสอบ {scroll_limit} ครั้ง)")
    profile_dir = os.path.abspath(os.path.join("data", "browser_profile"))
    
    if not os.path.exists(profile_dir):
        print("❌ ไม่พบโปรไฟล์ Facebook กรุณารันเมนูตั้งค่าล็อกอินก่อน (setup_login.py)")
        return False
        
    with sync_playwright() as p:
        print("🚀 กำลังเปิดเบราว์เซอร์...")
        browser = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            headless=False,
            viewport={"width": 1280, "height": 720},
            args=["--disable-notifications", "--disable-infobars"]
        )
        
        page = browser.new_page()
        print(f"🌐 กำลังไปยังหน้าเพจ: {page_url}")
        page.goto(page_url)
        time.sleep(5)
        
        # Check login status
        if "login" in page.url:
            print("❌ ดูเหมือนจะยังไม่ได้ล็อกอิน กรุณาล็อกอินก่อน")
            browser.close()
            return False
            
        print("🔍 กำลังสแกนโพสต์ในเพจ...")
        
        # ค้นหาโพสต์ (Facebook มักใช้ role="article" สำหรับโพสต์แต่ละอัน)
        scanned_urls = set()
        deleted_count = 0
        
        for scroll in range(scroll_limit):
            posts = page.locator('div[role="article"]')
            count = posts.count()
            print(f"👀 เจอโครงสร้างโพสต์บนหน้าจอ {count} โพสต์ (รอบที่ {scroll+1})")
            
            for i in range(count):
                try:
                    post = posts.nth(i)
                    if not post.is_visible(): continue
                        
                    post_text = post.inner_text()
                    
                    # ปรับ Regex ให้จับลิงก์ที่ไม่มี https:// ด้วย (เพราะเฟสบุ๊คมักจะซ่อน https)
                    links = re.findall(r'(?:https://)?(s\.shopee\.co\.th/[A-Za-z0-9]+)', post_text)
                    if not links:
                        links = re.findall(r'(?:https://)?(shopee\.co\.th/[^\s\n]+)', post_text)
                        
                    # ถ้าในข้อความมองไม่เห็น (อาจจะโดนซ่อนในคำว่า 'ดูเพิ่มเติม') ให้ไปดึงจากลิงก์ <a> ตรงๆ
                    if not links:
                        anchors = post.locator('a').all()
                        for a in anchors:
                            href = a.get_attribute('href') or ""
                            # Facebook มักจะครอบลิงก์ด้วย l.facebook.com/l.php?u=...
                            import urllib.parse
                            if "u=" in href:
                                try:
                                    parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                                    if 'u' in parsed:
                                        href = parsed['u'][0]
                                except:
                                    pass
                            
                            m = re.search(r'(?:https://)?(s\.shopee\.co\.th/[A-Za-z0-9]+)', href)
                            if not m:
                                m = re.search(r'(?:https://)?(shopee\.co\.th/[^\s\n]+)', href)
                            if m:
                                links.append(m.group(1))
                                break
                                
                    if links:
                        target_link = links[0]
                        if not target_link.startswith("http"):
                            target_link = "https://" + target_link
                            
                        if target_link in scanned_urls: continue
                            
                        scanned_urls.add(target_link)
                        print(f"\n📦 พบโพสต์ที่มีลิงก์ Shopee: {target_link}")
                        print("กำลังเช็คสถานะสินค้า...")
                        
                        info = resolve_affiliate_link(target_link)
                        
                        if info is None:
                            print("🚨 คำเตือน: สินค้าไม่มีอยู่จริง! กำลังลบโพสต์...")
                            post.scroll_into_view_if_needed()
                            time.sleep(1)
                            
                            menu_btn = post.locator('div[aria-haspopup="menu"]').first
                            if menu_btn.is_visible():
                                menu_btn.click()
                                time.sleep(2)
                                
                                trash_btn = page.locator('span:has-text("ย้ายไปที่ถังขยะ"), span:has-text("Move to trash")').first
                                if trash_btn.is_visible():
                                    trash_btn.click()
                                    time.sleep(2)
                                    
                                    confirm_btn = page.locator('div[aria-label="ย้าย"], div[aria-label="Move"]').first
                                    if confirm_btn.is_visible():
                                        confirm_btn.click()
                                        print("✅ ลบโพสต์สำเร็จ!")
                                        deleted_count += 1
                                        time.sleep(4)
                                    else:
                                        print("⚠️ หาปุ่มยืนยันการลบไม่เจอ")
                                else:
                                    print("⚠️ หาเมนูย้ายไปถังขยะไม่เจอ")
                            else:
                                print("⚠️ หาปุ่ม ... ไม่เจอ")
                        else:
                            print(f"✅ สินค้ายังอยู่ปกติ (รหัส: {info['product_id']})")
                except Exception as e:
                    print(f"Error checking post: {e}")
                    
            print(f"⬇️ เลื่อนหน้าจอลง... ({scroll+1}/{scroll_limit})")
            page.mouse.wheel(0, 1000)
            time.sleep(3)
            
        print("\n========================================")
        print(f"🎉 สแกนเสร็จสิ้น! ลบโพสต์ที่ลิงก์ตายไปทั้งหมด {deleted_count} โพสต์")
        print("========================================")
        browser.close()
        return True

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    url = input("ใส่ลิงก์เพจ: ")
    clean_dead_links(url)


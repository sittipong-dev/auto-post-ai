import os
import sys
import time
import re
import pyperclip
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
        
    print("🚀 กำลังโหลดบอทโพสต์...")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=profile_dir,
                headless=False,
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
            
            # ========== โหมดโพสต์ข้อความเฉยๆ (ไม่มีวิดีโอ) ==========
            if video_path is None:
                print("📝 โหมดโพสต์ข้อความ...")
                page.goto("https://www.facebook.com/profile.php", wait_until="domcontentloaded")
                time.sleep(5)
                page.keyboard.press("Escape")
                time.sleep(1)
                
                # เปิดกล่องสร้างโพสต์
                create_post_btn = page.locator("text=คุณกำลังคิดอะไรอยู่")
                if create_post_btn.count() > 0:
                    create_post_btn.first.click(force=True)
                else:
                    page.keyboard.press("p")
                time.sleep(4)
                
                # วางแคปชั่น (ใช้ JavaScript Paste Event เพื่อกระตุ้น Lexical Editor ให้รับรู้ข้อความ 100%)
                textbox = page.locator('div[contenteditable="true"]').first
                textbox.evaluate("""node => {
                    node.focus();
                    node.dispatchEvent(new MouseEvent('click', {bubbles: true}));
                }""")
                time.sleep(1)
                
                # จำลอง Paste Event ที่ Lexical Editor จะรับรู้
                page.evaluate("""(text) => {
                    const editor = document.querySelector('div[contenteditable="true"]');
                    if (!editor) return;
                    editor.focus();
                    const dt = new DataTransfer();
                    dt.setData('text/plain', text);
                    const pasteEvent = new ClipboardEvent('paste', {
                        bubbles: true,
                        cancelable: true,
                        clipboardData: dt
                    });
                    editor.dispatchEvent(pasteEvent);
                }""", caption)
                time.sleep(3)
                
                # เช็คว่าข้อความถูกวางจริงหรือเปล่า
                editor_text = page.evaluate("""() => {
                    const editor = document.querySelector('div[contenteditable="true"]');
                    return editor ? editor.innerText.trim() : '';
                }""")
                
                if len(editor_text) > 0:
                    print(f"✅ วางแคปชั่นสำเร็จ! (ความยาว {len(editor_text)} ตัวอักษร)")
                else:
                    # ถ้า Paste Event ไม่เวิร์ค ลองใช้ execCommand แทน
                    print("⚠️ Paste Event ไม่เวิร์ค กำลังลองวิธีสำรอง (execCommand)...")
                    page.evaluate("""(text) => {
                        const editor = document.querySelector('div[contenteditable="true"]');
                        if (!editor) return;
                        editor.focus();
                        document.execCommand('insertText', false, text);
                    }""", caption)
                    time.sleep(2)
                    
                    editor_text2 = page.evaluate("""() => {
                        const editor = document.querySelector('div[contenteditable="true"]');
                        return editor ? editor.innerText.trim() : '';
                    }""")
                    
                    if len(editor_text2) > 0:
                        print(f"✅ วางแคปชั่นสำเร็จด้วยวิธีสำรอง! (ความยาว {len(editor_text2)} ตัวอักษร)")
                    else:
                        # วิธีสุดท้าย: ใช้ keyboard.type พิมพ์ทีละตัว (ช้าแต่ชัวร์)
                        print("⚠️ ลองวิธีสุดท้าย: พิมพ์ทีละตัวอักษร...")
                        page.keyboard.type(caption, delay=10)
                        time.sleep(2)
                        print("✅ พิมพ์แคปชั่นเสร็จแล้ว!")
                
                # ถ่ายรูปเช็คว่าข้อความโผล่บนหน้าจอจริงไหม
                ensure_dir("scratch")
                screenshot_path = os.path.abspath(os.path.join("scratch", "fb_caption_check.png"))
                page.screenshot(path=screenshot_path)
                print(f"📸 ถ่ายรูปหน้าจอหลังวางแคปชั่นเก็บไว้ที่: {screenshot_path}")
                time.sleep(2)
                
                # ปิด Link Preview ที่เฟสบุ๊คเด้งขึ้นมาเมื่อเจอลิงก์ในแคปชั่น (มันจะบังปุ่มถัดไป!)
                print("🗑️ กำลังปิด Link Preview (ถ้ามี)...")
                try:
                    # หาปุ่มลบ/ปิด Link Preview (ไอคอนถังขยะหรือ X)
                    close_preview = page.locator('div[aria-label="ลบ"], div[aria-label="Remove"], div[aria-label="นำภาพตัวอย่างออก"], div[aria-label="Remove preview"]').first
                    if close_preview.is_visible(timeout=3000):
                        close_preview.click(force=True)
                        print("✅ ปิด Link Preview สำเร็จ!")
                        time.sleep(2)
                    else:
                        # ลองหาปุ่ม X แบบอื่น
                        trash_btns = page.locator('svg[aria-label="ลบ"], svg[aria-label="Remove"]')
                        if trash_btns.count() > 0:
                            trash_btns.first.click(force=True)
                            print("✅ ปิด Link Preview สำเร็จ (วิธี 2)!")
                            time.sleep(2)
                        else:
                            print("ℹ️ ไม่เจอ Link Preview (อาจจะไม่มี)")
                except Exception as e:
                    print(f"ℹ️ ไม่มี Link Preview หรือปิดไม่ได้: {e}")
                
                # ฟังก์ชันช่วยคลิกแบบมนุษย์ (ข้ามระบบป้องกันของ React)
                def human_click(element):
                    try:
                        element.scroll_into_view_if_needed()
                        time.sleep(0.5)
                        box = element.bounding_box()
                        if box:
                            page.mouse.click(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
                            return
                    except: pass
                    try: element.click(force=True)
                    except: element.evaluate("node => node.click()")

                # หากดปุ่ม ถัดไป (Next) ก่อน — กดแค่ครั้งเดียว!
                print("🚀 กำลังเช็คว่ามีปุ่ม 'ถัดไป' หรือไม่...")
                next_clicked = False
                for attempt in range(3):
                    if next_clicked:
                        break
                    all_btns = page.locator("div[role='button'], button")
                    for i in range(all_btns.count()):
                        btn = all_btns.nth(i)
                        try:
                            if btn.is_visible():
                                text = btn.inner_text().strip()
                                label = (btn.get_attribute("aria-label") or "").strip()
                                if text == "ถัดไป" or label == "ถัดไป" or text == "Next" or label == "Next":
                                    print("✅ เจอปุ่ม 'ถัดไป' กำลังเอาเมาส์ไปคลิก...")
                                    human_click(btn)
                                    next_clicked = True
                                    time.sleep(5)
                                    # ถ่ายรูปหลังกดถัดไป
                                    page.screenshot(path=os.path.abspath(os.path.join("scratch", "fb_after_next.png")))
                                    print("📸 ถ่ายรูปหลังกดถัดไป → scratch/fb_after_next.png")
                                    break
                        except: pass
                    time.sleep(2)

                # กดปุ่มโพสต์ — หาปุ่มสีฟ้าตัวสุดท้ายที่เขียนว่า "โพสต์" เท่านั้น (ไม่ใช่เมนูที่มีคำว่าโพสต์ปน)
                print("🚀 กำลังหาปุ่ม 'โพสต์' (ปุ่มสีฟ้าด้านล่าง)...")
                post_btn = None
                for _ in range(5):
                    # วิธี 1: หาปุ่มที่ inner_text ตรงเป๊ะว่า "โพสต์" (ไม่มีคำอื่นปน)
                    all_btns = page.locator("div[role='button'], button")
                    for i in range(all_btns.count()):
                        btn = all_btns.nth(i)
                        try:
                            if btn.is_visible():
                                text = btn.inner_text().strip()
                                label = (btn.get_attribute("aria-label") or "").strip()
                                # ต้องตรงเป๊ะๆ ว่า "โพสต์" หรือ "Post" เท่านั้น ห้ามมีคำอื่นปน!
                                if text in ["โพสต์", "Post"] and len(text) <= 6:
                                    post_btn = btn  # ไม่ break เพื่อเอาตัวสุดท้าย (ปุ่มล่างสุด)
                                elif label in ["โพสต์", "Post"] and len(label) <= 6:
                                    post_btn = btn
                        except: pass
                    if post_btn: break
                    time.sleep(2)
                    
                if post_btn:
                    print("✅ เจอปุ่มโพสต์แล้ว กำลังเอาเมาส์ไปคลิก...")
                    human_click(post_btn)
                    print("✅ กดปุ่มโพสต์แล้ว!")
                    time.sleep(5)
                    # ถ่ายรูปหลังกดโพสต์
                    page.screenshot(path=os.path.abspath(os.path.join("scratch", "fb_after_post.png")))
                    print("📸 ถ่ายรูปหลังกดโพสต์ → scratch/fb_after_post.png")
                else:
                    print("⚠️ หาปุ่มโพสต์ไม่เจอ!")
                    return False
                
                # หากดปุ่ม เรียบร้อย (Done) เผื่อมีหน้าต่างยืนยันเด้งขึ้นมา
                print("🚀 กำลังเช็คว่ามีปุ่ม 'เรียบร้อย' หรือไม่...")
                done_btn = None
                for _ in range(3):
                    all_btns = page.locator("div[role='button'], button")
                    for i in range(all_btns.count()):
                        btn = all_btns.nth(i)
                        try:
                            if btn.is_visible():
                                text = btn.inner_text().strip()
                                label = (btn.get_attribute("aria-label") or "").strip()
                                if text == "เรียบร้อย" or label == "เรียบร้อย" or text == "Done" or label == "Done":
                                    done_btn = btn
                                    break
                        except: pass
                    if done_btn: break
                    time.sleep(2)
                
                if done_btn:
                    print("✅ เจอปุ่ม 'เรียบร้อย' กำลังเอาเมาส์ไปคลิกปิดงาน...")
                    human_click(done_btn)
                    time.sleep(3)
                
                print("✅ โพสต์ข้อความสำเร็จ!")
                browser.close()
                return True
                
            # ========== โหมดอัปโหลดวิดีโอ (Reels) ==========
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

            # 4. ปักตะกร้า Affiliate (ถ้ามีลิงก์)
            if affiliate_url:
                print("🛒 กำลังปักตะกร้า Affiliate ลงในคลิป Reels...")
                try:
                    # หาเมนูเพิ่มสินค้า
                    add_product_btn = page.locator('text="เพิ่มสินค้า", text="Add product", text="Add products"').last
                    if add_product_btn.is_visible(timeout=5000):
                        add_product_btn.click()
                        time.sleep(3)
                        
                        # หากล่องหน้าต่างที่เด้งขึ้นมา
                        modal = page.locator('div[role="dialog"]').last
                        if modal.is_visible(timeout=5000):
                            inputs = modal.locator('input')
                            
                            # ช่องแรกคือ URL
                            inputs.nth(0).fill(affiliate_url)
                            time.sleep(2) # รอให้ระบบ Facebook โหลดลิงก์และขึ้นติ๊กถูกสีเขียว
                            
                            # ช่องสองคือ ชื่อลิงก์
                            inputs.nth(1).fill("กดซื้อสินค้าที่นี่ค่ะ")
                            time.sleep(1)
                            
                            # หาปุ่ม "บันทึก" หรือ "Save" ในหน้าต่างนั้น
                            save_btn = modal.locator('div[role="button"]:has-text("บันทึก"), div[role="button"]:has-text("Save"), button:has-text("บันทึก"), button:has-text("Save")').last
                            save_btn.click()
                            print("✅ ปักตะกร้า Affiliate ลงคลิป Reels สำเร็จ!")
                            time.sleep(3)
                        else:
                            print("⚠️ หน้าต่างเพิ่มสินค้าไม่เด้งขึ้นมา")
                    else:
                        print("⚠️ หาเมนู 'เพิ่มสินค้า' ไม่เจอ (เพจอาจจะยังไม่มีฟีเจอร์นี้) -> ข้ามการปักตะกร้า")
                except Exception as e:
                    print(f"⚠️ เกิดข้อผิดพลาดตอนปักตะกร้า: {e}")

            # 5. กดปุ่ม Publish
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

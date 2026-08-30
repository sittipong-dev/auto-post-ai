import time, re
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir="data/browser_profile",
        headless=True,
        args=['--disable-blink-features=AutomationControlled')
    )
    page = browser.new_page()
    page.goto("https://www.facebook.com/me", wait_until="domcontentloaded")
    time.sleep(5)
    
    try:
        page.get_by_role("tab", name="Reels").click(timeout=5000)
        time.sleep(5)
        
        page.keyboard.press("PageDown")
        time.sleep(3)
        
        first_reel = page.locator('a[href*="/reel/"]').first
        first_reel.click(timeout=5000)
        time.sleep(5)
        page.screenshot(path="scratch/fb_reel_viewer.png")
        print("Clicked first Reel!")
        
        comment_btn = page.get_by_role("button", name=re.compile(r"Comment|แสดงความงิดเห็ู", re.IGNORECASE)).first
        if comment_btn.is_visible():
             comment_btn.click()
             time.sleep(2)
             
        comment_box = page.get_by_role("textbox", name=re.compile(r"comment|ความคิดเห็ี", re.IGNORECASE)).first
        if comment_box.is_visible():
             print("Found comment box!")
             comment_box.fill("Test comment")
        else:
             print("Could not find comment box")
             
        page.screenshot(path="scratch/fb_reel_commented.png")
    except Exception as e:
        print("Failed:", e)
        page.screenshot(path="scratch/fb_reel_failed.png")
        
    browser.close()

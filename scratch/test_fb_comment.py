import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir="data/browser_profile",
        headless=True,
        args=['--disable-blink-features=AutomationControlled']
    )
    page = browser.new_page()
    page.goto("https://www.facebook.com/me", wait_until="domcontentloaded")
    time.sleep(5)
    
    # Try to click Reels tab
    try:
        page.get_by_role("tab", name="Reels").click(timeout=5000)
        time.sleep(5)
        
        # Press PageDown to load grid
        page.keyboard.press("PageDown")
        time.sleep(3)
        
        # Click the first reel link
        first_reel = page.locator('a[href*="/reel/"]').first
        first_reel.click(timeout=5000)
        time.sleep(5)
        page.screenshot(path="scratch/fb_reel_viewer.png")
        print("Clicked first Reel!")
        
        # Now try to find comment button
        comment_box = page.get_by_role("textbox", name="comment")
        if comment_box.count() > 0:
            print("Found comment box!")
            comment_box.first.fill("Test comment")
        else:
            print("No comment textbox found, looking for button...")
            comment_btn = page.get_by_role("button", name="Comment")
            if comment_btn.count() == 0:
                 comment_btn = page.get_by_role("button", name="แสดงความคิดเห็น")
                 
            if comment_btn.count() > 0:
                 comment_btn.first.click()
                 time.sleep(2)
                 comment_box = page.get_by_role("textbox", name="comment")
                 if comment_box.count() == 0:
                     comment_box = page.get_by_role("textbox", name="ความคิดเห็น")
                 if comment_box.count() > 0:
                     print("Found comment box after clicking button!")
                     comment_box.first.fill("Test comment")
            else:
                 print("Could not find comment button")
                 
        page.screenshot(path="scratch/fb_reel_commented.png")
    except Exception as e:
        print("Failed:", e)
        page.screenshot(path="scratch/fb_reel_failed.png")
        
    browser.close()

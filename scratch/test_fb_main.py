import time, re
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
    
    try:
        page.get_by_role("tab", name=re.compile("Reels", re.IGNORECASE)).click(timeout=5000)
        time.sleep(5)
        
        page.keyboard.press("PageDown")
        time.sleep(3)
        
        first_reel = page.locator('div[role="main"] a[href*="/reel/"]').first
        first_reel.click(timeout=5000)
        time.sleep(5)
        page.screenshot(path="scratch/fb_reel_viewer2.png")
        print("Clicked first Reel!")
        
    except Exception as e:
        print("Failed:", e)
        page.screenshot(path="scratch/fb_reel_failed2.png")
        
    browser.close()

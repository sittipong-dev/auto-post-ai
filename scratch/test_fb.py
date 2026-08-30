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
        reels_tab = page.get_by_role("tab", name="Reels")
        reels_tab.click(timeout=5000)
        time.sleep(5)
        page.screenshot(path="scratch/fb_reels_tab.png")
        print("Clicked Reels tab!")
    except Exception as e:
        print("Failed to click Reels tab:", e)
        page.screenshot(path="scratch/fb_reels_tab_failed.png")
        
    browser.close()

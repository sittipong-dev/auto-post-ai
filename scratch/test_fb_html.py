import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir="data/browser_profile",
        headless=True,
        viewport={'width': 1920, 'height': 1080},
        args=['--disable-blink-features=AutomationControlled']
    )
    page = browser.new_page()
    page.goto("https://www.facebook.com/me", wait_until="domcontentloaded")
    time.sleep(5)
    
    page.get_by_role("tab", name="Reels").click()
    time.sleep(5)
    
    page.keyboard.press("PageDown")
    time.sleep(3)
    
    first_reel = page.locator('div[role="main"] a[href*="/reel/"]').first
    first_reel.click()
    time.sleep(5)
    
    html = page.content()
    with open("scratch/reel_page.html", "w", encoding="utf-8") as f:
        f.write(html)
        
    print("HTML saved!")
    browser.close()

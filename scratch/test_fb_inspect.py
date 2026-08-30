import time, re
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
    
    try:
        page.get_by_role("tab", name=re.compile("Reels", re.IGNORECASE)).click(timeout=5000)
        time.sleep(5)
        
        page.keyboard.press("PageDown")
        time.sleep(3)
        
        first_reel = page.locator('div[role="main"] a[href*="/reel/"]').first
        first_reel.click(timeout=5000)
        time.sleep(5)
        
        # Dump all aria-labels that are visible
        elements = page.locator('[aria-label]').all()
        labels = set()
        for el in elements:
            if el.is_visible():
                labels.add(el.get_attribute('aria-label'))
                
        print("Visible aria-labels:")
        for label in labels:
            if label:
                print("-", label)
                
    except Exception as e:
        print("Failed:", e)
        
    browser.close()

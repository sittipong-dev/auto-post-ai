with open('src/fb_poster.py', 'r', encoding='utf-8') as f:
    ma = f.read()

# Increase hard wait after upload to 25 seconds
ma = ma.replace('print("✅ ใส่ไฟล์วิดีโอเข้าระบบสำเร็จ! รอโหลด 10 วินาที...")\n                time.sleep(10)', 'print("✅ ใส่ไฟล์วิดีโอเข้าระบบสำเร็จ! รอกระบวนการอัปโหลดของ Facebook 30 วินาที...")\n                time.sleep(30)')

# Increase timeout on publish button from 15s to 45s
ma = ma.replace('publish_btn.click(timeout=15000)', 'publish_btn.click(timeout=45000)')

with open('src/fb_poster.py', 'w', encoding='utf-8') as f:
    f.write(ma)
print("Updated fb_poster timeouts.")

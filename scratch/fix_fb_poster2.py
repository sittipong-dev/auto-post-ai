with open('src/fb_poster.py', 'r', encoding='utf-8') as f:
    ma = f.read()

# Replace the 30s wait with 60s wait
ma = ma.replace('print("✅ ใส่ไฟล์วิดีโอเข้าระบบสำเร็จ! รอกระบวนการอัปโหลดของ Facebook 30 วินาที...")\n                time.sleep(30)', 'print("✅ ใส่ไฟล์วิดีโอเข้าระบบสำเร็จ! รอกระบวนการอัปโหลดของ Facebook 60 วินาที...")\n                time.sleep(60)')

# Replace the 45s timeout with 90s timeout
ma = ma.replace('publish_btn.click(timeout=45000)', 'publish_btn.click(timeout=90000)')

with open('src/fb_poster.py', 'w', encoding='utf-8') as f:
    f.write(ma)
print("Updated fb_poster timeouts to 60/90s.")

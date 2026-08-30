import re

with open('src/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

target = '''        # 4. โพสต์ลงเพจ
        print(f"\\n🌐 กำลังโพสต์ลง Facebook...")
        from fb_poster import post_to_facebook
        post_success = post_to_facebook(output_video_path, caption)'''

replacement = '''        # --- ระบบตรวจวิดีโอก่อนโพสต์ ---
        print(f"\\n✅ สร้างวิดีโอเสร็จสมบูรณ์! ไฟล์บันทึกอยู่ที่: {output_video_path}")
        print(f"📝 แคปชั่นที่จะโพสต์:\\n{caption}\\n")
        
        while True:
            post_choice = input(f"❓ คุณต้องการโพสต์วิดีโอนี้ลง Facebook หรือไม่? (y = โพสต์เลย / n = ขอเก็บไว้ก่อน): ").strip().lower()
            if post_choice in ['y', 'yes', 'n', 'no']:
                break
            print("⚠️ กรุณาพิมพ์ y (เพื่อโพสต์) หรือ n (เพื่อข้าม)")
            
        if post_choice in ['y', 'yes']:
            # 4. โพสต์ลงเพจ
            print(f"\\n🌐 กำลังโพสต์ลง Facebook...")
            from fb_poster import post_to_facebook
            post_success = post_to_facebook(output_video_path, caption)
        else:
            print(f"\\n⏭️ ยกเลิกการโพสต์ (ไฟล์วิดีโอถูกเก็บไว้ที่เครื่องแล้ว)")
            post_success = False'''

if target in content:
    content = content.replace(target, replacement)
    with open('src/main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully patched main.py")
else:
    print("Target string not found in main.py")

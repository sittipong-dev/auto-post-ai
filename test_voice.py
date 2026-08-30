import os
import sys

# แก้ปัญหา print emoji ไม่ออกบน Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from f5_tts_gen import generate_voice_f5

test_script = "สวัสดีครับคุณสิทธิ์ นี่คือเสียงทดสอบจากเอไอเอฟไฟฟ์ทีทีเอส สมองคนไทยทำงานได้อย่างยอดเยี่ยมครับ"
ref_audio = os.path.join("assets", "voices", "male_cute.wav")
desktop_path = os.path.join(os.environ['USERPROFILE'], 'Desktop')
output_file = os.path.join(desktop_path, 'test_voice.wav')

print("กำลังสั่งรัน F5-TTS (สมองไทย + CUDA)...")
success = generate_voice_f5(test_script, output_file, ref_audio)

if success:
    print(f"\nสำเร็จ! ไฟล์เสียงถูกบันทึกไว้ที่: {output_file}")
    print("เชิญที่หน้า Desktop แล้วดับเบิลคลิกฟังไฟล์ test_voice.wav ได้เลยครับ!")
else:
    print("\nมีบางอย่างผิดพลาดครับ")

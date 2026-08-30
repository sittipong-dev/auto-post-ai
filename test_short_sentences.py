import os
import sys
import soundfile as sf
import speech_recognition as sr
import google.generativeai as genai
from dotenv import load_dotenv

# แก้ปัญหาพิมพ์ภาษาไทยใน console Windows
try: sys.stdout.reconfigure(encoding='utf-8')
except: pass

# 1. ให้ Gemini แต่งสคริปต์แบบสั้นๆ
print("🧠 กำลังให้ Gemini แต่งสคริปต์แบบประโยคสั้นๆ...")
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

prompt = """
คุณคือนักป้ายยาบน TikTok
จงเขียนสคริปต์ขายของ 10-15 วินาที (ป้ายยากล้องวงจรปิด)
กติกา:
1. เขียนเป็นภาษาพูดป้ายยา
2. 🌟 สำคัญมาก: ห้ามเขียนประโยคยาวเด็ดขาด! ให้เขียนเป็นประโยคสั้นๆ ห้วนๆ กระชับๆ (ประโยคละไม่เกิน 5-7 คำ) แล้วให้กด "ขึ้นบรรทัดใหม่" เสมอ
3. แปลงตัวเลขเป็นคำอ่าน (เช่น 24 ชั่วโมง เป็น ยี่สิบสี่ชั่วโมง)
4. จบสคริปต์ด้วยคำว่า ค่ะ

ตัวอย่างที่ถูกต้อง:
กล้องตัวนี้ดีมากค่ะ
ภาพชัดแจ๋ว
ดูผ่านมือถือได้เลย
ติดไว้ปลอดภัยแน่นอนค่ะ
จิ้มตะกร้าเลยค่ะ

สคริปต์ของคุณ:
"""
model = genai.GenerativeModel('gemini-3.5-flash-lite')
response = model.generate_content(prompt)
script_text = response.text.strip()
print("\n--- สคริปต์ที่ได้ ---")
print(script_text)
print("-------------------\n")

# 2. พากย์เสียงด้วย F5-TTS
print("🚀 กำลังโหลดสมองกลภาษาไทย (F5-TTS V1)...")
from f5_tts_th.tts import TTS
from f5_tts_th.utils_infer import load_model

def local_load_f5tts(self, model_type="v1"):
    ckpt_path = os.path.join("assets", "f5_models", "model_1000000.pt")
    vocab_path = os.path.join("assets", "f5_models", "vocab.txt")
    model_cfg = dict(dim=1024, depth=22, heads=16, ff_mult=2, text_dim=512, text_mask_padding=False, conv_layers=4, pe_attn_head=1)
    return load_model(model_cfg, ckpt_path, mel_spec_type=self.vocoder_name, vocab_file=vocab_path)

TTS.load_f5tts = local_load_f5tts
tts = TTS(model="v1")

ref_path = r"assets\voices\female_cute.wav"
out_path = os.path.join(os.environ['USERPROFILE'], 'Desktop', 'test_short_sentences.wav')

r = sr.Recognizer()
with sr.AudioFile(ref_path) as source:
    ref_text = r.recognize_google(r.record(source), language='th-TH')

# แปลงการขึ้นบรรทัดใหม่เป็นจุด เพื่อให้ AI หยุดหายใจอย่างเป็นธรรมชาติ
gen_text = script_text.replace('\n', ' . \n')

print("🎙️ กำลังสังเคราะห์เสียง...")
wav = tts.infer(ref_audio=ref_path, ref_text=ref_text, gen_text=gen_text, step=32, cfg=2.0, speed=1.15)
sf.write(out_path, wav, 24000)
print(f"✅ บันทึกไฟล์สำเร็จที่: {out_path}")

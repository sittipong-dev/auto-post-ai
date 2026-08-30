import os
import soundfile as sf
import speech_recognition as sr
import sys

# แก้ปัญหาพิมพ์ภาษาไทยใน console Windows
try: sys.stdout.reconfigure(encoding='utf-8')
except: pass

desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')

voices = [
    "female_cute.wav",
    "female_formal.wav",
    "male_cute.wav",
    "male_deep.wav",
    "test01.wav"
]

gen_text = "สวัสดีค่ะทุกคน ช่วงนี้ทำงานหนัก ปวดหลังปวดคอกันบ้างไหมคะ อย่าลืมพักผ่อนและหันมาดูแลตัวเองกันบ้างนะคะ ถ้าใครมองหาตัวช่วยดีๆ จิ้มลิงก์ด้านล่างไปดูแลสุขภาพกันได้เลยค่ะ"

print("🚀 กำลังโหลดสมองกลภาษาไทย (F5-TTS V1)... (รอประมาณ 10-15 วินาที)")

from f5_tts_th.tts import TTS
from f5_tts_th.utils_infer import load_model

# Monkey Patch
def local_load_f5tts(self, model_type="v1"):
    ckpt_path = os.path.join("assets", "f5_models", "model_1000000.pt")
    vocab_path = os.path.join("assets", "f5_models", "vocab.txt")
    model_cfg = dict(
        dim=1024, depth=22, heads=16, ff_mult=2,
        text_dim=512, text_mask_padding=False,
        conv_layers=4, pe_attn_head=1,
    )
    return load_model(
        model_cfg, ckpt_path,
        mel_spec_type=self.vocoder_name,
        vocab_file=vocab_path,
    )

TTS.load_f5tts = local_load_f5tts
tts = TTS(model="v1")
print("✅ โหลดสมองกลสำเร็จ! เริ่มทำการพากย์เสียงทั้ง 5 แบบด้วยสคริปต์สายสุขภาพ...")

r = sr.Recognizer()

for voice in voices:
    ref_path = os.path.join("assets", "voices", voice)
    # ใส่ชื่อว่า health_ เพื่อไม่ให้ทับไฟล์เก่า
    out_path = os.path.join(desktop, f"health_{voice}")
    
    if not os.path.exists(ref_path):
        print(f"⚠️ ไม่พบไฟล์ {voice} ข้ามการทดสอบ")
        continue
        
    print(f"\n🎙️ กำลังพากย์เสียง: {voice}...")
    
    # 1. ถอดความเสียงต้นแบบ
    ref_text = ""
    try:
        with sr.AudioFile(ref_path) as source:
            audio_data = r.record(source)
            ref_text = r.recognize_google(audio_data, language='th-TH')
    except Exception as e:
        continue
        
    # 2. พากย์เสียง (ใช้สปีด 1.05 พอ เพราะเป็นสายสุขภาพ พูดเนิบๆ หน่อย)
    try:
        wav = tts.infer(
            ref_audio=ref_path,
            ref_text=ref_text,
            gen_text=gen_text,
            step=32,
            cfg=2.0,
            speed=1.05
        )
        sf.write(out_path, wav, 24000)
        print(f"   ✅ บันทึกไฟล์สำเร็จที่: {out_path}")
    except Exception as e:
        print(f"   ❌ พากย์เสียงพัง: {e}")

print("\n🎉 พากย์เสียงครบทั้ง 5 ไฟล์แล้ว! ไปลองฟังที่หน้า Desktop ได้เลยครับ")

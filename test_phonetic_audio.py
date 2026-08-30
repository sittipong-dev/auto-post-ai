import os
import soundfile as sf
import speech_recognition as sr
import sys

try: sys.stdout.reconfigure(encoding='utf-8')
except: pass

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
out_path = os.path.join(os.environ['USERPROFILE'], 'Desktop', 'test_phonetic.wav')

r = sr.Recognizer()
with sr.AudioFile(ref_path) as source:
    ref_text = r.recognize_google(r.record(source), language='th-TH')

gen_text = "ซื้อ กล้อง วง จร ปิด ตัว นี้ ปลอด ภัย ไร้ กัง วล ตลอด ยี่ สิบ สี่ ชั่ว โมง คับ"

wav = tts.infer(ref_audio=ref_path, ref_text=ref_text, gen_text=gen_text, step=32, cfg=2.0, speed=1.15)
sf.write(out_path, wav, 24000)
print(f"✅ บันทึกไฟล์สำเร็จที่: {out_path}")

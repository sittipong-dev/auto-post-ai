import os
import soundfile as sf
from f5_tts_th.tts import TTS
import speech_recognition as sr

ref_audio = r"C:\Users\ssitt\Desktop\auto post  ai\assets\voices\male_cute.wav"
out_audio = r"C:\Users\ssitt\Desktop\auto post  ai\output\test_f5th.wav"

r = sr.Recognizer()
with sr.AudioFile(ref_audio) as source:
    audio_data = r.record(source)
    ref_text = r.recognize_google(audio_data, language='th-TH')
    print("Ref text:", ref_text)

print("Loading TTS model...")
tts = TTS(model="v1")

print("Generating voice...")
wav = tts.infer(
    ref_audio=ref_audio,
    ref_text=ref_text,
    gen_text="นี่คือการทดสอบ มุมมอง และ ปวดคอ ครับ",
    step=32,
    cfg=2.0,
    speed=1.15
)

sf.write(out_audio, wav, 24000)
print("Done! Saved to:", out_audio)

# -*- coding: utf-8 -*-
import os
import subprocess
import shutil

def generate_voice_f5(script_text, output_path, ref_audio_path):
    print(f"กำลังพากย์เสียงด้วย F5-TTS (Native Thai)... (อาจใช้เวลาสักครู่)")
    
    # ลบไฟล์เก่าออกก่อน
    if os.path.exists(output_path):
        os.remove(output_path)
        
    out_dir = os.path.dirname(output_path)
    
    # ใช้ Google Speech Recognition แกะสคริปต์ต้นฉบับภาษาไทย
    import speech_recognition as sr
    ref_text = ""
    try:
        r = sr.Recognizer()
        with sr.AudioFile(ref_audio_path) as source:
            audio_data = r.record(source)
            ref_text = r.recognize_google(audio_data, language='th-TH')
            print(f"[AI] แกะเสียงต้นแบบได้ว่า: {ref_text}")
    except Exception as e:
        print(f"[Warning] แกะเสียงต้นแบบไม่สำเร็จ จะปล่อยให้ F5-TTS เดาเอง: {e}")
        ref_text = ""
        
    if not ref_text:
        print("❌ ข้อผิดพลาด: ไม่สามารถถอดรหัสเสียงต้นแบบได้ F5-TTS จำเป็นต้องใช้สคริปต์ต้นแบบ!")
        return False
        
    try:
        from f5_tts_th.tts import TTS
        from f5_tts_th.utils_infer import load_model
        import soundfile as sf
        
        # Monkey patch TTS.load_f5tts เพื่อป้องกันการดาวน์โหลดไฟล์ 1.3GB ซ้ำ!
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
        
        # โหลดโมเดลภาษาไทย V1
        tts = TTS(model="v1")
        
        # ปรับแก้ปัญหาการเว้นวรรค
        gen_text = script_text.replace("\n", " . \n")
        
        # รันการสร้างเสียง
        print("กำลังสังเคราะห์เสียง...")
        wav = tts.infer(
            ref_audio=ref_audio_path,
            ref_text=ref_text,
            gen_text=gen_text,
            step=32,
            cfg=2.0,
            speed=1.15
        )
        
        # บันทึกไฟล์ 24kHz
        sf.write(output_path, wav, 24000)
        print("✅ F5-TTS พากย์เสียงสำเร็จ")
        return True
    except Exception as e:
        print(f"❌ F5-TTS Error: {e}")
        return False

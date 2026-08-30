import sys
import speech_recognition as sr
sys.stdout.reconfigure(encoding='utf-8')
r = sr.Recognizer()
with sr.AudioFile('assets/voices/male_cute.wav') as source:
    audio = r.record(source)
    try:
        text = r.recognize_google(audio, language='th-TH')
        print("Transcript:", text)
    except Exception as e:
        print("Error:", e)

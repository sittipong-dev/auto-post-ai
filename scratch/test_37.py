import google.generativeai as genai
import os
import sys
from dotenv import load_dotenv

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

model_name = 'models/gemini-3.7-flash'
try:
    model_info = genai.get_model(model_name)
    print(f"OK! Found model: {model_info.name}")
    
    # ทดสอบเรียกใช้งานจริง
    print(f"Testing model {model_name}...")
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Hello")
    print(f"Success! Reply: {response.text.strip()}")
    
except Exception as e:
    print(f"Error: {e}")

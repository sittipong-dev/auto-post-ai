with open('src/main.py', 'r', encoding='utf-8') as f:
    ma = f.read()

# Downscale caption model to 3.5-flash-lite to save 3.7 quota
ma = ma.replace("model = __import__('google.generativeai').generativeai.GenerativeModel('gemini-3.7-flash')", "model = __import__('google.generativeai').generativeai.GenerativeModel('gemini-3.5-flash-lite')")

with open('src/main.py', 'w', encoding='utf-8') as f:
    f.write(ma)
print("Caption model downgraded to 3.5-lite to save quota.")

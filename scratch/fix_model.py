with open('src/ai_gen.py', 'r', encoding='utf-8') as f:
    ai = f.read()
with open('src/ai_gen.py', 'w', encoding='utf-8') as f:
    f.write(ai.replace('gemini-1.5-flash', 'gemini-3.5-flash'))

with open('src/main.py', 'r', encoding='utf-8') as f:
    ma = f.read()
with open('src/main.py', 'w', encoding='utf-8') as f:
    f.write(ma.replace('gemini-1.5-flash', 'gemini-3.5-flash'))
print("Fixed model name.")

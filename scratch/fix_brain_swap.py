with open('src/ai_gen.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'def generate_script(' in line:
        for j in range(i, i+10):
            if 'model = genai.GenerativeModel' in lines[j]:
                lines[j] = "    model = genai.GenerativeModel('gemini-3.5-flash-lite')\n"
                break
    elif 'def generate_broll_script(' in line:
        for j in range(i, i+10):
            if 'model = genai.GenerativeModel' in lines[j]:
                lines[j] = "    model = genai.GenerativeModel('gemini-3.7-flash')\n"
                break

with open('src/ai_gen.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("Models fixed properly.")

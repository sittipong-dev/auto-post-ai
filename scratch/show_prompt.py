with open('src/ai_gen.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    
start = False
for line in lines:
    if 'prompt = f"""' in line:
        start = True
    if start:
        print(line, end='')
    if '"""' in line and not 'prompt = f"""' in line and start:
        break

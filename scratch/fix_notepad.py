with open('src/main.py', 'r', encoding='utf-8') as f:
    ma = f.read()

# Replace os.system with os.startfile
ma = ma.replace('os.system(f\'notepad "{script_file}"\')', 'os.startfile(script_file)')

with open('src/main.py', 'w', encoding='utf-8') as f:
    f.write(ma)
print("Replaced os.system with os.startfile")

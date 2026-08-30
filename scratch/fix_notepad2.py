with open('src/main.py', 'r', encoding='utf-8') as f:
    ma = f.read()

# Replace os.startfile with explicit subprocess call
old_code = "os.startfile(script_file)"
new_code = """import subprocess
            try:
                subprocess.Popen(['notepad.exe', os.path.abspath(script_file)])
            except Exception as e:
                print(f"❌ เปิด Notepad ไม่สำเร็จ: {e}")"""

if old_code in ma:
    ma = ma.replace(old_code, new_code)
    with open('src/main.py', 'w', encoding='utf-8') as f:
        f.write(ma)
    print("Replaced with subprocess.Popen")
else:
    print("Code not found.")

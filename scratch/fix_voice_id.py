with open('src/main.py', 'r', encoding='utf-8') as f:
    ma = f.read()
ma = ma.replace('f5_ref_voice = "alice"', 'f5_ref_voice = "21m00Tcm4TlvDq8ikWAM"')
ma = ma.replace('f5_ref_voice = "brian"', 'f5_ref_voice = "pNInz6obbfdqIqcOQ62R"')
with open('src/main.py', 'w', encoding='utf-8') as f:
    f.write(ma)
print("Fixed voice IDs.")

with open('src/main.py', 'r', encoding='utf-8') as f:
    ma = f.read()

ma = ma.replace('f5_ref_voice = "21m00Tcm4TlvDq8ikWAM"', 'f5_ref_voice = "Xb7hH8MSUJpSbSDYk0k2"')
ma = ma.replace('f5_ref_voice = "pNInz6obbfdqIqcOQ62R"', 'f5_ref_voice = "nPczCjzI2devNBz1zQrb"')

with open('src/main.py', 'w', encoding='utf-8') as f:
    f.write(ma)
print("Fixed voice IDs in main.py")

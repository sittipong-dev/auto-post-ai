with open('src/elevenlabs_gen.py', 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace('"model_id": "eleven_multilingual_v2"', '"model_id": "eleven_v3"')
with open('src/elevenlabs_gen.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated to eleven_v3.")

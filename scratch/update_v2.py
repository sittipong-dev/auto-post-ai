with open('src/elevenlabs_gen.py', 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace('"model_id": "eleven_v3"', '"model_id": "eleven_multilingual_v2"')
with open('src/elevenlabs_gen.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated to multilingual_v2 in main code.")

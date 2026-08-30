with open('src/ai_gen.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace specifically inside generate_script (Salesman)
old_func = "def generate_script(product_name, price, tone"
new_func = old_func
content = content.replace("model = genai.GenerativeModel('gemini-3.7-flash')", "model = genai.GenerativeModel('gemini-3.5-flash-lite')", 1)

with open('src/ai_gen.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Split-brain architecture implemented successfully.")

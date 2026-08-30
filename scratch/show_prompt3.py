import re
with open('src/ai_gen.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Find all prompts
prompts = re.findall(r'prompt = f\"\"\"(.*?)\"\"\"', text, re.DOTALL)
if len(prompts) > 1:
    with open('scratch/prompt_broll.txt', 'w', encoding='utf-8') as out:
        out.write(prompts[1])

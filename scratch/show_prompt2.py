import json
with open('src/ai_gen.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
match = re.search(r'prompt = f\"\"\"(.*?)\"\"\"', text, re.DOTALL)
if match:
    # write to a temp file and type it
    with open('scratch/prompt_out.txt', 'w', encoding='utf-8') as out:
        out.write(match.group(1))

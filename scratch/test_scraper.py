import requests
import re

url = 'https://shopee.co.th/product/1278126372/26962408187'
headers = {'User-Agent': 'Mozilla/5.0'}
text = requests.get(url, headers=headers).text

# Look for image hashes like "sg-11134201-7rd5z-lz..."
# Shopee image hashes are typically 32 chars long, but sometimes they have prefixes.
# Let's just find anything looking like down-th.img.susercontent.com/file/xxx
matches = re.findall(r'down-th\.img\.susercontent\.com/file/([a-zA-Z0-9_-]+)', text)
# Unique hashes
unique_hashes = list(dict.fromkeys(matches))

print(f"Found {len(unique_hashes)} unique image hashes:")
for h in unique_hashes[:10]:
    print(f"https://down-th.img.susercontent.com/file/{h}")

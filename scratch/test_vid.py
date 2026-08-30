import requests, re, json
url = 'https://shopee.co.th/product/1128049590/25855289623'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
res = requests.get(url, headers=headers)
print('Length:', len(res.text))

mp4_urls = re.findall(r'(https://cvf\.shopee\.co\.th/file/[a-zA-Z0-9]+(?:\.mp4)?)', res.text)
if mp4_urls:
    print('Found cvf mp4 URLs:', set(mp4_urls))

mp4_urls2 = re.findall(r'(https://[a-zA-Z0-9-.]+/file/[a-zA-Z0-9]+(?:\.mp4)?)', res.text)
print('All /file/ URLs:', set(mp4_urls2))

import requests, re, json
url = 'https://shopee.co.th/product/1128049590/25855289623'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
res = requests.get(url, headers=headers)
match = re.search(r'\"video_info_list\":\[(.*?)\]', res.text)
if match:
    print('Found video info:', match.group(1))
else:
    print('No video info list')

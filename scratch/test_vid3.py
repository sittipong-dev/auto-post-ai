import requests
url = 'https://down-zl-th.vod.susercontent.com/api/v4/11110105/mms/th-11110105-6ke15-lprn9klb8mje78.16003251731663390.mp4'
res = requests.head(url)
print('Status:', res.status_code)
print('Content-Type:', res.headers.get('Content-Type'))

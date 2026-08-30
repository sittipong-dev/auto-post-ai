import sys
import os
sys.path.append('src')
sys.stdout.reconfigure(encoding='utf-8')
from web_image_api import search_and_download_image
success = search_and_download_image('หมอผู้หญิงคนไทยกำลังให้คำปรึกษา', 'assets/temp_broll/test.jpg')
print("Success:", success)

import os
import requests
from ddgs import DDGS

def search_and_download_image(query, output_path):
    print(f"🔍 กำลังค้นหาภาพจากอินเทอร์เน็ตด้วยคำว่า: '{query}'")
    try:
        # Search for images using DuckDuckGo
        ddgs = DDGS()
        results = list(ddgs.images(
            query,
            safesearch='moderate',
            max_results=5
        ))
        
        if not results:
            print(f"⚠️ ไม่พบรูปภาพสำหรับคำว่า '{query}'")
            return False
            
        # Try downloading the first valid image
        for img_data in results:
            img_url = img_data.get('image')
            if not img_url:
                continue
                
            try:
                print(f"⬇️ กำลังดาวน์โหลดภาพ...")
                headers = {'User-Agent': 'Mozilla/5.0'}
                response = requests.get(img_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    print(f"✅ ดาวน์โหลดภาพสำเร็จ: {output_path}")
                    return True
            except Exception as e:
                print(f"⚠️ โหลดภาพจากลิงก์แรกล้มเหลว ลองลิงก์ถัดไป... ({e})")
                continue
                
        print(f"❌ ดาวน์โหลดภาพไม่สำเร็จเลยสำหรับ '{query}'")
        return False
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการค้นหาภาพ: {e}")
        return False

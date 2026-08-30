import os
import requests
from dotenv import load_dotenv

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

def search_pexels_video(query, orientation="portrait", size="medium", per_page=15):
    if not PEXELS_API_KEY:
        print("❌ ไม่พบ PEXELS_API_KEY ในไฟล์ .env")
        return None
        
    url = "https://api.pexels.com/videos/search"
    headers = {
        "Authorization": PEXELS_API_KEY
    }
    params = {
        "query": query,
        "orientation": orientation,
        "size": size,
        "per_page": per_page
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get("videos"):
                return data["videos"]
            else:
                print(f"⚠️ ไม่พบวิดีโอสำหรับคีย์เวิร์ด: {query}")
                return []
        else:
            print(f"❌ Pexels API Error: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการค้นหาวิดีโอ Pexels: {e}")
        return []

def get_best_video_link(video_data):
    files = video_data.get("video_files", [])
    if not files:
        return None
        
    best_file = None
    for f in files:
        if f.get("quality") == "hd" and f.get("width", 0) <= 1080:
            best_file = f
            break
            
    if not best_file:
        best_file = files[0]
        
    return best_file.get("link")

def download_pexels_video(url, output_path):
    try:
        response = requests.get(url, stream=True, timeout=30)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        else:
            print(f"❌ ดาวน์โหลดล้มเหลว: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดขณะดาวน์โหลด: {e}")
        return False

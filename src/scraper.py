import pandas as pd
import os
import sys
import requests
from bs4 import BeautifulSoup
import traceback

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

from PIL import Image

def download_image(url, save_path, min_size=400):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
                
            # ตรวจสอบขนาด สัดส่วนภาพ และ "ขนาดไฟล์ (File Size)"
            try:
                # 3. เช็คขนาดไฟล์ (Bytes) ถ้ารูปใหญ่แต่ไฟล์เล็กกว่า 40KB แปลว่าเป็นรูปโปร่งใส/แบนเนอร์ว่างเปล่า (Shopee Overlay)
                file_size = os.path.getsize(save_path)
                if file_size < 40000:
                    os.remove(save_path)
                    return False
                    
                with Image.open(save_path) as img:
                    width, height = img.width, img.height
                    
                    # 1. เล็กเกินไป (ต่ำกว่า 400x400) = รูปโลโก้/ไอคอน
                    is_too_small = width < min_size or height < min_size
                    
                    # 2. สัดส่วนภาพ (กว้าง/ยาว) ไม่อยู่ในช่วง 0.8 ถึง 1.25 = รูปแบนเนอร์ยาวๆ หรือป้ายโฆษณา
                    ratio = width / height if height > 0 else 0
                    is_not_square = ratio < 0.8 or ratio > 1.25
                    
                    if is_too_small or is_not_square:
                        img.close()
                        os.remove(save_path)
                        return False
            except Exception:
                os.remove(save_path)
                return False
                
            return True
        return False
    except Exception as e:
        print(f"Download Exception: {e}")
        return False

import re

def scrape_shopee_images(url, max_images=20):
    print(f"Scraping Data จาก: {url}")
    image_urls = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            html_text = response.text
            soup = BeautifulSoup(html_text, 'html.parser')
            
            # 1. หารูปภาพหลัก (og:image) ก่อน เพราะชัดสุดชัวร์สุด
            og_img = soup.find('meta', property='og:image')
            if og_img and og_img.get('content'):
                image_urls.append(og_img['content'])
                
            # 2. ล้วงรูปภาพเพิ่มเติมจากโค้ดหลังบ้าน (ค้นหา hash รูป)
            matches = re.findall(r'down-th\.img\.susercontent\.com/file/([a-zA-Z0-9_-]+)', html_text)
            
            for m in matches:
                # สร้าง url เต็ม
                full_url = f"https://down-th.img.susercontent.com/file/{m}"
                # เช็คว่าไม่ซ้ำกับรูปที่มีอยู่แล้ว
                if full_url not in image_urls:
                    image_urls.append(full_url)
                
                # ถ้าครบตามจำนวนที่ต้องการแล้ว (เช่น 5 รูป) ก็หยุดหา
                if len(image_urls) >= max_images:
                    break
        else:
            print(f"Server returned status code: {response.status_code}")
    except Exception as e:
        print(f"Scraping Error: {e}")
        
    return image_urls

def scrape_shopee_video(url):
    print(f"Scraping Video จาก: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            html_text = response.text
            # ค้นหาข้อมูล JSON วิดีโอที่ซ่อนอยู่ในโค้ดหลังบ้าน
            match = re.search(r'\"video_info_list\":\[(.*?)\]', html_text)
            if match:
                video_json_str = match.group(1)
                # ค้นหา URL ที่ลงท้ายด้วย .mp4 (มีหลายความละเอียด เราจะดึงมาทั้งหมด)
                urls = re.findall(r'\"url\":\"(https://[^\"]+\.mp4)\"', video_json_str)
                if urls:
                    # ปกติ Shopee จะเรียงไฟล์ 720p ไว้ท้ายๆ หรือไม่ก็เอาอันแรกไปเลย
                    print(f"พบลิงก์วิดีโอ: {urls[-1]}")
                    return urls[-1] 
        else:
            print(f"Server returned status code: {response.status_code}")
    except Exception as e:
        print(f"Video Scrape Error: {e}")
        
    return None

def process_csv(csv_path="data/target_products.csv"):
    try:
        print(f"กำลังเปิดอ่านไฟล์: {csv_path}")
        df = pd.read_csv(csv_path)
        print(f"อ่านไฟล์สำเร็จ! พบสินค้าทั้งหมด {len(df)} รายการ\n")
        
        for index, row in df.iterrows():
            if pd.isna(row['รหัสสินค้า']) or pd.isna(row['ลิงก์สินค้า']):
                continue
                
            product_id = str(row['รหัสสินค้า']).strip()
            if product_id.endswith('.0'):
                product_id = product_id[:-2]
                
            product_name = str(row['ชื่อสินค้า'])
            product_url = str(row['ลิงก์สินค้า'])
            
            print(f"--- เริ่มคิวที่ {index+1} ---")
            print(f"สินค้า: {product_name[:40]}...")
            
            save_dir = os.path.join("assets", "products", product_id)
            ensure_dir(save_dir)
            
            # เจาะระบบดึงรูป
            img_url = scrape_shopee_image(product_url)
            
            if img_url:
                save_path = os.path.join(save_dir, "cover.jpg")
                print(f"พบรูปภาพ! กำลังดาวน์โหลด: {img_url}")
                success = download_image(img_url, save_path)
                
                if success:
                    print(f"Success: โหลดรูปลงเครื่องสำเร็จ! จัดเก็บที่: {save_path}\n")
                else:
                    print("Failed: ไม่สามารถดาวน์โหลดรูปได้\n")
            else:
                print("Failed: ไม่พบรูปภาพ (อาจจะติดระบบป้องกันของเว็บ)\n")
                
    except Exception as e:
        print(f"Critical Error: {e}")
        traceback.print_exc()

def resolve_affiliate_link(short_url):
    """
    แกะลิงก์ข้อเสนอ (Short Link) เป็น URL เต็ม 
    และดึงรหัสสินค้า, ชื่อสินค้า, สรรพคุณ จากหน้าเว็บ
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        # วิ่งตามลิงก์ไปให้ถึงปลายทาง
        res = requests.get(short_url, headers=headers, timeout=15)
        long_url = res.url
        
        # ค้นหารหัสร้านค้าและรหัสสินค้า
        m = re.search(r'/(\d+)/(\d+)', long_url)
        if not m:
            m = re.search(r'i\.(\d+)\.(\d+)', long_url)
            
        if m:
            shop_id, item_id = m.groups()
            standard_url = f'https://shopee.co.th/product/{shop_id}/{item_id}'
            
            # ดึงข้อมูลจาก URL มาตรฐาน
            res2 = requests.get(standard_url, headers=headers, timeout=15)
            soup = BeautifulSoup(res2.text, 'html.parser')
            
            t = soup.find('meta', property='og:title')
            d = soup.find('meta', property='og:description')
            
            title = t['content'] if t else ""
            desc = d['content'] if d else ""
            
            # ตรวจสอบว่าสินค้าถูกลบหรือไม่มีอยู่จริง
            if "ซื้อขายผ่านมือถือ" in title or title.strip() == "Shopee Thailand":
                print(f"⚠️ ตรวจพบว่าลิงก์สินค้านี้ 'ไม่มีอยู่จริง' หรือ 'ถูกลบไปแล้ว'")
                return None
                
            # ลบคำว่า | Shopee Thailand ออกจากชื่อ
            title = title.replace(" | Shopee Thailand", "").strip()
            
            return {
                'product_id': item_id,
                'product_name': title,
                'product_desc': desc,
                'product_url': standard_url
            }
    except Exception as e:
        print(f"Error resolving link: {e}")
        
    return None

if __name__ == "__main__":
    ensure_dir(os.path.join("assets", "products"))
    process_csv()

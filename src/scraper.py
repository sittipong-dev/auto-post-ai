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
    
    headers_list = [
        {
            "User-Agent": "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)",
            "Accept-Language": "th-TH,th;q=0.9,en;q=0.8",
        },
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "th-TH,th;q=0.9,en;q=0.8",
        }
    ]
    
    for headers in headers_list:
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                html_text = response.text
                soup = BeautifulSoup(html_text, 'html.parser')
                
                # 1. หารูปภาพหลัก (og:image) ก่อน
                og_img = soup.find('meta', property='og:image')
                if og_img and og_img.get('content'):
                    img_c = og_img['content']
                    if img_c not in image_urls:
                        image_urls.append(img_c)
                        
                # 2. ล้วงรูปภาพเพิ่มเติมจากโค้ด (ค้นหา hash รูป)
                matches = re.findall(r'down-th\.img\.susercontent\.com/file/([a-zA-Z0-9_-]+)', html_text)
                
                for m in matches:
                    # ข้ามไฟล์ที่ไม่ใช่รูปสินค้าจริง
                    if m.startswith('promo-dim') or len(m) < 15:
                        continue
                    full_url = f"https://down-th.img.susercontent.com/file/{m}"
                    if full_url not in image_urls:
                        image_urls.append(full_url)
                    
                    if len(image_urls) >= max_images:
                        break
                        
            if len(image_urls) > 1:
                break
        except Exception as e:
            print(f"Scraping Error: {e}")
            
    return image_urls

def scrape_shopee_video(url):
    print(f"Scraping Video จาก: {url}")
    headers_list = [
        {
            "User-Agent": "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)",
            "Accept-Language": "th-TH,th;q=0.9,en;q=0.8",
        },
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "th-TH,th;q=0.9,en;q=0.8",
        }
    ]
    
    for headers in headers_list:
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                html_text = response.text
                
                # 1. ค้นหาจาก video_info_list
                match = re.search(r'\"video_info_list\":\[(.*?)\]', html_text)
                if match:
                    video_json_str = match.group(1)
                    urls = re.findall(r'\"url\":\"(https://[^\"]+\.mp4)\"', video_json_str)
                    if urls:
                        print(f"พบลิงก์วิดีโอ: {urls[-1]}")
                        return urls[-1]
                        
                # 2. ค้นหาจาก URL mp4 หรือ cv.shopee โดยตรงในโค้ด
                direct_videos = re.findall(r'https://[^\s\"\'<>]+\.mp4', html_text)
                if direct_videos:
                    print(f"พบลิงก์วิดีโอตรง: {direct_videos[0]}")
                    return direct_videos[0]
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
        crawler_headers = {
            'User-Agent': 'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)',
            'Accept-Language': 'th-TH,th;q=0.9,en;q=0.8'
        }
        
        # วิ่งตามลิงก์ไปให้ถึงปลายทาง (ถ้าเป็น short link)
        if "s.shopee.co.th" in short_url or "/universal-link/" in short_url:
            res = requests.get(short_url, headers=crawler_headers, timeout=15)
            long_url = res.url
        else:
            long_url = short_url
            
        # ค้นหารหัสร้านค้าและรหัสสินค้า
        m = re.search(r'/(\d+)/(\d+)', long_url)
        if not m:
            m = re.search(r'i\.(\d+)\.(\d+)', long_url)
            
        if m:
            shop_id, item_id = m.groups()
            standard_url = f'https://shopee.co.th/product/{shop_id}/{item_id}'
            
            # ดึงข้อมูลจาก URL ด้วย Crawler Header เพื่อข้าม Anti-Bot
            res2 = requests.get(standard_url, headers=crawler_headers, timeout=15)
            soup = BeautifulSoup(res2.text, 'html.parser')
            
            t = soup.find('meta', property='og:title')
            d = soup.find('meta', property='og:description')
            
            title = t['content'] if t and t.get('content') else ""
            desc = d['content'] if d and d.get('content') else ""
            
            # ถ้า og:title ยังว่าง ลองดูจาก <title> tag
            if not title:
                title_tag = soup.find('title')
                if title_tag:
                    title = title_tag.text.strip()
            
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
        else:
            # ถ้าเป็น URL ที่ไม่มี pattern shop/item ลองดึงตรงๆ
            res2 = requests.get(long_url, headers=crawler_headers, timeout=15)
            soup = BeautifulSoup(res2.text, 'html.parser')
            t = soup.find('meta', property='og:title')
            d = soup.find('meta', property='og:description')
            title = t['content'] if t and t.get('content') else ""
            desc = d['content'] if d and d.get('content') else ""
            title = title.replace(" | Shopee Thailand", "").strip()
            if title and "Shopee Thailand" not in title:
                return {
                    'product_id': 'item',
                    'product_name': title,
                    'product_desc': desc,
                    'product_url': long_url
                }
    except Exception as e:
        print(f"Error resolving link: {e}")
        
    return None

if __name__ == "__main__":
    ensure_dir(os.path.join("assets", "products"))
    process_csv()

import pandas as pd
import os
import glob
from src.scraper import resolve_affiliate_link

def get_latest_csv(folder_path='data'):
    csv_files = glob.glob(os.path.join(folder_path, '*.csv'))
    if not csv_files: return None
    return max(csv_files, key=lambda f: max(os.path.getmtime(f), os.path.getctime(f)))

print('🔍 เริ่มต้นการทดสอบระบบ Smart Fallback (Diagnostics Mode)\n')
csv_path = get_latest_csv('data')
print(f'📂 ไฟล์ที่ระบบตรวจพบว่าใหม่ล่าสุด: {os.path.basename(csv_path)}')

try:
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
except UnicodeDecodeError:
    df = pd.read_csv(csv_path, encoding='cp874')

print(f'📋 จำนวนสินค้าที่พบในไฟล์: {len(df)} รายการ')
print('-' * 40)
if len(df) > 0:
    for i in range(min(2, len(df))): # Show up to 2 items
        row = df.iloc[i]
        if 'ลิงก์ข้อเสนอ' not in row or pd.isna(row['ลิงก์ข้อเสนอ']):
             print(f'❌ สินค้าชิ้นที่ {i+1}: ไม่มีคอลัมน์ ลิงก์ข้อเสนอ หรือข้อมูลว่างเปล่า')
        else:
             affiliate_url = str(row['ลิงก์ข้อเสนอ']).strip()
             has_full = ('ชื่อสินค้า' in row and not pd.isna(row['ชื่อสินค้า'])) and ('รหัสสินค้า' in row and not pd.isna(row['รหัสสินค้า']))
             print(f'🛒 สินค้าชิ้นที่ {i+1}:')
             if has_full:
                 print('  🟢 สถานะ: พบข้อมูลครบถ้วน (ไฟล์ปกติจาก Shopee)')
                 print(f'    - รหัสสินค้า: {row["รหัสสินค้า"]}')
                 print(f'    - ชื่อสินค้า: {str(row["ชื่อสินค้า"])[:60]}...')
             else:
                 print('  🟡 สถานะ: ข้อมูลไม่ครบ (เปิดโหมด Smart Fallback แกะลิงก์)')
                 print(f'    - ลิงก์ที่อ่านได้: {affiliate_url}')
                 print('    - กำลังทดสอบแกะลิงก์... (รอสักครู่)')
                 details = resolve_affiliate_link(affiliate_url)
                 if details:
                     print('    ✅ แกะลิงก์สำเร็จ! ข้อมูลที่ได้คือ:')
                     print(f'      🆔 รหัสสินค้า: {details["product_id"]}')
                     print(f'      🏷️ ชื่อสินค้า: {details["product_name"][:60]}...')
                     print(f'      📄 รายละเอียด: {details["product_desc"][:60]}...')
                     print(f'      🔗 ลิงก์จริง: {details["product_url"]}')
                 else: print('    ❌ แกะลิงก์ล้มเหลว')
        print('-' * 40)

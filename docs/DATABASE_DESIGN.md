# Database Design
ระบบใช้ไฟล์ CSV เป็นฐานข้อมูลหลักในเฟส MVP

## 1. Table: target_products.csv
ตารางเก็บคลังสินค้าที่ผ่านการคัดเลือก
| Column Name | Data Type | Description |
|---|---|---|
| `id` | String | รหัสสินค้า (Shopee ID) |
| `name` | String | ชื่อสินค้า |
| `price` | Float | ราคาสินค้า |
| `affiliate_link` | String | ลิงก์ที่แปลงแล้ว (Tracking URL) |
| `status` | String | PENDING, SCRAPED, RENDERED, POSTED, FAILED |

## 2. Table: short_links.csv
ตารางเก็บข้อมูลลิงก์ย่อและสถิติ
| Column Name | Data Type | Description |
|---|---|---|
| `original_link` | String | ลิงก์ Shopee |
| `short_url` | String | ลิงก์ย่อ (เช่น bit.ly/xxx) |
| `clicks` | Integer | จำนวนคลิกปัจจุบัน (อัปเดตรายสัปดาห์) |

## 3. Logs: system.log
| Format | `[YYYY-MM-DD HH:MM:SS] [LEVEL] [MODULE] Message` |

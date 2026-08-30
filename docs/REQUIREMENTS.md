# Software Requirements Specification (SRS)
**Project Name:** Auto Post AI (Ultimate Affiliate Bot)

## 1. Introduction
ระบบอัตโนมัติสำหรับทำ Affiliate Marketing โดยเน้นการสร้างวิดีโอสั้น (Reels) อัตโนมัติ เพื่อโพสต์ลง Facebook (MVP)

## 2. Functional Requirements
- **F-01 (Data Sourcing & Ingestion):** 
  - ระบบรับข้อมูลสินค้าขายดีจาก Google Sheet (บน Google Drive ที่สร้างโดย AI Radar)
  - ผู้ใช้คัดเลือกสินค้าและนำลิงก์ Shopee Affiliate บันทึกลงไฟล์ `data/target_products.csv`
  - โปรแกรมอ่านรายการสินค้าจากไฟล์ CSV แบบ Batch Processing เพื่อนำไปผลิตสื่ออัตโนมัติ
  - *เพิ่มเติม (Input Flexibility):* เมื่อพัฒนาโปรแกรมจริง ต้องออกแบบให้ผู้ใช้ป้อนข้อมูลได้ 2 ช่องทาง:
    1. **Import CSV:** โหลดไฟล์เพื่อรันงานทีละเยอะๆ
    2. **Manual Input:** มีช่องให้คีย์วางลิงก์ (Paste Links) สินค้าเองได้โดยตรง และสามารถวางทีละหลายๆ ลิงก์พร้อมกันได้
- **F-02 (Scrape):** ดึงรูปภาพความละเอียดสูง, วิดีโอ (ถ้ามี), ชื่อ, และจุดเด่นสินค้าจากลิงก์ Shopee
- **F-03 (AI Brain):** เชื่อมต่อ Gemini API เพื่อแต่งสคริปต์วิดีโอป้ายยา และเขียนแคปชั่นพร้อมแฮชแท็ก
  - *เพิ่มเติม (Style Customization):* ผู้ใช้สามารถตั้งค่าผ่านโปรแกรมให้ AI แต่งสไตล์แบบอัตโนมัติ (Auto) หรือบังคับเลือกสไตล์ที่กำหนดไว้ได้เอง (Manual) เช่น สไตล์ฮา, วิชาการ, วัยรุ่น
- **F-04 (TTS):** แปลงสคริปต์ข้อความเป็นเสียงพากย์ด้วย Edge-TTS (ภาษาไทยธรรมชาติ)
  - *เพิ่มเติม (Voice Customization):* ผู้ใช้สามารถตั้งค่าผ่านโปรแกรมเพื่อเลือกคนพากย์ (ชาย/หญิง) และปรับจังหวะการพูด (Speed) ให้กระชับขึ้นได้ตามแพลตฟอร์ม
- **F-05 (Video Factory):** สร้างคลิปวิดีโอแนวตั้ง 9:16 ด้วย MoviePy โดยรวมรูปภาพ/วิดีโอ + เสียงพากย์ + เพลงพื้นหลัง (BGM)
- **F-06 (Post & Comment):** โพสต์คลิปลง Facebook Page Reels พร้อมพิมพ์คอมเมนต์แรกแปะลิงก์ Affiliate ทันที
- **F-07 (Engagement Bot):** ตรวจจับคอมเมนต์ลูกค้า ตอบกลับอัตโนมัติ และส่งลิงก์สินค้าผ่าน DM/Inbox

## 3. Non-Functional Requirements (System Constraints & Safety)
- **N-01 (Account Warm-up):** ระบบต้องรันสคริปต์สุ่มเลื่อนหน้าจอ (Scroll) และกดไลก์ฟีดข่าว 5-10 นาทีก่อนโพสต์ เพื่อจำลองพฤติกรรมมนุษย์ ป้องกันบัญชีโดนแบน
- **N-02 (BGM Integration):** ระบบ Video Maker ต้องนำเพลงปลอดลิขสิทธิ์ (Royalty-Free) มามิกซ์เป็นพื้นหลังพร้อมกับเสียงพากย์เสมอ เพื่อให้คลิปน่าสนใจ
- **N-03 (Unoriginal Content Avoidance):** ต้องมีระบบปรับแต่งไฟล์วิดีโอ (Video Manipulation) เช่น พลิกซ้ายขวา (Mirror) หรือใส่กรอบ เพื่อหลีกเลี่ยงการโดน Facebook แบนเรื่องเนื้อหาซ้ำ
- **N-04 (Robust Error Handling):** โค้ดทุกส่วนต้องครอบด้วย `Try-Catch` หากอินเทอร์เน็ตหลุดหรือโหลดเว็บไม่ขึ้น ระบบต้องข้ามสินค้านั้นไปทำรายการถัดไปทันที และบันทึกลง `system_error.log` โดยไม่ทำให้โปรแกรมค้าง
- **N-05 (AI Rate Limiting):** โมดูล AI Brain ต้องมีฟังก์ชัน `Retry` และ `Exponential Backoff` เมื่อเรียกใช้ Gemini API เพื่อป้องกันโปรแกรมแครชหากส่งคำขอถี่เกินไป (API Rate Limits)
- **N-06 (Thai Font Rendering):** โมดูล Video Maker (MoviePy) ต้องดึงไฟล์ฟอนต์มาตรฐานภาษาไทย (เช่น `Kanit.ttf`) จากโฟลเดอร์ `assets/` มาใช้งาน เพื่อป้องกันปัญหาสระลอยหรือตัวอักษรเป็นกล่องสี่เหลี่ยม
- **N-07 (Session Validation):** โมดูล Facebook Auto Poster ต้องมีระบบ "ตรวจสอบสถานะล็อกอิน" เบื้องต้นก่อนเริ่มโพสต์ หากพบว่าคุกกี้ (Persistent Context) หมดอายุหรือหลุด ระบบจะต้องแจ้งเตือนและหยุดทำงาน ไม่ฝืนรันต่อจนเกิด Error

## 4. Directory Structure (โครงสร้างโฟลเดอร์โปรเจกต์)
เพื่อให้การเขียนโค้ดเป็นระเบียบ จะใช้โครงสร้างโฟลเดอร์ดังนี้:
```text
/auto post ai
├── /docs          (เอกสารต่างๆ ของระบบ)
├── /src           (ไฟล์ซอร์สโค้ด Python ทั้งหมด รวมถึงโมดูลต่างๆ)
├── /data          (ไฟล์ฐานข้อมูล .csv เช่น target_products.csv และ browser_profile)
├── /assets        (ไฟล์ตั้งต้น เช่น ไฟล์เพลง BGM, ฟอนต์ลายน้ำ)
├── /output        (ไฟล์วิดีโอ .mp4 ที่สร้างเสร็จแล้ว รอโพสต์)
└── .env           (ไฟล์ซ่อนสำหรับเก็บรหัส API Keys)
```

## 5. Future Roadmap (แผนพัฒนาในอนาคต)
- **Cross-Platform Auto Poster:** ขยายขีดความสามารถของบอทนักโพสต์ จากเฟสเริ่มต้น (Facebook Reels) ไปสู่แพลตฟอร์มวิดีโอสั้นอื่นๆ
  - **TikTok:** ระบบอัปโหลดคลิปอัตโนมัติพร้อมรองรับการ "ปักตะกร้า" (TikTok Shop Affiliate)
  - **Shopee Video:** ระบบอัปโหลดคลิปป้ายยาและเชื่อมโยงรหัสสินค้าเพื่อปักตะกร้าลง Shopee Video โดยตรง
    *(Note: การพยายามเจาะระบบล็อกอิน Shopee Affiliate ด้วย Playwright Stealth มีความซับซ้อนและโดนบล็อกได้ง่าย แนะนำให้ใช้ Official API หรือวิธีป้อนลิงก์แบบ Manual จะเสถียรกว่า)*
- **Dynamic Video Extraction (ดึงวิดีโอต้นฉบับแทนภาพนิ่ง):** อัปเกรดระบบ Scraper ให้ดึง "ไฟล์วิดีโอตัวอย่างสินค้า" จากร้านค้า Shopee มาใช้ทำ Reels แทนภาพนิ่ง
  - **วิธีทำ (Implementation Guide):**
    1. **Data Fetching:** ใช้ Shopee Internal API ยิงคำขอไปที่ `https://shopee.co.th/api/v4/item/get?itemid={item_id}&shopid={shop_id}`
    2. **Video Parsing:** ค้นหาตัวแปร `video_info_list` เพื่อดาวน์โหลดไฟล์ `.mp4`
    3. **Audio Replacement:** ใช้คำสั่ง `video_clip.without_audio()` ลบเสียงรบกวนต้นฉบับใน MoviePy
    4. **AI Voice Muxing:** นำเสียงพากย์ AI ภาษาไทยของเราประกบเข้าไปแทนที่ จะได้คลิปที่ดูเป็นมืออาชีพ

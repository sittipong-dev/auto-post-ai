# API Integration Design

## 1. Gemini API (Google AI Studio)
- **Endpoint:** `generativelanguage.googleapis.com`
- **Method:** POST
- **Purpose:** สร้างแคปชั่นเฟสบุ๊คและสคริปต์เสียงพากย์
- **Input:** ชื่อสินค้า, จุดเด่นสินค้า
- **Output:** JSON (caption, script)

## 2. Edge-TTS (Text-to-Speech)
- **Library:** `edge-tts` (Python)
- **Purpose:** สร้างไฟล์ MP3
- **Voice:** `th-TH-PremwadeeNeural` หรือเสียงภาษาไทยอื่นๆ

## 3. Shopee Affiliate (Web Scraping / Optional API)
- **Method:** Web Scraping (Playwright)
- **Purpose:** ดึงรูปภาพ (.jpg) และข้อมูลสินค้า
- **Fallback:** ใช้งาน Shopee Open API หากขอสิทธิ์ได้

## 4. URL Shortener API (Bit.ly)
- **Endpoint:** `api-ssl.bitly.com/v4/shorten`
- **Purpose:** ย่อลิงก์เพื่อทำ Tracking

## 5. Environment Variables (.env Configuration)
รหัสผ่านและคีย์ต่างๆ จะไม่ถูกเขียนลงในโค้ดโดยตรง แต่จะถูกเก็บไว้อย่างปลอดภัยในไฟล์ `.env` ที่ root folder:
```env
# AI Models
GEMINI_API_KEY=your_gemini_api_key_here

# URL Tracking
BITLY_API_KEY=your_bitly_access_token_here

# Social Media (Optional, if using API instead of Playwright)
# FB_PAGE_ACCESS_TOKEN=xxx
```

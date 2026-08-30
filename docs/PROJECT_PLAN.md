# Project Plan & Timeline
**ระยะเวลาโดยประมาณ:** 4 สัปดาห์ (Part-time)

## Phase 1: MVP Foundation (Week 1)
- [ ] Setup Project & Docs
- [ ] Module: Scraper (ดึงรูปและข้อมูล)
- [ ] Module: AI Brain (Gemini + TTS)
- [ ] Module: Video Maker (MoviePy)

## Phase 2: Social Automation (Week 2)
- [ ] Module: Auto Poster (Playwright login & post)
- [ ] Module: Auto Comment (แปะลิงก์)
- [ ] URL Tracking Integration

## Phase 3: Ultimate Features (Week 3)
- [ ] Module: Scout Bot (สแกนหาสินค้าขายดี)
- [ ] Module: Engagement Bot (ตอบคอมเมนต์ + DM)
- [ ] Account Warm-up System

## Phase 4: Testing & Tuning (Week 4)
- [ ] End-to-End Testing
- [ ] ปรับจูนระบบ Anti-Ban (Delay, Proxy)
- [ ] แก้ไขบั๊กและเปิดใช้งานจริง

## Risk Management & Mitigation
- **Risk 1: กฎเหล็กแพลตฟอร์ม (โดนแบน)** 
  - **Mitigation:** รันบอทบน Facebook Page เท่านั้น, ใช้เทคนิค Fingerprint, และจำกัดการโพสต์ 3-5 คลิปต่อวัน
- **Risk 2: ข้อจำกัดการดึงข้อมูลหลังบ้าน (Shopee Scraping Constraints)**
  - **ปัญหา:** การเขียนบอท Scout Bot เพื่อเข้าระบบหลังบ้านมีความท้าทายเรื่อง CAPTCHA และระบบป้องกัน
  - **Mitigation:** เตรียมแผนสำรองโดยใช้ `Persistent Context` (เซฟคุกกี้ของผู้ใช้) เพื่อข้ามหน้าล็อกอิน หรือเปลี่ยนไปใช้ Official API หากเป็นไปได้

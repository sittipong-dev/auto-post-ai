# TODO & Task List

- [x] **Task 1:** สร้าง Environment (Virtual Env), ไฟล์ `.env` และ `requirements.txt`
- [x] **Task 2:** จัดเตรียมโครงสร้างโฟลเดอร์ (`/src`, `/data`, `/assets`, `/output`)
- [x] **Task 3:** ติดตั้งไลบรารี: `playwright`, `moviepy`, `google-generativeai`, `edge-tts`, `pandas`, `python-dotenv`
- [x] **Task 4:** สมัคร Google AI Studio และนำ API Key มาใส่ในไฟล์ `.env`
- [x] **Task 5 (Initial Login):** เขียนสคริปต์ `setup_login.py` และล็อกอิน Facebook เพื่อเซฟคุกกี้ (Persistent Context) สำเร็จ
- [ ] **Task 6 (CSV Reader & Scraper):** เขียนโมดูลอ่านไฟล์ `data/target_products.csv` และเขียนโค้ด `src/scraper.py` เพื่อดึงรูปภาพ/ข้อมูลสินค้า
- [ ] **Task 7 (AI Brain & TTS):** เขียนโมดูล `src/ai_gen.py` เชื่อมต่อ Gemini และแปลงเสียงด้วย Edge-TTS
- [ ] **Task 8 (Video Maker):** เขียนโมดูล `src/video_maker.py` ตัดต่อวิดีโอ 9:16 + ใส่เพลง BGM + พลิกภาพกันซ้ำ
- [ ] **Task 9 (FB Auto Poster):** เขียนโมดูล `src/fb_poster.py` วอร์มบัญชี อัปโหลด Reels และคอมเมนต์ลิงก์
- [ ] **Task 10 (Pipeline Integration):** รวมทุกโมดูลเข้าด้วยกันใน `src/main.py` หรือ `run_autopost.py` เพื่อรันแบบ Batch

# 🥭 DurionBot — ระบบช่วยเกษตรกรทุเรียน (อ.พิปูน จ.นครศรีธรรมราช)

> **เป้าหมาย**: ให้เกษตรกรใช้ LINE chat ถามเรื่อง ฝน ราคา ปุ๋ย โรค → ได้คำตอบทันทีฟรี ไม่ต้องเดินดู เซนเซอร์ ไม่ต้องจ้างใคร

---

## 🏗️ สถาปัตยกรรมระบบ (Architecture)

```
┌─────────────────────────────────────────────────────────────────────┐
│                  เกษตรกร (LINE app บนมือถือ)                       │
│                  พิมพ์: "ฝนตกพรุ่งนี้ไหม" / ส่งรูปใบทุเรียน         │
└──────────────────────────┬──────────────────────────────────────────┘
                           │ LINE Messaging API (ฟรี - reply ไม่นับโควต้า)
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│           Cloudflare Worker (ฟรี 100,000 req/วัน)                  │
│   - รับ webhook จาก LINE                                            │
│   - แยกประเภทคำถาม (intent classifier - rule-based, ไม่ใช้ AI)     │
│   - ดึงข้อมูลจาก KV store (cache 24 ชม.)                           │
│   - ตอบกลับเป็น Flex Message (กราฟ/ตาราง/รูป)                      │
└──────────┬──────────────────────────────────┬───────────────────────┘
           │                                  │
           │ ข้อความ/ราคา/ฝน                  │ รูปโรค → upload
           │ (ตอบจาก cache ทันที)             │
           ▼                                  ▼
┌──────────────────────┐         ┌──────────────────────────────────┐
│ Cloudflare KV/D1     │         │ Ollama Server (PC ที่บ้าน)      │
│ (cache ฟรี)          │         │ - llava:7b → วินิจฉัยโรคจากรูป  │
│ - ราคาทุเรียนวันนี้  │         │ - llama3.2 → ตอบคำถามทั่วไป     │
│ - ฝน 7 วัน           │         │ - ฟรี 100% รันบนเครื่องตัวเอง   │
│ - ราคาปุ๋ย           │         │ - Cloudflare Tunnel (ฟรี)       │
└──────────▲───────────┘         └──────────────────────────────────┘
           │
           │ อัปเดตทุก 6 ชม.
           │
┌──────────┴──────────────────────────────────────────────────────────┐
│              GitHub Actions (ฟรี 2,000 นาที/เดือน)                  │
│   Cron job รัน scrapers ทุก 6 ชม.:                                  │
│   - TMD API → ดึงพยากรณ์ฝน ต.ควนกลาง อ.พิปูน                       │
│   - talaadthai.com / kasetprice.com → ราคาทุเรียน                  │
│   - rakayang.net → ราคายาง 5 ตลาด                                  │
│   - moc.go.th → ราคาปุ๋ยเปรียบเทียบยี่ห้อ                          │
│   - YouTube/TikTok RSS → เก็บวิดีโอใหม่ตามคำค้น                    │
│   → push อัปเดตเข้า GitHub repo + push ขึ้น KV                      │
└─────────────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                GitHub Repo (vault/) — Obsidian-compatible           │
│   ทุกไฟล์เป็น .md → เปิดใน Obsidian บน PC ดูได้ + Git versioning   │
│   - vault/09-daily-data/2026-04-25-rain.md                          │
│   - vault/09-daily-data/2026-04-25-prices.md                        │
│   - vault/05-market/trends-monthly.md (สรุปแนวโน้ม)                │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 💰 ค่าใช้จ่ายทั้งระบบ = **0 บาท/เดือน**

| ส่วนประกอบ | บริการ | ราคา | เงื่อนไข |
|----|----|----|----|
| LINE Bot | LINE Messaging API | **ฟรี** | reply ไม่นับโควต้า, push 200 ข้อความ/เดือน |
| Backend | Cloudflare Workers | **ฟรี** | 100,000 request/วัน |
| Database | Cloudflare KV + D1 | **ฟรี** | KV 1GB / D1 5GB |
| Cron jobs | GitHub Actions | **ฟรี** | 2,000 นาที/เดือน (เราใช้ ~120 นาที) |
| AI วินิจฉัยโรค | Ollama (llava:7b) | **ฟรี** | รันบน PC ที่บ้าน, RAM 8GB ขึ้นไป |
| AI Tunnel | Cloudflare Tunnel | **ฟรี** | unlimited bandwidth |
| Hosting Wiki | GitHub Pages | **ฟรี** | unlimited public repo |
| **TOTAL** | | **0 บาท** | |

> **เปรียบเทียบ**: ถ้าใช้ Claude API ตอบทุกคำถาม จะตก ~3,000–8,000 บาท/เดือน  
> เราใช้ rule-based + cache + Ollama แทน → ประหยัด 100%

---

## 📋 ฟีเจอร์ที่รองรับ (ตอบโจทย์ที่คุณต้องการ)

| # | ฟีเจอร์ | สถานะ | Token Claude ที่ใช้/คำถาม |
|---|---------|--------|---------------------|
| 1 | 🌧️ พยากรณ์ฝน ต.ควนกลาง อ.พิปูน นครศรีฯ ล่วงหน้า 7 วัน | ✅ | 0 (ดึงจาก TMD API) |
| 2 | 🍈 ราคาทุเรียน 4 พันธุ์ + แนวโน้ม + ทำนายช่วงราคาดี | ✅ | 0 (cache + กราฟ) |
| 3 | 🌳 ราคายางพารา 5 ตลาด | ✅ | 0 (cache) |
| 4 | 🌱 ราคาปุ๋ยเปรียบเทียบยี่ห้อ (15-15-15, 16-16-16, 13-13-21) | ✅ | 0 (cache) |
| 5 | 🦠 วินิจฉัยโรคทุเรียนจากรูปภาพ | ✅ | 0 (ใช้ Ollama llava ที่บ้าน) |
| 6 | 📝 วินิจฉัยโรคจากคำอธิบาย | ✅ | 0 (ใช้ Ollama llama3) |
| 7 | 🤖 LINE Chat ฟรีไม่จำกัด | ✅ | 0 (reply messages) |
| 8 | 📺 ดึงวิดีโอ YouTube/TikTok ใหม่ทุกวัน auto | ✅ | 0 (RSS feed) |
| 9 | 📊 Dashboard ใน Obsidian บน PC | ✅ | 0 |

---

## 🚀 ขั้นตอนการติดตั้งโดยรวม (Master Checklist)

ทำตามลำดับ — แต่ละขั้นมี guide ละเอียดในโฟลเดอร์ `docs/`:

- [ ] **1. ติดตั้ง Ollama บน PC ที่บ้าน** → [docs/01-setup-ollama.md](docs/01-setup-ollama.md) — 30 นาที
- [ ] **2. สมัคร Cloudflare + ทำ Tunnel** → [docs/02-setup-cloudflare.md](docs/02-setup-cloudflare.md) — 20 นาที
- [ ] **3. สร้าง LINE Official Account + Bot** → [docs/03-setup-line-bot.md](docs/03-setup-line-bot.md) — 30 นาที
- [ ] **4. Deploy Cloudflare Worker** → [docs/04-deploy-worker.md](docs/04-deploy-worker.md) — 15 นาที
- [ ] **5. ขอ TMD API key** → [docs/05-tmd-api.md](docs/05-tmd-api.md) — รอ 1-2 วัน
- [ ] **6. Setup GitHub Actions cron** → [docs/06-github-actions.md](docs/06-github-actions.md) — 15 นาที
- [ ] **7. ติดตั้ง Obsidian บน PC** → [docs/07-obsidian.md](docs/07-obsidian.md) — 10 นาที
- [ ] **8. ทดสอบทั้งระบบ** → [docs/08-testing.md](docs/08-testing.md) — 30 นาที

**รวมเวลาติดตั้ง: ~3 ชั่วโมง (ไม่นับเวลารอ TMD)**

---

## 📂 โครงสร้างโปรเจคนี้

```
durionbot/
├── README.md                    ← ไฟล์นี้
├── docs/                        ← คู่มือ step-by-step ทุกขั้นตอน
│   ├── 01-setup-ollama.md
│   ├── 02-setup-cloudflare.md
│   ├── 03-setup-line-bot.md
│   ├── 04-deploy-worker.md
│   ├── 05-tmd-api.md
│   ├── 06-github-actions.md
│   ├── 07-obsidian.md
│   └── 08-testing.md
├── workers/                     ← Cloudflare Worker code
│   ├── src/index.js             ← LINE webhook handler
│   ├── src/intent.js            ← จำแนกประเภทคำถาม (no AI)
│   ├── src/handlers/            ← logic แต่ละหัวข้อ
│   └── wrangler.toml            ← config
├── scrapers/                    ← Python scripts ดึงข้อมูล
│   ├── scrape_tmd.py            ← ฝน
│   ├── scrape_durian_price.py   ← ราคาทุเรียน
│   ├── scrape_rubber.py         ← ราคายาง
│   ├── scrape_fertilizer.py     ← ราคาปุ๋ย
│   ├── scrape_youtube.py        ← วิดีโอใหม่
│   └── scrape_tiktok.py         ← TikTok
├── line-bot/                    ← LINE Flex Message templates
│   ├── flex_weather.json
│   ├── flex_price.json
│   └── flex_disease.json
├── disease-ai/                  ← Ollama prompts + image classifier
│   ├── prompts/
│   ├── ollama_server.py         ← FastAPI wrap Ollama
│   └── disease_knowledge.md
├── scripts/                     ← utility scripts
│   ├── deploy.sh
│   └── test_all.sh
└── obsidian-vault/              ← Wiki (เปิดใน Obsidian)
    ├── 01-diseases/             ← ข้อมูลโรค (จากเดิม + เพิ่ม)
    ├── 02-cultivation/          ← การเพาะปลูก
    ├── 05-market/               ← ราคาและตลาด
    ├── 06-weather/              ← สภาพอากาศ
    ├── 08-sources/              ← แหล่งข้อมูล
    ├── 09-daily-data/           ← ข้อมูลรายวัน (auto-generated)
    └── 10-ai-prompts/           ← prompt template สำหรับ Ollama
```

---

## 🎯 จุดเด่นของระบบ (ทำไมออกแบบแบบนี้)

### 1. **ทำไมไม่ใช้ Claude API ทั้งหมด?**
Claude เก่งจริง แต่ค่า token แพง การถามราคาทุเรียน ฝน ปุ๋ย เป็นข้อมูล structured ดึงจาก API ตรงได้เลย ไม่ต้องให้ AI ตอบ → **ประหยัด 95%**

### 2. **ทำไมใช้ Ollama (local) ไม่ใช่ ChatGPT free?**
- ChatGPT free จำกัด ใช้นานๆ โดน rate limit
- Ollama รันที่ PC = ฟรีไม่จำกัด ใช้ llava วินิจฉัยภาพได้
- ข้อมูลรูปสวนของเกษตรกรไม่ต้องส่งออกนอกบ้าน = privacy ดี

### 3. **ทำไม LINE Bot?**
- เกษตรกรไทย 95% มี LINE อยู่แล้ว → **ไม่ต้องโหลดแอปใหม่**
- Reply messages ฟรีไม่จำกัด (ไม่กิน 200 quota/เดือน)
- ส่ง Flex Message → กราฟ ตาราง รูป ดูง่าย

### 4. **ทำไมต้อง cache?**
ข้อมูลฝน/ราคา ไม่ได้เปลี่ยนทุกวินาที → cache 6 ชม. ได้ ลด API call 99%

### 5. **ทำไมเก็บใน Obsidian Wiki?**
- ของเดิมใช้ Obsidian อยู่แล้ว → ต่อยอดง่าย
- Markdown = readable + Git versioning ได้
- ดึงดู graph view เห็นความสัมพันธ์โรค-สภาพอากาศ-ราคา ได้

---

## 📞 ตัวอย่างการใช้งานจริง

**เช้าวันจันทร์ 6 โมง เกษตรกรเปิด LINE:**

```
👨‍🌾 เกษตรกร: "ฝนวันนี้"
🤖 Bot: [Flex Card]
        🌧️ ต.ควนกลาง อ.พิปูน
        วันนี้ 25/04 - มีฝน 70% ปริมาณ 15-25 มม.
        พรุ่งนี้ 26/04 - ฝนเล็กน้อย 30%
        คำแนะนำ: เลื่อนพ่นยา รอหลังฝน
        [กราฟ 7 วัน]

👨‍🌾 เกษตรกร: "ราคาทุเรียน"
🤖 Bot: [Flex Card]
        🍈 ราคาหมอนทอง วันนี้
        เบอร์ใหญ่: 145-160 บ./กก. ↑ +5
        เบอร์เล็ก: 95-110 บ./กก. ↑ +3
        แนวโน้มเดือนนี้: ขาขึ้น 📈
        ช่วงดีที่สุด: ปลายเดือน พ.ค. (คาด 175-190)

👨‍🌾 เกษตรกร: [ส่งรูปใบทุเรียนมีจุดสีน้ำตาล]
🤖 Bot: [กำลังวิเคราะห์รูป...]
        🦠 น่าจะเป็น: โรคใบจุดสาหร่าย (Algal leaf spot)
        ความมั่นใจ: ปานกลาง
        วิธีแก้:
        1. ตัดใบที่เป็นทิ้ง เผาทำลาย
        2. พ่น คอปเปอร์ออกซีคลอไรด์ 80% WP
           อัตรา 30-40 ก./น้ำ 20 ลิตร
        3. ทุก 7-10 วัน 2-3 ครั้ง
        ⚠️ พบในช่วงฝนตกชื้น แนะนำตัดแต่งกิ่งให้โปร่ง
```

---

## 🆘 ขอความช่วยเหลือ / มีปัญหา

อ่าน [docs/troubleshooting.md](docs/troubleshooting.md) หรือ Issue ใน GitHub repo

---

**ต่อไปอ่าน**: [docs/01-setup-ollama.md](docs/01-setup-ollama.md) เพื่อเริ่มติดตั้ง 🚀

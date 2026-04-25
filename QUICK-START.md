# 🚀 Quick Start (สำหรับคนใจร้อน)

> ติดตั้งใช้งานเบื้องต้นใน 30 นาที (ยังไม่รวม Ollama + รอ TMD)

---

## ⚡ Path สำหรับลองเร็วๆ (Demo Mode)

ใช้แค่ LINE Bot + ราคาทุเรียน static + ฝนจาก Open-Meteo (ไม่ต้องรอ TMD)

### 1. Clone repo + setup Cloudflare (10 นาที)
```bash
git clone https://github.com/YOU/durionbot.git
cd durionbot

# ติดตั้ง wrangler
npm install -g wrangler
wrangler login

# สร้าง KV
wrangler kv:namespace create DURIONBOT_KV
# คัดลอก ID ใส่ใน workers/wrangler.toml
```

### 2. Setup LINE Bot (10 นาที)
ทำตาม [docs/03-setup-line-bot.md](docs/03-setup-line-bot.md) — ข้ามส่วน Rich Menu ก่อนได้

### 3. Deploy Worker (5 นาที)
```bash
cd workers
wrangler secret put LINE_CHANNEL_SECRET
wrangler secret put LINE_CHANNEL_ACCESS_TOKEN
# Ollama URL ใส่ dummy ก่อน (จะ disable disease feature)
echo "dummy" | wrangler secret put OLLAMA_TUNNEL_URL

npm run deploy
```

### 4. Run scrapers ครั้งแรก (5 นาที)
```bash
cd ../scrapers
pip install -r requirements.txt

# ตั้ง env vars (export ก่อนรัน)
export CF_ACCOUNT_ID=xxx
export CF_API_TOKEN=xxx
export CF_KV_NAMESPACE_ID=xxx

# รัน
python scrape_tmd.py        # ใช้ Open-Meteo fallback
python scrape_durian_price.py  # static prices ตามฤดูกาล
python scrape_rubber.py
python scrape_fertilizer.py
python push_to_kv.py
```

### 5. ทดสอบ LINE
- เพิ่ม Bot เป็นเพื่อน
- พิมพ์ `ฝน` → ควรได้พยากรณ์
- พิมพ์ `ราคาทุเรียน` → ได้ราคา

### 6. Setup GitHub Actions ทีหลัง
ทำตาม [docs/06-github-actions.md](docs/06-github-actions.md) แล้ว scraper จะรัน auto ทุก 6 ชม.

---

## 🐢 Path เต็มระบบ (3 ชั่วโมง)

ทำตามลำดับ:
1. [docs/01-setup-ollama.md](docs/01-setup-ollama.md) — 30 นาที
2. [docs/02-setup-cloudflare.md](docs/02-setup-cloudflare.md) — 20 นาที
3. [docs/03-setup-line-bot.md](docs/03-setup-line-bot.md) — 30 นาที
4. [docs/04-deploy-worker.md](docs/04-deploy-worker.md) — 15 นาที
5. [docs/05-tmd-api.md](docs/05-tmd-api.md) — 10 นาที (รอ 1-2 วัน)
6. [docs/06-github-actions.md](docs/06-github-actions.md) — 15 นาที
7. [docs/07-obsidian.md](docs/07-obsidian.md) — 10 นาที
8. [docs/08-testing.md](docs/08-testing.md) — 30 นาที

---

## ❓ ติดปัญหา

ดู [docs/troubleshooting.md](docs/troubleshooting.md)

ถ้ายังไม่ได้ — เปิด GitHub Issue หรือ ส่ง screenshot มาถาม

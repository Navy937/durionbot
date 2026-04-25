# Scrapers

Python scripts ดึงข้อมูลจาก data sources ต่างๆ

## ติดตั้ง
```bash
pip install -r requirements.txt
```

## วิธีรันทีละตัว

```bash
# Weather (TMD or Open-Meteo fallback)
TMD_API_KEY=xxx python scrape_tmd.py

# Durian price
python scrape_durian_price.py

# Rubber price
python scrape_rubber.py

# Fertilizer price
python scrape_fertilizer.py

# YouTube videos
YOUTUBE_API_KEY=xxx python scrape_youtube.py

# TikTok bookmarks (manual entry only)
python scrape_tiktok.py

# Push ทั้งหมดขึ้น Cloudflare KV
CF_ACCOUNT_ID=xxx CF_API_TOKEN=xxx CF_KV_NAMESPACE_ID=xxx python push_to_kv.py
```

## Output

ทุก scraper จะเขียน:
- `obsidian-vault/09-daily-data/<topic>.json` (consumed by Worker via KV)
- `obsidian-vault/09-daily-data/YYYY-MM-DD-<topic>.md` (readable in Obsidian)

## ปัญหาที่พบบ่อย

ดู [docs/troubleshooting.md](../docs/troubleshooting.md)

## เพิ่ม scraper ใหม่

1. สร้าง `scrape_<topic>.py`
2. Output JSON → `obsidian-vault/09-daily-data/<topic>.json`
3. เพิ่ม mapping ใน `push_to_kv.py`
4. เพิ่ม step ใน `.github/workflows/scrape.yml`
5. เขียน handler ใน `workers/src/handlers/`
6. เพิ่ม intent keyword ใน `workers/src/intent.js`

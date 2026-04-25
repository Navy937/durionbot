---
title: ตัวอย่างข้อมูลรายวัน
category: 09-daily-data
tags: [auto, scraped]
---

# 📊 09 - Daily Data (auto-generated)

⚠️ **ห้ามแก้ไฟล์ในโฟลเดอร์นี้ด้วยมือ** — จะถูก scraper เขียนทับ

ไฟล์ในโฟลเดอร์นี้สร้างโดย GitHub Actions cron ทุก 6 ชั่วโมง:

| ไฟล์ | สร้างโดย | KV key |
|------|----------|--------|
| `weather.json` | `scrape_tmd.py` | `weather:khuanklang` |
| `durian-price.json` | `scrape_durian_price.py` | `durian:price` |
| `durian-price-history.json` | (history rolling 30 วัน) | (ไม่ push KV) |
| `rubber-price.json` | `scrape_rubber.py` | `rubber:price` |
| `fertilizer-price.json` | `scrape_fertilizer.py` | `fertilizer:price` |
| `youtube-new-videos.json` | `scrape_youtube.py` | (ไม่ push KV) |
| `tiktok-bookmarks.json` | `scrape_tiktok.py` | (ไม่ push KV) |
| `YYYY-MM-DD-*.md` | scraper แต่ละตัว เขียน markdown ให้ Obsidian อ่าน | - |

---

## 🔍 ใช้ข้อมูลใน folder นี้ทำอะไรได้

ใน Obsidian:
1. เปิด `DASHBOARD.md` → ดู Dataview query ที่ดึงข้อมูลที่นี่
2. ทำ chart ด้วย plugin **Charts**: ราคาทุเรียน 30 วัน

ใน LINE Bot:
- Worker ดึงตรงจาก KV ที่ scraper push ไว้

ใน Python อื่นๆ:
```python
import json
with open("obsidian-vault/09-daily-data/weather.json") as f:
    data = json.load(f)
```

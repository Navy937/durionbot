# 📘 08 — ทดสอบทั้งระบบ End-to-End

> **เวลาที่ใช้**: 30 นาที

---

## 🧪 Test Plan

| # | Test Case | คำสั่ง | ผลที่คาดหวัง | คะแนน |
|---|---|---|---|---|
| 1 | Help menu | "ช่วย" | Flex card 6 ปุ่ม | __ |
| 2 | Weather today | "ฝน" | Card พยากรณ์วันนี้ | __ |
| 3 | Weather 7 days | "ฝน 7 วัน" | Carousel 7 ใบ | __ |
| 4 | Durian price | "ราคาหมอนทอง" | ราคา + แนวโน้ม + ทำนาย | __ |
| 5 | Rubber price | "ราคายาง" | 5 ตลาด | __ |
| 6 | Fertilizer picker | "ปุ๋ย" | ปุ่มเลือกสูตร | __ |
| 7 | Fertilizer compare | "ปุ๋ย 15-15-15" | เปรียบเทียบยี่ห้อ | __ |
| 8 | Disease text | "ใบทุเรียนมีจุดสีน้ำตาล" | วินิจฉัย | __ |
| 9 | Disease image | ส่งรูปใบเป็นโรค | วินิจฉัย + แนะวิธีแก้ | __ |
| 10 | Unknown | "วันนี้กินอะไรดี" | บอก commands | __ |

---

## 🔍 ทดสอบทีละส่วน

### A. Test Worker (Cloudflare)

```bash
# health check
curl https://durionbot.YOUR-NAME.workers.dev/health
# → OK
```

ดู log ตอนทดสอบ:
```bash
cd durionbot/workers
wrangler tail
```

แล้วเปิด LINE พิมพ์ทดสอบ — ดู log ทุกการ request

---

### B. Test KV ว่ามีข้อมูล

```bash
# list keys
wrangler kv:key list --binding DURIONBOT_KV

# ดูค่า
wrangler kv:key get "weather:khuanklang" --binding DURIONBOT_KV
wrangler kv:key get "durian:price" --binding DURIONBOT_KV
wrangler kv:key get "rubber:price" --binding DURIONBOT_KV
wrangler kv:key get "fertilizer:price" --binding DURIONBOT_KV
wrangler kv:key get "diseases:kb" --binding DURIONBOT_KV
```

ถ้า key ไหนไม่มี → GitHub Actions ยังไม่ได้รัน หรือ scraper ตัวนั้นมีปัญหา

---

### C. Test Ollama (ที่บ้าน)

```bash
# ตรวจ Ollama รัน
curl http://localhost:11434/api/tags

# ตรวจ wrapper API
curl http://localhost:8000/health

# ทดสอบ diagnose ข้อความ
curl -X POST http://localhost:8000/diagnose \
  -H "Content-Type: application/json" \
  -d '{"description":"ใบทุเรียนมีจุดสีน้ำตาล","mode":"text"}'

# ทดสอบ diagnose รูป
curl -X POST http://localhost:8000/diagnose \
  -H "Content-Type: application/json" \
  -d '{"image_base64":"...","mode":"image"}'
```

---

### D. Test Tunnel (จาก internet → PC ที่บ้าน)

```bash
# จากเครื่องอื่น (เช่น มือถือ tethering)
curl https://durionbot-ai.YOUR-DOMAIN.com/health

# ถ้าได้ → tunnel ทำงาน
# ถ้าไม่ได้ → ตรวจ cloudflared status
```

ใน Cloudflare dashboard:
- Zero Trust → Networks → Tunnels → ดู status

---

### E. Test GitHub Actions

ไป repo → tab Actions → Run workflow manually

ดู log แต่ละ step:
- ✅ scrape_tmd
- ✅ scrape_durian
- ✅ scrape_rubber
- ✅ scrape_fertilizer
- ✅ scrape_youtube
- ✅ push_to_kv
- ✅ commit_data

---

## 🐛 Common Issues

### "ฝน" ไม่ตอบ
1. `wrangler tail` ดู log
2. ถ้า log ขึ้น "ข้อมูลพยากรณ์ฝนยังไม่พร้อม" → KV ว่าง → run GH Actions
3. ถ้า log error "TypeError: env.DURIONBOT_KV.get is not a function" → KV binding ผิด → ตรวจ wrangler.toml

### ราคาทุเรียนไม่ขึ้น
- scraper อาจถูก block (talaadthai, kasetprice เปลี่ยน HTML)
- ดู log ใน GH Actions → fix selector
- ใช้ Open Data APIs (data.moc.go.th) เป็น fallback

### Disease (image) timeout
- LINE timeout 5 วินาที — Ollama llava ใช้เวลา ~10-30 วินาที
- เราใส่ workaround: ตอบ "กำลังประมวลผล..." ทันที + ส่ง follow-up message ผ่าน push API
- หรือ pre-process ให้รูปเล็กลง (resize 512x512) ก่อนส่ง

### Bot ไม่เห็น "ปุ๋ย 15-15-15"
- ดู `intent.js` keyword matching
- "ปุ๋ย" + "15-15-15" → ต้อง match ทั้งคู่ — ถ้าไม่ → debug `classifyIntent("ปุ๋ย 15-15-15")`

---

## 📊 Performance Targets

| Metric | Target | ความเป็นจริง |
|---|---|---|
| Reply latency (ข้อความ) | < 1 วิ | ~200-500 ms |
| Reply latency (รูป) | < 5 วิ | 8-20 วิ (Ollama ช้า) |
| Worker cost/เดือน | 0 บาท | ✓ |
| Token Claude/เดือน | 0 | ✓ |
| Uptime | > 99% | ขึ้นกับ PC ที่บ้าน |

---

## 🎉 ระบบพร้อมใช้!

ส่ง QR code ของ LINE OA ให้เพื่อนเกษตรกรในชุมชน → ใช้ฟรีกัน 🚀

หา bug? → ดู [docs/troubleshooting.md](troubleshooting.md)

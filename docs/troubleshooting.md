# 🆘 Troubleshooting

## ปัญหาที่พบบ่อยและวิธีแก้

---

## 🌧️ Weather

### "ข้อมูลพยากรณ์ยังไม่พร้อม"
- **สาเหตุ**: KV ว่าง
- **แก้**: รัน GitHub Action manually ครั้งหนึ่ง → `Actions tab → Run workflow`

### TMD API ตอบ 401 Unauthorized
- **สาเหตุ**: API key ผิด/หมดอายุ
- **แก้**: 
  - ตรวจ secret `TMD_API_KEY` ใน GitHub
  - ถ้ายังไม่ได้ key — ใช้ Open-Meteo เป็น fallback (ไม่ต้องสมัคร)

### พยากรณ์ผิดกับสภาพจริง
- **เป็นปกติ** — TMD แม่น ~70% สำหรับฝน 24 ชม.
- ถ้าแม่นกว่านี้ → ลองรวมหลาย source (ensemble)

---

## 🍈 ราคาทุเรียน

### ราคาไม่ตรงกับตลาดในพื้นที่
- ตลาดไท/สี่มุมเมือง = ราคาขายส่งกรุงเทพฯ (สูงกว่าราคา**ที่สวน**ในนครฯ)
- เพิ่ม scraper ดึงราคาจาก facebook กลุ่มทุเรียนพิปูน (manual entry ก็ได้)

### Scraper ดึงข้อมูลไม่ได้
- เว็บอาจเปลี่ยน HTML structure
- เปิด `scrapers/scrape_durian_price.py` → debug selector
- อีกทางเลือก: ใช้ MOC Open Data API ตรง (เสถียรกว่า)

---

## 🦠 Disease AI

### Ollama ตอบช้ามาก (>30 วินาที)
- **สาเหตุ**: รันบน CPU ไม่มี GPU
- **แก้สั้นๆ**:
  - ใช้โมเดลเล็กลง: `ollama pull llava:7b-q4_0`
  - ลด context: `--context-window 2048`
- **แก้ยาว**: ใช้ GPU (NVIDIA RTX 3060+ ทำงาน 5-10 เท่าเร็วกว่า)

### ตอบไม่ถูกโรค
- llava ไม่ได้เทรนกับโรคทุเรียนโดยเฉพาะ → "เดาเก่ง" เท่านั้น
- **แก้**: เพิ่ม prompt template ให้ละเอียด (ดู `disease-ai/prompts/`)
- **แก้ระยะยาว**: fine-tune ด้วยรูปโรคจริง 200+ รูป (ใช้ Unsloth/LoRA)

### LINE timeout เพราะ Ollama ช้า
- LINE webhook timeout = 5 วิ
- Ollama image diagnosis = 10-30 วิ
- **แก้ที่เราทำใน code**:
  1. ตอบ "กำลังประมวลผล..." ทันที (≤1 วิ)
  2. ส่ง follow-up ผ่าน push API หลัง Ollama เสร็จ (กิน 1 quota จาก 200)

---

## 🤖 LINE Bot

### ไม่ตอบเลย
1. `wrangler tail` — มี log เข้าไหม?
2. ถ้าไม่มี: Webhook URL ใน LINE Console ผิด → re-verify
3. ถ้ามี error: 
   - "Invalid signature" → CHANNEL_SECRET ผิด
   - "Cannot read property of undefined" → handler bug → ดู stack trace

### โควต้าหมด
- ตรวจที่ LINE OA Manager → Insights
- เราใช้แต่ reply → ไม่กิน quota
- ถ้ากิน quota = code ส่ง push ไหนสักที่ → grep "push" ใน workers/

### Bot ไม่เห็นรูป
- ดู event type ใน log: ควรเป็น `message.type === 'image'`
- LINE จะส่ง image messageId ให้ เราดึง content เอง (ผ่าน getMessageContent)
- ถ้า content เป็น 0 byte → LINE delete รูปแล้ว (เก่ากว่า 7 วัน)

---

## ☁️ Cloudflare

### Worker request เกินโควต้า
- ฟรี = 100k req/วัน
- ปกติ Bot 1 ตัวกินไม่เกิน 1k req/วัน
- ถ้าเกิน → มีคน DDoS หรือมี bug retry loop → ดู `wrangler tail`

### Tunnel offline
- PC ที่บ้านดับ → ตรวจ
- cloudflared service ตาย → `sudo systemctl restart cloudflared`
- ใช้ Cloudflare dashboard → Zero Trust → Tunnels → ดู status

### KV write failed
- KV ฟรี = 1000 writes/วัน
- ปกติเราเขียน 6 ครั้ง/วัน × 5 keys = 30 writes/วัน → ห่างไกล limit
- ถ้าเกิน → มี loop bug

---

## 📦 GitHub Actions

### Workflow fail
- ดู log step ที่ fail
- common: 
  - "secret not found" → ตรวจ secrets ใน Repo Settings
  - "ModuleNotFoundError" → requirements.txt ขาด → เพิ่ม + commit
  - "API rate limit" → TMD/MOC จำกัด — ลด frequency

### Workflow ไม่รัน schedule
- GitHub ระงับ schedule ของ public repo ที่ไม่มี activity > 60 วัน
- **แก้**: commit อะไรก็ได้สักครั้ง/2 เดือน (auto by scraper เพราะ commit data ทุก 6 ชม. = ไม่มีปัญหา)

---

## 🍃 Obsidian

### Graph view ว่าง
- ยังไม่มี wiki link `[[..]]` ในไฟล์
- เพิ่ม link ระหว่างไฟล์: เช่นใน `01-diseases/ใบไหม้.md` ใส่ `[[06-weather/ฝน-เดือนกรกฎาคม]]`

### Dataview query ไม่ทำงาน
- ตรวจ frontmatter ของไฟล์ data — ต้องมี `category:` field
- ตรวจ syntax — ใช้ ` ```dataview ` ไม่ใช่ ` ```dataviewjs `

---

## 🚨 Emergency: ทุกอย่างล่ม

ลำดับการ debug:
1. LINE Bot ตอบไหม? → No → ปัญหา Worker หรือ Webhook
2. Worker tail มี log? → No → Webhook URL ผิด หรือ LINE config ผิด
3. มี log แต่ KV ว่าง? → run GH Actions manually
4. Image diagnose ใช้ไม่ได้? → ตรวจ Ollama + Tunnel ตามลำดับ

---

## 📞 Resources

- LINE Developers community: https://www.facebook.com/groups/linedevth
- Cloudflare Discord: https://discord.cloudflare.com/
- Ollama GitHub Discussions: https://github.com/ollama/ollama/discussions
- TMD email: info_service@tmd.go.th

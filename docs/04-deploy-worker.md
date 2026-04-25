# 📘 04 — Deploy Cloudflare Worker

> **เวลาที่ใช้**: 15 นาที (หลังเสร็จ docs 01–03)

---

## ขั้นตอนที่ 1: เปิด terminal ที่โฟลเดอร์ workers/

```bash
cd durionbot/workers
npm install
```

---

## ขั้นตอนที่ 2: ใส่ KV ID ใน wrangler.toml

แก้ไฟล์ `wrangler.toml` ที่บรรทัด:

```toml
[[kv_namespaces]]
binding = "DURIONBOT_KV"
id = "REPLACE_WITH_YOUR_KV_ID"          # ← ใส่ ID ที่ได้จาก doc 02
preview_id = "REPLACE_WITH_PREVIEW_ID"
```

ใส่ ID จากที่ได้ตอนรัน `wrangler kv:namespace create` ใน docs/02

---

## ขั้นตอนที่ 3: ตั้ง secrets

```bash
wrangler secret put LINE_CHANNEL_SECRET
# ใส่ค่าจาก LINE Developers Console (doc 03)

wrangler secret put LINE_CHANNEL_ACCESS_TOKEN
# ใส่ Channel access token

wrangler secret put OLLAMA_TUNNEL_URL
# ใส่ URL จาก Cloudflare Tunnel เช่น https://durionbot-ai.YOUR-DOMAIN.com
# หรือ https://random-name.trycloudflare.com (ถ้าใช้ quick tunnel)
```

ตรวจสอบ:
```bash
wrangler secret list
```

ควรเห็น 3 ตัวที่ตั้งไว้

---

## ขั้นตอนที่ 4: Test รันใน local ก่อน

```bash
npm run dev
```

จะได้ URL เช่น `http://localhost:8787`

ทดสอบ health check:
```bash
curl http://localhost:8787/health
# → OK
```

ทดสอบ webhook (จำลองข้อความ):
```bash
curl -X POST http://localhost:8787/webhook \
  -H "Content-Type: application/json" \
  -H "x-line-signature: test" \
  -d '{"events":[{"type":"message","replyToken":"test","message":{"type":"text","text":"ช่วย"}}]}'
```

ควรได้ 401 (signature ไม่ถูก) — ถูกต้อง = signature verification ทำงาน

กด `Ctrl+C` ออก

---

## ขั้นตอนที่ 5: Deploy จริง

```bash
npm run deploy
```

จะได้ URL เช่น `https://durionbot.YOUR-NAME.workers.dev`

> ถ้าเป็นครั้งแรก: wrangler ถามให้ subdomain — ใส่ชื่อที่จำง่าย เช่น `farmer123`

---

## ขั้นตอนที่ 6: ใส่ Webhook URL ใน LINE Console

กลับไปที่ https://developers.line.biz/console/

1. เลือก channel
2. แท็บ **Messaging API** → **Webhook URL**
3. ใส่: `https://durionbot.YOUR-NAME.workers.dev/webhook`
4. กด **Verify** → ควรได้ ✅ Success
5. **Use webhook**: ✅ Enabled

---

## ขั้นตอนที่ 7: ทดสอบจริง

เปิด LINE บนมือถือ → เปิดแชท Bot → พิมพ์ `ช่วย`

ควรได้ Flex Message แสดงเมนู

ดู log แบบ real-time:
```bash
wrangler tail
```

แล้วลองพิมพ์ใน LINE จะเห็น log ทันที

---

## 🐛 Troubleshooting

### ❌ "Invalid signature"
- LINE_CHANNEL_SECRET ผิด → ตรวจสอบใน LINE Developers Console → Basic settings

### ❌ Bot ไม่ตอบเลย
1. เช็ค `wrangler tail` มี log เข้าไหม
2. ถ้าไม่มี → Webhook URL ใน LINE ผิด หรือยังไม่ Enable
3. ถ้ามี log แต่ error → ดู error message

### ❌ "ข้อมูลยังไม่พร้อม"
- KV ยังว่าง → ต้องไป setup GitHub Actions (doc 06) ให้ดึงข้อมูลมาก่อน
- หรือใส่ข้อมูลเทียบเอง: 
  ```bash
  wrangler kv:key put --binding DURIONBOT_KV "weather:khuanklang" '{"forecast":[],"updated_at":"2026-04-25T00:00:00Z"}'
  ```

---

## ✅ Checklist

- [ ] Worker deploy สำเร็จ ได้ URL
- [ ] ตั้ง 3 secrets เรียบร้อย
- [ ] Webhook URL ผูกกับ LINE แล้ว verified
- [ ] Bot ตอบ "ช่วย" ได้

🎉 ไปต่อ → [05-tmd-api.md](05-tmd-api.md)

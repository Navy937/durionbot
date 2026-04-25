---
title: Setup Checklist
category: setup
date: 2026-04-25
---

# ✅ Master Checklist

ใช้เพื่อ track ว่าตั้งระบบไปถึงไหนแล้ว

---

## Phase 1: Local AI (วันที่ 1)

- [ ] ดาวน์โหลด Ollama
- [ ] `ollama pull llama3.2:3b`
- [ ] `ollama pull llava:7b`
- [ ] ตั้ง `OLLAMA_HOST=0.0.0.0:11434`
- [ ] ติดตั้ง Python + dependencies
- [ ] รัน `python disease-ai/ollama_server.py` ได้
- [ ] ทดสอบ `curl http://localhost:8000/health` → OK

## Phase 2: Cloud Setup (วันที่ 1)

- [ ] สมัคร Cloudflare account
- [ ] `wrangler login`
- [ ] สร้าง KV namespace → จด ID
- [ ] ติดตั้ง cloudflared
- [ ] สร้าง tunnel → ผูก hostname (หรือใช้ trycloudflare)
- [ ] รัน tunnel → ทดสอบเข้า ollama_server ผ่าน tunnel URL ได้

## Phase 3: LINE Bot (วันที่ 1)

- [ ] สมัคร LINE Business ID
- [ ] สร้าง LINE OA
- [ ] เปิด Messaging API
- [ ] ได้ Channel Secret + Access Token
- [ ] ตั้ง greeting message
- [ ] เพิ่ม Bot เป็นเพื่อนใน LINE ของตัวเอง

## Phase 4: Deploy Worker (วันที่ 1)

- [ ] ใส่ KV ID ใน `wrangler.toml`
- [ ] `wrangler secret put LINE_CHANNEL_SECRET`
- [ ] `wrangler secret put LINE_CHANNEL_ACCESS_TOKEN`
- [ ] `wrangler secret put OLLAMA_TUNNEL_URL`
- [ ] `npm run deploy` สำเร็จ
- [ ] ใส่ Webhook URL ใน LINE Console + Verify ✅

## Phase 5: Data Pipeline (วันที่ 2)

- [ ] สมัคร TMD API → รอ key
- [ ] (option) สมัคร YouTube Data API
- [ ] Push code ขึ้น GitHub
- [ ] ตั้ง GitHub secrets ครบ 4 ตัว
- [ ] รัน workflow manually → สำเร็จ
- [ ] เปิด LINE → พิมพ์ "ฝน" → ได้ข้อมูลจริง

## Phase 6: Polish (วันที่ 2-3)

- [ ] ทำ Rich Menu ใน LINE OA
- [ ] ติดตั้ง Obsidian + Dataview plugin
- [ ] เปิด vault → เห็น DASHBOARD.md ทำงาน
- [ ] ตั้ง Obsidian Git plugin auto-pull
- [ ] ทดสอบ end-to-end ทั้ง 10 test cases

## Phase 7: Production (วันที่ 4+)

- [ ] PC ที่บ้านตั้ง auto-start Ollama + cloudflared + ollama_server
- [ ] เพิ่มเพื่อนเกษตรกรในชุมชนใช้ LINE Bot
- [ ] เก็บ feedback → iterate prompt + scraper

---

## 📊 Progress

```dataviewjs
const phases = [
  { name: "Phase 1: Local AI", total: 7 },
  { name: "Phase 2: Cloud", total: 6 },
  { name: "Phase 3: LINE Bot", total: 6 },
  { name: "Phase 4: Worker", total: 6 },
  { name: "Phase 5: Data Pipeline", total: 6 },
  { name: "Phase 6: Polish", total: 5 },
  { name: "Phase 7: Production", total: 3 },
];
const total = phases.reduce((s, p) => s + p.total, 0);
dv.paragraph(`Total tasks: **${total}**`);
```

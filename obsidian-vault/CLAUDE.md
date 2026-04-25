# CLAUDE.md — Durian Wiki Schema

> ไฟล์นี้เป็น "ข้อตกลง" สำหรับ Claude/AI ใดๆ ที่มาช่วยจัดการ Wiki

---

## 📋 รูปแบบหัวไฟล์ (Front Matter)

ทุกไฟล์ใน Wiki ควรเริ่มด้วย:

```yaml
---
title: ชื่อไฟล์
category: 01-diseases | 02-cultivation | 03-phenology | 04-quality | 05-market | 06-weather | 07-risk-factors | 08-sources | 09-daily-data | 10-ai-prompts
tags: [โรค, การให้น้ำ, ราคา, ฯลฯ]
source: URL หรือชื่อแหล่งที่มา
date-created: YYYY-MM-DD
date-updated: YYYY-MM-DD
confidence: high | medium | low
---
```

---

## 🏷️ ระบบแท็ก

### โรคและปัญหา
`#โรค-ใบไหม้` `#โรค-ราน้ำมัน` `#โรค-ไฟทอป` `#ปัญหา-แมลง` `#หนอน`

### การเพาะปลูก
`#ปุ๋ย-N` `#ปุ๋ย-P` `#ปุ๋ย-K` `#น้ำ` `#ดิน`

### ช่วงเวลา
`#ช่วง-เตรียมพื้นที่` `#ช่วง-ออกดอก` `#ช่วง-ออกผล` `#ช่วง-เก็บเกี่ยว`

### ราคา/ตลาด
`#ราคา-สูง` `#ราคา-ต่ำ` `#แนวโน้ม` `#ตลาด`

### สภาพอากาศ
`#ฝน` `#อุณหภูมิ` `#ความชื้น` `#พิปูน`

### Auto-generated
`#auto` `#scraped` `#daily`

---

## 📂 หมวดหมู่และโฟลเดอร์

| โฟลเดอร์ | สำหรับ | สร้างด้วย |
|----------|--------|----------|
| `01-diseases/` | ฐานความรู้โรค | manual |
| `02-cultivation/` | ปุ๋ย น้ำ | manual |
| `03-phenology/` | ฤดูกาล | manual |
| `04-quality/` | คุณภาพผล | manual |
| `05-market/` | trends, analysis | manual + scrape สรุป |
| `06-weather/` | ฝน รายเดือน | manual + scrape สรุป |
| `07-risk-factors/` | ความเสี่ยง | manual |
| `08-sources/` | links | manual + youtube auto-add |
| **`09-daily-data/`** | **auto** ทุก 6 ชม. | **scraper เท่านั้น** |
| `10-ai-prompts/` | prompts สำหรับ Ollama | manual |

⚠️ **ห้ามแก้ไฟล์ใน `09-daily-data/` ด้วยมือ** — จะถูก overwrite

---

## 🔗 Wiki Linking

ใช้ `[[ ]]` เพื่อเชื่อมไฟล์:

```markdown
[[01-diseases/diseases-master]] — ดูฐานข้อมูลโรค
[[06-weather/]] — ดูข้อมูลสภาพอากาศ
```

---

## 📊 กฎ Citation

ทุก factual claim ต้องมีแหล่ง:

```markdown
### แหล่งที่มา
- [กรมส่งเสริมการเกษตร — เทคนิคปลูกทุเรียน](https://...)
- YouTube: ช่อง XYZ — "ทุเรียน 101" (วันที่)
- บันทึกส่วนตัว: 2026-04-25
```

---

## 🤖 ข้อตกลงกับ AI

ถ้าใช้ Ollama / Claude / ChatGPT มาช่วยจัด Wiki:

1. ✅ AI สามารถ **เพิ่ม** ไฟล์ใหม่ ใน folders 01-08, 10
2. ✅ AI สามารถ **เชื่อมลิงก์** [[..]] ระหว่างไฟล์
3. ❌ AI **ห้ามแก้** ไฟล์ใน `09-daily-data/`
4. ❌ AI **ห้ามลบ** ไฟล์ใดๆ — ขออนุญาตเจ้าของก่อน
5. ✅ AI ควร **อ้างอิง confidence** ในเรื่องที่ไม่แน่ใจ

---

## 💡 เคล็ดลับ

- ✅ 1 ไฟล์ = 1 แนวคิด (ไฟล์เล็กดีกว่าใหญ่)
- ✅ ใช้รูปประกอบโรค (ใส่ใน `attachments/`)
- ✅ commit Git บ่อยๆ → recover ได้
- ❌ อย่าลังเลถามให้ AI ช่วย refactor ไฟล์

---
title: Dashboard
category: dashboard
date-created: 2026-04-25
---

# 📊 DurionBot Dashboard

> หน้านี้ใช้ Dataview plugin — ติดตั้งใน Obsidian: Settings → Community plugins → Dataview

---

## 🌧️ ฝนสัปดาห์นี้

```dataview
TABLE WITHOUT ID
  date as "วันที่",
  source as "ที่มา"
FROM "09-daily-data"
WHERE category = "weather"
SORT date DESC
LIMIT 7
```

ดูข้อมูล detail ที่ `09-daily-data/weather.json` หรือเปิด LINE Bot พิมพ์ "ฝน 7 วัน"

---

## 🍈 ราคาทุเรียน 7 วันล่าสุด

```dataview
TABLE WITHOUT ID
  file.name as "ไฟล์",
  date as "วันที่",
  source as "ที่มา"
FROM "09-daily-data"
WHERE category = "durian-price"
SORT date DESC
LIMIT 7
```

---

## 🌳 ราคายางพารา

```dataview
TABLE WITHOUT ID
  file.name as "ไฟล์",
  date as "วันที่",
  source as "ที่มา"
FROM "09-daily-data"
WHERE category = "rubber-price"
SORT date DESC
LIMIT 7
```

---

## 🌱 ราคาปุ๋ย

```dataview
LIST
FROM "09-daily-data"
WHERE category = "fertilizer-price"
SORT date DESC
LIMIT 5
```

---

## 🦠 โรคที่ระวังเดือนนี้

ตามตารางใน [[01-diseases/diseases-master#📅 ตารางความเสี่ยงตามเดือน]]:

```dataviewjs
const month = new Date().getMonth() + 1;
const risks = {
  1: ["เพลี้ยไก่แจ้ (แตกใบอ่อน)"],
  2: ["เพลี้ยไก่แจ้ (แตกใบอ่อน)"],
  3: ["แอนแทรคโนส (ดอก)"],
  4: ["แอนแทรคโนส (ดอก)", "หนอนเจาะผล"],
  5: ["หนอนเจาะผล", "แอนแทรคโนส (ผลอ่อน)"],
  6: ["หนอนเจาะผล"],
  7: ["ไฟทอปเทอรา", "ผลเน่า", "ราน้ำมัน"],
  8: ["ไฟทอปเทอรา", "ผลเน่า", "ราน้ำมัน"],
  9: ["ใบจุดสาหร่าย", "ราน้ำมัน"],
  10: ["ใบจุดสาหร่าย"],
  11: ["ตรวจรากหลังฝน"],
  12: ["ตรวจรากหลังฝน"]
};
const monthRisks = risks[month] || [];
dv.list(monthRisks);
```

---

## 📺 วิดีโอใหม่จาก YouTube

ดู [[08-sources/youtube-collected]]

---

## 🔗 Quick Links

- [[01-diseases/diseases-master]] — ฐานความรู้โรค
- [[10-ai-prompts/prompts]] — prompt templates
- [[setup/checklist]] — checklist setup ระบบ
- [README หลัก](../README.md)

---

## 📝 Recent Updates (Auto)

```dataview
TABLE WITHOUT ID
  file.link as "ไฟล์",
  date as "วันที่",
  category as "หมวด"
FROM "09-daily-data"
SORT file.mtime DESC
LIMIT 10
```

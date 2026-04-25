---
title: Durian Knowledge Wiki + LINE Bot
category: root
tags: [ทุเรียน, การเพาะปลูก, การจัดการ, LINE-Bot]
date-created: 2026-04-25
---

# 🥭 Durian Knowledge Wiki + DurionBot

ศูนย์รวมความรู้ + ผู้ช่วย AI เกษตรกรทุเรียน  
อ.พิปูน จ.นครศรีธรรมราช (ต.ควนกลาง)

> **ระบบ DurionBot บน LINE** ติดต่อได้ตลอด 24 ชม. — ดู QR code ใน [[setup/line-qr]]

---

## 📂 หมวดหมู่หลัก

### 🦠 [01 - โรคและปัญหา](01-diseases/)
ดูไฟล์รวม [[01-diseases/diseases-master|diseases-master.md]] (7 โรคหลัก)

### 🌾 [02 - การเพาะปลูก](02-cultivation/)
ปุ๋ย น้ำ ดิน กำจัดศัตรู

### 🌸 [03 - ช่วงเวลาและเฟส](03-phenology/)
การออกดอก การออกผล เก็บเกี่ยว

### 🏆 [04 - คุณภาพผล](04-quality/)
การจัดเกรด คุณภาพ

### 💰 [05 - ราคาและตลาด](05-market/)
ราคาทุเรียน, ยาง, ปุ๋ย — auto update ทุก 6 ชม.

### 🌧️ [06 - สภาพอากาศ](06-weather/)
ฝน อุณหภูมิ ความชื้น

### ⚠️ [07 - ปัจจัยเสี่ยง](07-risk-factors/)
การพยากรณ์ความเสี่ยง

### 📚 [08 - แหล่งข้อมูล](08-sources/)
DOAE links, YouTube channels, บันทึกส่วนตัว

### 📊 [09 - ข้อมูลรายวัน](09-daily-data/)
auto-generated โดย scraper ทุก 6 ชม.

### 🤖 [10 - AI Prompts](10-ai-prompts/)
prompt templates สำหรับ Ollama

---

## 🚀 Dashboard

ดู [[DASHBOARD]] เพื่อเห็นภาพรวมราคา ฝน แนวโน้ม

---

## 💬 ใช้งาน LINE Bot

พิมพ์ใน LINE ของ DurionBot:

| คำสั่ง | ผลลัพธ์ |
|--------|---------|
| `ฝน` หรือ `ฝน 7 วัน` | พยากรณ์ฝน |
| `ราคาทุเรียน` | ราคา 4 พันธุ์ + แนวโน้ม |
| `ราคายาง` | 5 ตลาด |
| `ปุ๋ย 15-15-15` | เปรียบเทียบยี่ห้อ |
| ส่งรูปใบ/ผล | วินิจฉัยโรค |
| `ช่วย` | เมนูทั้งหมด |

---

## 🔧 การตั้งค่าระบบ

ดูเอกสารใน `../docs/`:
- [01-setup-ollama.md](../docs/01-setup-ollama.md) — AI ที่บ้าน
- [02-setup-cloudflare.md](../docs/02-setup-cloudflare.md) — Cloud
- [03-setup-line-bot.md](../docs/03-setup-line-bot.md) — LINE
- ครบทุกขั้นตอนใน [README หลัก](../README.md)

---

## 📊 Quick Stats (Dataview)

```dataview
TABLE WITHOUT ID
  category as "หมวด",
  length(rows) as "ไฟล์"
FROM ""
WHERE category != null AND category != "root"
GROUP BY category
SORT length(rows) DESC
```

---

**Happy farming! 🌾🥭**

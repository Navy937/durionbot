# 📘 07 — เปิด Obsidian Vault บน PC

> **เวลาที่ใช้**: 10 นาที  
> **ค่าใช้จ่าย**: ฟรี

---

## 🎯 Obsidian คืออะไร และทำไมใช้

Obsidian = โปรแกรมจัดการ markdown notes ที่:
- ทำ wiki link [[..]] ได้
- มี Graph View แสดงความเชื่อมโยง
- ฟรี ใช้กับไฟล์ markdown ปกติ
- ทำงาน offline 100%

ในระบบเรา:
- ข้อมูลจาก scraper จะถูก commit เป็น .md ใน `obsidian-vault/09-daily-data/`
- คุณเปิด Obsidian บน PC ดู graph view เห็นความเชื่อมระหว่างโรค-สภาพอากาศ-ราคา
- เพิ่มความรู้/บันทึกส่วนตัวได้ที่ตัว vault → ใส่ git push → backup ใน GitHub

---

## ขั้นตอนที่ 1: ติดตั้ง Obsidian

ดาวน์โหลดจาก https://obsidian.md/download

- Windows: `.exe`
- Mac: `.dmg`
- Linux: `.AppImage` หรือ `flatpak`

ติดตั้งปกติ → เปิด

---

## ขั้นตอนที่ 2: เปิด Vault

1. ที่หน้าแรก กด **Open folder as vault**
2. เลือก `durionbot/obsidian-vault/`
3. รอโหลด

จะเห็นไฟล์ทั้งหมดในโฟลเดอร์ — เปิด `index.md` เริ่มต้น

---

## ขั้นตอนที่ 3: ตั้งค่าเบื้องต้น

### Settings (ปุ่มเฟืองล่างซ้าย)

**Files & Links:**
- Default location for new attachments: `In subfolder under current folder`
- Subfolder name: `attachments`

**Editor:**
- Default editing mode: `Live preview`
- Use tabs: ✅ (เพื่อเปิดหลายไฟล์)

**Appearance:**
- Theme: ลองหา **Minimal** หรือ **Things** (ให้ดูง่ายขึ้น)

---

## ขั้นตอนที่ 4: เปิด Plugins ที่มีประโยชน์

### Core Plugins (มากับ Obsidian)
ไป Settings → Core plugins เปิด:

- **Graph view** ✅ (เห็นความเชื่อมโยง)
- **Templates** ✅
- **Daily notes** ✅
- **Tag pane** ✅
- **Search** ✅

### Community Plugins (ติดตั้งเพิ่ม)
1. Settings → Community plugins → **Turn on community plugins**
2. กด **Browse** → ค้นหาและติดตั้ง:

   - **Dataview** — query ไฟล์เป็น table (สำคัญมาก สำหรับเรา)
   - **Templater** — template แบบขั้นสูง
   - **Calendar** — ปฏิทินดู daily notes
   - **Charts** — ทำกราฟใน markdown
   - **Image Toolkit** — ดูรูปแบบ zoom (ใช้กับรูปโรคทุเรียน)

---

## ขั้นตอนที่ 5: ดู Graph View

กดไอคอน **Graph view** ที่แถบซ้าย (สาม dot เชื่อมกัน)

ปรับ filter:
- **Search**: `tag:#โรค` หรือ `path:09-daily-data`
- **Color groups**:
  - `tag:#โรค` → สีแดง
  - `tag:#ราคา` → สีเขียว
  - `tag:#ฝน` → สีฟ้า

ลาก node ดูได้

---

## ขั้นตอนที่ 6: ใช้ Dataview ทำ dashboard

ดูที่ `obsidian-vault/DASHBOARD.md` เพื่อดูตัวอย่าง query

ตัวอย่างที่ใช้บ่อย:

````markdown
## ราคาทุเรียน 7 วันล่าสุด

```dataview
TABLE date as "วันที่", price_big as "เบอร์ใหญ่", price_small as "เบอร์เล็ก"
FROM "09-daily-data"
WHERE category = "durian-price"
SORT date DESC
LIMIT 7
```

## ฝนสัปดาห์นี้

```dataview
TABLE rain_chance as "โอกาสฝน %", rain_mm as "ปริมาณ (มม.)"
FROM "09-daily-data"
WHERE category = "weather"
SORT date DESC
LIMIT 7
```
````

---

## ขั้นตอนที่ 7: Sync กับ GitHub (อัตโนมัติ)

วิธีที่ 1: **ใช้ Git plugin (แนะนำ)**

1. Community plugins → ค้น **Obsidian Git** → install + enable
2. Settings → Obsidian Git:
   - **Vault backup interval (minutes)**: 30
   - **Auto pull interval (minutes)**: 15
   - **Commit message**: `vault: {{date}} {{hostname}}`

ตอนนี้ทุก 30 นาที vault จะ commit + push อัตโนมัติ

วิธีที่ 2: **ใช้ git command ปกติ**

```bash
cd durionbot/obsidian-vault
git pull   # ดึงข้อมูลใหม่จาก scraper
# แก้ไข ...
git add .
git commit -m "update notes"
git push
```

---

## 💡 Workflow แนะนำสำหรับเกษตรกร

**เช้าวันจันทร์**:
1. เปิด Obsidian PC → กด pull (Ctrl+P → "Git: pull")
2. เปิด `DASHBOARD.md` → ดูราคาทุเรียน + ฝนสัปดาห์นี้ + แนวโน้มปุ๋ย
3. ถ้าเห็นสัญญาณ (เช่น ฝนหนัก 3 วัน + ราคาขึ้น) → วางแผน

**ระหว่างวัน**:
- ใช้ LINE Bot บนมือถือ ถามแบบเร็วๆ

**ปลายสัปดาห์**:
- บันทึกการตัดสินใจ/ผลลัพธ์ใน vault → commit
- รูปสวน รูปต้นไม้ ใส่ใน `obsidian-vault/attachments/`

---

## ✅ Checklist

- [ ] Obsidian เปิด vault สำเร็จ
- [ ] ติดตั้ง Dataview plugin
- [ ] เห็น Graph view
- [ ] ลอง sync กับ GitHub ได้

🎉 ไปต่อ → [08-testing.md](08-testing.md)

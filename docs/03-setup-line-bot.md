# 📘 03 — สร้าง LINE Official Account + Bot

> **เวลาที่ใช้**: 30 นาที  
> **ค่าใช้จ่าย**: 0 บาท (ใช้ Free plan)

---

## 🎯 ภาพรวม

เราจะใช้ **LINE Messaging API** ผ่าน **LINE Official Account (LINE OA)**:

- **Reply messages** (ตอบเมื่อมีคนทัก) = **ฟรีไม่จำกัด** ✅
- Push messages (ส่งโดยไม่มีคนทัก) = ฟรี 200 ข้อความ/เดือน
- เราใช้แค่ reply เป็นหลัก → **ฟรีตลอด**

---

## ขั้นตอนที่ 1: สมัคร LINE Business ID

1. ไปที่ https://account.line.biz/login
2. เลือก **Log in with LINE** (ใช้ LINE account ปกติ login)
3. กรอกข้อมูล: ชื่อ, เบอร์ติดต่อ, ประเทศ Thailand
4. ยืนยัน OTP

---

## ขั้นตอนที่ 2: สร้าง LINE Official Account

1. เข้า https://manager.line.biz/
2. กด **Create a new account**
3. กรอก:
   - **Account name**: `DurionBot สวนทุเรียน` (หรืออะไรก็ได้)
   - **Business category**: เกษตรกรรม
   - **Subcategory**: เกษตรกร
4. กด Create

หลังสร้างเสร็จ → เลือก **Free Plan** (ตลอด)

---

## ขั้นตอนที่ 3: ตั้งค่า OA ให้ตอบเป็น Bot

ใน LINE OA Manager:

1. แท็บ **Settings** (มุมขวาบน)
2. เมนูซ้าย → **Response settings**
3. ตั้งค่าตามนี้:
   - **Chat**: ✅ ON (เผื่อกรณีต้องคุยกับคนจริง)
   - **Webhook**: ✅ ON ⭐ **สำคัญ** — ต้องเปิด
   - **Auto-response**: ❌ OFF
   - **Greeting message**: ✅ ON (ตั้งข้อความต้อนรับ)
4. กด Save

ตั้ง greeting message:
```
🥭 สวัสดีครับ ผมคือ DurionBot ผู้ช่วยเกษตรกรทุเรียน

ลองพิมพ์:
🌧️ "ฝน" → เช็คพยากรณ์ฝน ต.ควนกลาง
🍈 "ราคาทุเรียน" → ราคาวันนี้ + แนวโน้ม
🌳 "ราคายาง" → ราคายางพารา
🌱 "ปุ๋ย 15-15-15" → เปรียบเทียบราคาปุ๋ย
🦠 ส่งรูปใบ/ผล → วินิจฉัยโรค
❓ "ช่วย" → ดูคำสั่งทั้งหมด
```

---

## ขั้นตอนที่ 4: เปิด Messaging API

1. ใน LINE OA Manager → **Settings** → เมนูซ้าย → **Messaging API**
2. กด **Enable Messaging API**
3. เลือก provider (ถ้าไม่มี → กด **Create a new provider** → ใส่ชื่อ เช่น "DurionBot")
4. ปุ่ม **Agree** → confirm

จะได้ **LINE Developers Console URL** → เปิดดู

---

## ขั้นตอนที่ 5: ตั้งค่าใน LINE Developers Console

ไปที่ https://developers.line.biz/console/

1. เลือก provider ที่สร้างไว้
2. คลิก channel ของคุณ (Messaging API)
3. แท็บ **Basic settings**:
   - คัดลอก **Channel secret** เก็บไว้ (จะใช้ใน Worker)
4. แท็บ **Messaging API**:
   - เลื่อนลงไปที่ **Channel access token**
   - กด **Issue** → คัดลอก token ยาวๆ เก็บไว้

⚠️ **เก็บ 2 ค่านี้ปลอดภัย — ห้ามแชร์**:
- `LINE_CHANNEL_SECRET`
- `LINE_CHANNEL_ACCESS_TOKEN`

---

## ขั้นตอนที่ 6: ตั้งค่า Webhook URL

(ทำหลัง deploy Worker เสร็จ — ดู [04-deploy-worker.md](04-deploy-worker.md))

ใน Channel → **Messaging API** tab:
1. **Webhook URL**: `https://durionbot.YOUR-NAME.workers.dev/webhook`
2. กด **Verify** — ควรได้ ✅ Success
3. **Use webhook**: ✅ Enabled
4. **Auto-reply messages**: ❌ Disabled (ปิด default ของ LINE)
5. **Greeting messages**: ✅ Enabled (ใช้ที่ตั้งไว้)

---

## ขั้นตอนที่ 7: เพิ่มเพื่อน + ทดสอบ

1. ใน Console → แท็บ **Messaging API**
2. หา **QR code** ใต้ **Bot basic ID**
3. เปิด LINE บนมือถือ → สแกน QR
4. กด Add Friend

ทดสอบ: พิมพ์ `สวัสดี` ส่งให้ Bot
- ก่อน deploy worker: ไม่มีอะไรเกิด (ถูกต้อง)
- หลัง deploy: ควรได้คำตอบ

---

## ขั้นตอนที่ 8: สร้าง Rich Menu (เมนูถาวรด้านล่าง)

Rich Menu = ปุ่มลัดที่เกษตรกรกดได้เลย ไม่ต้องพิมพ์

### 8.1 ดาวน์โหลด LINE Rich Menu Maker

ใช้เว็บออนไลน์ฟรี: https://anbon.app.officialaccount.line.me/

หรือทำเองด้วย Photoshop/Canva:
- ขนาด: **2500 x 1686 px** (ใหญ่) หรือ **2500 x 843 px** (เตี้ย)
- format: PNG หรือ JPEG
- ขนาดไฟล์ไม่เกิน 1 MB

### 8.2 ตัวอย่าง layout 6 ปุ่ม (2 แถว)

```
┌──────────────┬──────────────┬──────────────┐
│  🌧️ ฝน       │  🍈 ทุเรียน   │  🌳 ยาง       │
├──────────────┼──────────────┼──────────────┤
│  🌱 ปุ๋ย      │  🦠 โรค       │  ❓ ช่วย      │
└──────────────┴──────────────┴──────────────┘
```

### 8.3 อัปโหลด Rich Menu

ผ่าน LINE OA Manager:
1. **Home** → **Rich menu**
2. กด Create
3. อัปโหลดรูป → ตั้ง action ของแต่ละปุ่ม:
   - **Type**: Text
   - **Text**: เช่น `ฝน`, `ราคาทุเรียน`, `ราคายาง`, `ปุ๋ย`, `วินิจฉัยโรค`, `ช่วย`
4. **Display period**: All time
5. **Default**: ✅ ตั้งเป็นค่าเริ่มต้น
6. Save

> เกษตรกรกดปุ่มเดียว = ส่งคำว่า "ฝน" ให้ Bot ทันที — ไม่ต้องพิมพ์เอง

---

## ✅ Checklist ก่อนไปต่อ

- [ ] สร้าง LINE OA เรียบร้อย
- [ ] เปิด Messaging API + ได้ Channel Secret + Access Token
- [ ] บันทึก credentials ปลอดภัย
- [ ] สร้าง Greeting Message
- [ ] ทำ Rich Menu (option ภายหลังก็ได้)
- [ ] เพิ่ม Bot เป็นเพื่อนใน LINE ของตัวเอง

🎉 ไปต่อ → [04-deploy-worker.md](04-deploy-worker.md)

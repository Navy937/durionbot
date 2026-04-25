# 📘 05 — ขอ TMD API Key (ฟรี)

> **เวลาที่ใช้**: 10 นาที + รอ 1-2 วันทำการ  
> **ค่าใช้จ่าย**: ฟรี (เพื่อการศึกษา/ใช้ส่วนตัว/ไม่หาผลประโยชน์)

---

## 🎯 TMD API คืออะไร

TMD = Thai Meteorological Department (กรมอุตุนิยมวิทยา)

มี 2 endpoint หลักที่เราจะใช้:
- **WeatherForecast** — พยากรณ์ราย 3 ชม. ล่วงหน้า 7 วัน เลือกพิกัดได้
- **WeatherToday** — พยากรณ์รายวันแยกตำบล/อำเภอ

ความถี่อัปเดต: ทุก 6 ชม. (พอเหมาะกับ scraper ของเรา)

---

## ขั้นตอนที่ 1: ลงทะเบียน

ไปที่ https://data.tmd.go.th/nwpapi/

> ⚠️ ถ้าเว็บล่ม ลองเข้า https://data.tmd.go.th/ แล้วหาเมนู API/บริการข้อมูล

1. กด **สมัครสมาชิก** หรือ **Register**
2. กรอก:
   - ชื่อ-นามสกุล
   - Email (ใช้ที่เข้าได้จริง)
   - หน่วยงาน: ใส่ "เกษตรกรอิสระ" หรือ "บุคคลทั่วไป"
   - **วัตถุประสงค์การใช้งาน**: 

   ใส่ข้อความประมาณนี้ (สำคัญ — ต้องชัดเจน):
   ```
   ใช้สำหรับสวนทุเรียนส่วนตัวที่ ต.ควนกลาง อ.พิปูน จ.นครศรีธรรมราช
   ดึงพยากรณ์ฝนเพื่อวางแผนการพ่นยา ใส่ปุ๋ย เก็บผล
   ไม่ใช้เพื่อการพาณิชย์ ไม่เผยแพร่สู่สาธารณะ
   ```

3. submit → รอ email confirm (ปกติ 1-2 วันทำการ)

---

## ขั้นตอนที่ 2: รับ API Key

ปกติจะได้ email ภายใน 24-48 ชม. มีลิงก์ไป login → คัดลอก **uid** หรือ **token** เก็บไว้

API key มีรูปแบบ JWT ยาวๆ เช่น:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxxxxxxx...
```

---

## ขั้นตอนที่ 3: ทดสอบ API

```bash
# พยากรณ์ตำบลควนกลาง อำเภอพิปูน
curl "https://data.tmd.go.th/nwpapi/v1/forecast/location/hourly/place?province=นครศรีธรรมราช&amphoe=พิปูน&tambon=ควนกลาง&fields=tc,rh,rr,wd&duration=72" \
  -H "accept: application/json" \
  -H "authorization: Bearer YOUR_API_KEY"
```

ผลลัพธ์ควรได้ JSON พยากรณ์รายชั่วโมง 72 ชม.

---

## ขั้นตอนที่ 4: เก็บ API key ใน GitHub Secrets

(ทำหลัง setup GitHub Actions — doc 06)

```
TMD_API_KEY = eyJhbGciOiJIUzI1NiI...
```

---

## 🐛 ถ้าไม่ได้ API Key ใน 3 วัน

- ลอง email ติดต่อ: `info_service@tmd.go.th`
- โทร: 02-399-3031, 02-399-1422

---

## 🆘 ทางเลือกถ้า TMD API ใช้ไม่ได้

ใช้ **OpenWeatherMap** แทน (ฟรี 1,000 calls/วัน) — แม่นน้อยกว่า TMD แต่ทันใจ

```bash
# พิกัด ต.ควนกลาง อ.พิปูน
LAT=8.50
LON=99.65

curl "https://api.openweathermap.org/data/2.5/forecast?lat=${LAT}&lon=${LON}&appid=YOUR_OWM_KEY&units=metric&lang=th"
```

สมัคร OWM ฟรี: https://openweathermap.org/api

หรือใช้ **Open-Meteo** (ฟรี ไม่ต้องสมัคร — แม่นน้อยที่สุด แต่ใช้ทันที):

```bash
curl "https://api.open-meteo.com/v1/forecast?latitude=8.50&longitude=99.65&hourly=temperature_2m,relativehumidity_2m,precipitation,windspeed_10m&timezone=Asia/Bangkok&forecast_days=7"
```

---

## ✅ Checklist

- [ ] ลงทะเบียน TMD API แล้ว
- [ ] ได้ API key (หรือใช้ Open-Meteo เป็น fallback)
- [ ] ทดสอบดึงข้อมูล ต.ควนกลาง สำเร็จ

🎉 ไปต่อ → [06-github-actions.md](06-github-actions.md)

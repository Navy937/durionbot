# 📘 06 — Setup GitHub Actions (cron job ดึงข้อมูลทุก 6 ชม.)

> **เวลาที่ใช้**: 15 นาที  
> **ค่าใช้จ่าย**: ฟรี (2,000 นาที/เดือน, เราใช้ ~120 นาที)

---

## 🎯 ทำไมใช้ GitHub Actions

- **ฟรี** สำหรับ public repo
- มี cron schedule ในตัว
- ไม่ต้อง host server เอง
- เก็บ history ของข้อมูล (commit ทุกครั้ง = snapshot)

ระบบของเรา:
- Action รันทุก 6 ชั่วโมง
- เรียก scrapers ทั้งหมด (TMD, ราคาทุเรียน, ยาง, ปุ๋ย, YouTube)
- บันทึกผลใน `obsidian-vault/09-daily-data/`
- **push ขึ้น Cloudflare KV** ผ่าน wrangler หรือ KV API
- commit ขึ้น GitHub repo

---

## ขั้นตอนที่ 1: สร้าง GitHub Repo

1. ไปที่ https://github.com/new
2. ชื่อ: `durionbot` (หรืออะไรก็ได้)
3. Public ✅ (เพื่อให้ Actions ฟรี)
4. กด Create

ใน terminal:
```bash
cd durionbot/
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/durionbot.git
git push -u origin main
```

---

## ขั้นตอนที่ 2: ตั้ง Secrets ใน GitHub

ไปที่: `Repo → Settings → Secrets and variables → Actions → New repository secret`

ใส่ทีละตัว:

| Secret Name | Value |
|---|---|
| `TMD_API_KEY` | JWT token จาก TMD (doc 05) |
| `CF_ACCOUNT_ID` | Cloudflare Account ID |
| `CF_API_TOKEN` | Cloudflare API Token (สร้างที่ขั้นต่อไป) |
| `CF_KV_NAMESPACE_ID` | KV ID ที่สร้างไว้ (doc 02) |
| `OPENWEATHER_API_KEY` | (option) ถ้าใช้ OWM แทน TMD |

### วิธีสร้าง Cloudflare API Token

1. https://dash.cloudflare.com/profile/api-tokens
2. **Create Token** → ใช้ template **Edit Cloudflare Workers**
3. หรือ **Custom token** ตั้ง permission:
   - Account → Workers KV Storage → Edit
   - Account → Account Settings → Read
4. กด Create → คัดลอก token (เก็บให้ดี — ดูแค่ครั้งเดียว!)

### หา Account ID

หน้า dashboard Cloudflare → ดูแถบขวา → **Account ID** = ตัวเลขยาวๆ

---

## ขั้นตอนที่ 3: ไฟล์ workflow

ไฟล์ `.github/workflows/scrape.yml` (ผมสร้างให้แล้วใน repo)

ดูเนื้อหาที่ `.github/workflows/scrape.yml`

---

## ขั้นตอนที่ 4: รัน workflow ครั้งแรก (manual)

1. ไปที่ tab **Actions** ใน repo
2. เลือก workflow **Scrape Daily Data**
3. กด **Run workflow** (ปุ่มขวา) → เลือก branch main → Run

ดู progress: คลิกที่ run แล้วดู log

ถ้าสำเร็จ:
- จะเห็น commit ใหม่ใน repo (เพิ่มไฟล์ใน `obsidian-vault/09-daily-data/`)
- เปิด LINE Bot ลองพิมพ์ "ฝน" → ตอนนี้ควรได้ข้อมูลจริงแล้ว

---

## ขั้นตอนที่ 5: ตั้ง schedule

Workflow ของเราตั้งให้รันทุก 6 ชม. โดย default:
```yaml
schedule:
  - cron: '0 */6 * * *'  # 00:00, 06:00, 12:00, 18:00 UTC
```

UTC + 7 = เวลาไทย → รันที่ 7:00, 13:00, 19:00, 1:00 ของไทย

**ปรับได้ที่บรรทัด `cron:`** เช่น:
- `0 */3 * * *` = ทุก 3 ชม.
- `0 0,12 * * *` = วันละ 2 ครั้ง (เที่ยงคืน เที่ยงวัน UTC)

---

## ✅ Checklist

- [ ] Push code ขึ้น GitHub สำเร็จ
- [ ] ตั้ง 4 secrets ครบ
- [ ] Workflow รัน manual ครั้งแรกสำเร็จ (เขียว ✅)
- [ ] เปิด LINE → พิมพ์ "ฝน" ได้ข้อมูลจริง

🎉 ไปต่อ → [07-obsidian.md](07-obsidian.md)

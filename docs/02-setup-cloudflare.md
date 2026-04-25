# 📘 02 — ตั้งค่า Cloudflare (ฟรี) + Tunnel เชื่อม Ollama ที่บ้าน

> **เวลาที่ใช้**: 20 นาที  
> **ค่าใช้จ่าย**: 0 บาท ตลอดไป

## 🎯 ทำไมต้องใช้ Cloudflare

3 บริการที่เราจะใช้:

1. **Cloudflare Workers** — host backend code (รับ webhook จาก LINE)
2. **Cloudflare KV** — เก็บข้อมูลราคา/ฝน cached
3. **Cloudflare Tunnel** — ทำให้ Ollama ที่บ้านเข้าถึงได้จาก internet โดยไม่ต้อง port forward

ทั้งหมด**ฟรี** สำหรับ traffic ระดับเรา (ไม่เกิน 100k req/วัน)

---

## ขั้นตอนที่ 1: สมัคร Cloudflare

1. ไปที่ https://dash.cloudflare.com/sign-up
2. ใส่ email + password → กด Create Account
3. ยืนยัน email
4. เลือก plan: **Free Plan** (ตลอด)

> ไม่ต้องโยง credit card ก็ใช้ได้ทุกอย่างที่เราจะใช้

---

## ขั้นตอนที่ 2: ติดตั้ง Wrangler (CLI ของ Cloudflare)

ต้องมี Node.js ก่อน — ถ้ายังไม่มี:
- Windows: ดาวน์โหลด LTS จาก https://nodejs.org/
- Mac: `brew install node`
- Linux: `sudo apt install nodejs npm`

ติดตั้ง wrangler:
```bash
npm install -g wrangler
```

ทดสอบ:
```bash
wrangler --version
# wrangler 3.x.x
```

ล็อกอิน:
```bash
wrangler login
```
จะเปิด browser ให้ authorize → กด Allow

---

## ขั้นตอนที่ 3: สร้าง KV Namespace

KV = key-value store ที่ใช้เก็บ cache

```bash
wrangler kv:namespace create DURIONBOT_KV
```

จะได้ output เช่น:
```
🌀 Creating namespace with title "durionbot-kv"
✨ Success!
Add the following to your configuration file:
{ binding = "DURIONBOT_KV", id = "abc123def456" }
```

**คัดลอก `id` เก็บไว้** — ต้องใช้ในขั้นต่อไป

สร้าง namespace สำหรับ preview ด้วย:
```bash
wrangler kv:namespace create DURIONBOT_KV --preview
```

---

## ขั้นตอนที่ 4: ติดตั้ง cloudflared (สำหรับ Tunnel)

### Windows
ดาวน์โหลด `cloudflared-windows-amd64.exe` จาก:
https://github.com/cloudflare/cloudflared/releases/latest

เปลี่ยนชื่อเป็น `cloudflared.exe` → ใส่ใน `C:\cloudflared\` → เพิ่มใน PATH

### Mac
```bash
brew install cloudflared
```

### Linux
```bash
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb
```

ตรวจสอบ:
```bash
cloudflared --version
```

---

## ขั้นตอนที่ 5: สร้าง Tunnel เชื่อม Ollama

### 5.1 Login
```bash
cloudflared tunnel login
```
เปิด browser → เลือก domain (ถ้าไม่มี → ใช้ trycloudflare.com ฟรี)

### 5.2 สร้าง tunnel
```bash
cloudflared tunnel create durionbot-ai
```

จะได้ output:
```
Tunnel credentials written to /home/user/.cloudflared/abc-123-def.json
Created tunnel durionbot-ai with id abc-123-def
```

**จด Tunnel ID เก็บไว้**

### 5.3 สร้าง config file

#### Windows: `C:\Users\YOUR_USER\.cloudflared\config.yml`
#### Mac/Linux: `~/.cloudflared/config.yml`

```yaml
tunnel: abc-123-def    # ใส่ Tunnel ID ของคุณ
credentials-file: /home/user/.cloudflared/abc-123-def.json   # path ไฟล์ credentials

ingress:
  # ส่ง traffic ไปที่ Ollama wrapper API
  - hostname: durionbot-ai.YOUR-DOMAIN.com
    service: http://localhost:8000
  # default rule (จำเป็น)
  - service: http_status:404
```

> **ถ้าคุณไม่มี domain ของตัวเอง**: ใช้ "Quick Tunnel" แทน:
> ```bash
> cloudflared tunnel --url http://localhost:8000
> ```
> จะได้ random URL เช่น `https://random-name.trycloudflare.com`  
> **ข้อเสีย**: URL เปลี่ยนทุกครั้งที่ restart → ต้อง update Worker config

### 5.4 ผูก hostname (ถ้ามี domain)

```bash
cloudflared tunnel route dns durionbot-ai durionbot-ai.YOUR-DOMAIN.com
```

### 5.5 รัน Tunnel
```bash
cloudflared tunnel run durionbot-ai
```

ควรเห็น log แบบ:
```
INF Connection registered  connIndex=0 location=BKK
```

ทดสอบ:
```bash
curl https://durionbot-ai.YOUR-DOMAIN.com/health
```

---

## ขั้นตอนที่ 6: ทำให้ Tunnel รันอัตโนมัติ

### Windows (ใช้เป็น service)
```powershell
# Run PowerShell as Administrator
cloudflared.exe service install
```

### Mac
```bash
sudo cloudflared service install
```

### Linux
```bash
sudo cloudflared service install
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
```

---

## ✅ Checklist ก่อนไปต่อ

- [ ] login Cloudflare ผ่าน wrangler ได้
- [ ] สร้าง KV namespace แล้ว — มี ID เก็บไว้
- [ ] cloudflared tunnel ทำงาน
- [ ] เข้า `https://YOUR-TUNNEL-URL/health` แล้วเจอ Ollama API ได้
- [ ] Tunnel auto-start ตอน boot

🎉 ไปต่อ → [03-setup-line-bot.md](03-setup-line-bot.md)

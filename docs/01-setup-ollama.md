# 📘 01 — ติดตั้ง Ollama (AI ฟรี รันบน PC ตัวเอง)

> **เวลาที่ใช้**: 30 นาที  
> **อุปกรณ์**: PC ที่บ้าน (Windows/Mac/Linux) RAM ≥ 8GB, SSD แนะนำ  
> **ค่าใช้จ่าย**: 0 บาท

---

## 🎯 Ollama คืออะไร และทำไมถึงใช้

**Ollama** = โปรแกรมรัน LLM (โมเดล AI) บนเครื่องตัวเอง ไม่ต้องส่งข้อมูลขึ้น cloud

| | Claude API | ChatGPT Free | Ollama (เลือกอันนี้) |
|---|---|---|---|
| ค่าใช้จ่าย | ~3 บาท/คำถาม | ฟรีแต่จำกัด | **ฟรีไม่จำกัด** |
| Privacy รูปสวน | ส่งขึ้น cloud | ส่งขึ้น cloud | **อยู่ที่บ้าน** |
| Rate limit | จ่ายเงินเพิ่มได้ | โดนเตะถ้าใช้เยอะ | **ไม่มี** |
| Internet | ต้องมี | ต้องมี | ใช้แค่ตอน setup |
| ความเก่ง | สูงสุด | สูง | **พอใช้สำหรับงานเรา** |

โมเดลที่จะใช้:
- **llava:7b** (~4.7 GB) — วินิจฉัยโรคจาก**รูปภาพ**
- **llama3.2:3b** (~2 GB) — ตอบคำถาม**ข้อความ** (เร็ว เบา)

รวม disk space ที่ต้องใช้: **~7 GB**

---

## 📥 ขั้นตอนที่ 1: ดาวน์โหลด Ollama

### Windows
1. ไปที่ https://ollama.com/download/windows
2. กด **Download for Windows** → ได้ไฟล์ `OllamaSetup.exe`
3. เปิดไฟล์ → กด Install (ใช้เวลา 1-2 นาที)
4. หลังติดตั้งเสร็จ Ollama จะรันใน background (เห็นไอคอนใน system tray)

### Mac
```bash
brew install ollama
brew services start ollama
```
หรือดาวน์โหลด `.dmg` จาก https://ollama.com/download/mac

### Linux (Ubuntu/Debian)
```bash
curl -fsSL https://ollama.com/install.sh | sh
sudo systemctl start ollama
sudo systemctl enable ollama  # auto start ตอน boot
```

---

## ✅ ขั้นตอนที่ 2: ตรวจสอบว่า Ollama รันอยู่

เปิด **Terminal** (Mac/Linux) หรือ **PowerShell** (Windows):

```bash
ollama --version
```

ควรได้ผลคล้าย:
```
ollama version is 0.5.x
```

ทดสอบเพิ่ม:
```bash
curl http://localhost:11434
```
ควรได้: `Ollama is running`

ถ้าไม่ได้ → ตรวจสอบ:
- Windows: เปิด Task Manager → ค้นหา process ชื่อ `ollama` ต้องมี
- Mac/Linux: รัน `ps aux | grep ollama`

---

## 📦 ขั้นตอนที่ 3: ดาวน์โหลดโมเดล AI

### โมเดลตอบข้อความ (llama3.2)

```bash
ollama pull llama3.2:3b
```

จะเห็นการดาวน์โหลด ~2 GB ใช้เวลา 5-15 นาที (ขึ้นกับเน็ต)

ทดสอบ:
```bash
ollama run llama3.2:3b "สวัสดี คุณเป็นใคร"
```

ควรได้คำตอบภาษาไทยเล็กน้อย (โมเดลเล็ก ไทยจะกระดูดบ้าง — ไม่เป็นไรเพราะเราจะใช้ prompt template ช่วย)

ออกจาก chat: พิมพ์ `/bye`

### โมเดลดูรูป (llava — วินิจฉัยโรคจากภาพ)

```bash
ollama pull llava:7b
```

ดาวน์โหลด ~4.7 GB ใช้เวลา 10-30 นาที

ทดสอบ:
```bash
# วางรูปทุเรียนไว้ที่ ~/Desktop/test.jpg ก่อน
ollama run llava:7b "บรรยายภาพนี้ภาษาไทย" /Desktop/test.jpg
```

---

## 🌐 ขั้นตอนที่ 4: เปิด API ให้เข้าถึงจากภายนอก

โดย default Ollama เปิด port `11434` แต่ฟังเฉพาะ `localhost`  
เราต้องให้รับจาก network อื่นได้ (เพื่อให้ Cloudflare Tunnel ต่อมาได้)

### Windows

1. กด `Win + R` → พิมพ์ `sysdm.cpl` → Enter
2. แท็บ **Advanced** → ปุ่ม **Environment Variables**
3. ในส่วน **System variables** กด **New**:
   - Variable name: `OLLAMA_HOST`
   - Variable value: `0.0.0.0:11434`
4. ปิด restart Ollama:
   - ไอคอน Ollama ใน system tray → คลิกขวา → Quit
   - เปิดโปรแกรม Ollama ใหม่

### Mac
```bash
launchctl setenv OLLAMA_HOST "0.0.0.0:11434"
brew services restart ollama
```

### Linux (systemd)
```bash
sudo mkdir -p /etc/systemd/system/ollama.service.d
sudo nano /etc/systemd/system/ollama.service.d/override.conf
```

ใส่เนื้อหา:
```ini
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
```

แล้วรัน:
```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

### ✅ ทดสอบว่าเปิด API ได้:
```bash
curl http://localhost:11434/api/tags
```
ควรเห็น list โมเดล:
```json
{
  "models": [
    { "name": "llama3.2:3b", ... },
    { "name": "llava:7b", ... }
  ]
}
```

---

## 🔌 ขั้นตอนที่ 5: ทดสอบ API จริง (ตอบข้อความ)

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2:3b",
  "prompt": "อธิบายโรคใบจุดสาหร่ายในทุเรียนเป็นภาษาไทยสั้นๆ",
  "stream": false
}'
```

จะได้ JSON response:
```json
{
  "response": "โรคใบจุดสาหร่าย เกิดจากเชื้อ Cephaleuros virescens...",
  ...
}
```

🎉 **ถ้าได้ผลแบบนี้ = Ollama พร้อมใช้งานแล้ว!**

---

## 🖼️ ขั้นตอนที่ 6: ทดสอบ API จริง (วินิจฉัยจากรูป)

```bash
# encode รูปเป็น base64
base64 -i test.jpg > image.b64

# ส่งไป llava
curl http://localhost:11434/api/generate -d '{
  "model": "llava:7b",
  "prompt": "นี่คือรูปใบทุเรียน บอกว่าน่าจะเป็นโรคอะไร และวิธีแก้",
  "images": ["'"$(cat image.b64)"'"],
  "stream": false
}'
```

---

## 🔧 ขั้นตอนที่ 7: สร้าง wrapper API (Python FastAPI)

เราจะสร้าง API ตัวกลาง ที่ทำหน้าที่:
- รับ webhook จาก Cloudflare Worker
- ใส่ prompt template ที่ tune มาแล้ว
- ส่งไป Ollama
- ตอบกลับเป็นรูปแบบที่เข้าใจง่าย

ดู code ที่ `disease-ai/ollama_server.py` (ในโปรเจคนี้)

ติดตั้ง dependencies:
```bash
pip install fastapi uvicorn requests pillow
```

รัน server:
```bash
cd disease-ai/
python ollama_server.py
```

จะรันที่ `http://localhost:8000`

ทดสอบ:
```bash
curl -X POST http://localhost:8000/diagnose \
  -F "description=ใบทุเรียนมีจุดสีน้ำตาล ขอบใบไหม้"
```

---

## ⚙️ ขั้นตอนที่ 8: ทำให้รันอัตโนมัติตอน boot

### Windows — ใส่ใน Task Scheduler
1. กด `Win + R` → `taskschd.msc` → Enter
2. **Create Basic Task**:
   - Name: `Ollama Wrapper API`
   - Trigger: **When the computer starts**
   - Action: **Start a program**
     - Program: `C:\Python310\python.exe` (path Python ของคุณ)
     - Arguments: `C:\path\to\durionbot\disease-ai\ollama_server.py`
     - Start in: `C:\path\to\durionbot\disease-ai\`
3. กด Finish

### Mac — สร้าง LaunchAgent
สร้างไฟล์ `~/Library/LaunchAgents/com.durionbot.ai.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.durionbot.ai</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/local/bin/python3</string>
    <string>/path/to/durionbot/disease-ai/ollama_server.py</string>
  </array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
</dict>
</plist>
```

โหลด:
```bash
launchctl load ~/Library/LaunchAgents/com.durionbot.ai.plist
```

### Linux (systemd) 
สร้าง `/etc/systemd/system/durionbot-ai.service`:
```ini
[Unit]
Description=DurionBot AI Wrapper
After=network.target ollama.service

[Service]
Type=simple
User=YOUR_USER
WorkingDirectory=/path/to/durionbot/disease-ai
ExecStart=/usr/bin/python3 /path/to/durionbot/disease-ai/ollama_server.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable durionbot-ai
sudo systemctl start durionbot-ai
```

---

## 🐛 ปัญหาที่พบบ่อย

### ❌ "Out of memory" ตอนใช้ llava
- llava:7b ต้องการ RAM อย่างน้อย 6 GB
- ถ้าเครื่องช้า ใช้รุ่นเล็กแทน: `ollama pull llava:7b-q4_0` (quantized, RAM น้อยกว่า)

### ❌ "model not found"  
รัน `ollama list` ดูว่าโมเดลโหลดมาแล้วหรือยัง  
ถ้าไม่มี → `ollama pull <ชื่อโมเดล>`

### ❌ ตอบช้ามาก
- ตรวจ CPU/GPU ของเครื่อง — ถ้าไม่มี GPU จะรันบน CPU ช้า ~10-30 วินาที/คำถาม
- แนะนำ: ลด context window (`ollama run model "..." --context-window 2048`)
- ถ้ามี NVIDIA GPU → Ollama จะใช้อัตโนมัติ (เร็วขึ้น 5-10 เท่า)

### ❌ ตอบไม่ใช่ภาษาไทย
- llama3.2:3b ภาษาไทยอ่อน → ใช้ prompt บังคับ:
  ```
  "ตอบเป็นภาษาไทยเท่านั้น ห้ามใช้ภาษาอังกฤษ: <คำถาม>"
  ```
- หรือดาวน์โหลดโมเดลใหญ่: `ollama pull llama3.1:8b` (ต้อง RAM 12 GB)

---

## ✅ Checklist ก่อนไปขั้นต่อไป

- [ ] รัน `ollama --version` ได้
- [ ] รัน `ollama list` เห็น `llama3.2:3b` และ `llava:7b`
- [ ] รัน `curl http://localhost:11434/api/tags` ได้ผล
- [ ] ทดสอบรูปด้วย llava ได้คำตอบ (อาจไม่แม่น 100% แต่ตอบได้)
- [ ] ตั้งค่าให้เปิดอัตโนมัติตอน boot

🎉 ขั้นตอนนี้เสร็จสมบูรณ์แล้ว → ไปต่อ [02-setup-cloudflare.md](02-setup-cloudflare.md)

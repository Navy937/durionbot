# Disease AI Wrapper

FastAPI server ที่ห่อ Ollama เพื่อให้ Cloudflare Worker เรียกใช้ได้

## Architecture

```
Cloudflare Worker (LINE webhook)
        │
        │ HTTPS via Cloudflare Tunnel
        ▼
ollama_server.py  (FastAPI :8000)
        │
        │ HTTP localhost:11434
        ▼
Ollama
        ├─ llama3.2:3b   (ตอบข้อความ)
        └─ llava:7b      (ดูรูป)
```

## ติดตั้ง
```bash
pip install -r requirements.txt
```

## รัน
```bash
# default port 8000
python ollama_server.py

# หรือ custom
PORT=8000 OLLAMA_URL=http://localhost:11434 python ollama_server.py
```

## ทดสอบ

### Health
```bash
curl http://localhost:8000/health
```

### วินิจฉัยจากข้อความ
```bash
curl -X POST http://localhost:8000/diagnose \
  -H "Content-Type: application/json" \
  -d '{"description":"ใบทุเรียนมีจุดสีน้ำตาล ขอบใบไหม้","mode":"text"}'
```

### วินิจฉัยจากรูป
```bash
# encode รูปก่อน
B64=$(base64 -w0 leaf.jpg)

curl -X POST http://localhost:8000/diagnose \
  -H "Content-Type: application/json" \
  -d "{\"image_base64\":\"$B64\",\"mode\":\"image\"}"
```

## ปรับ prompt template

แก้ใน `ollama_server.py` ฟังก์ชัน:
- `diagnose_image()` — prompt llava
- `diagnose_text()` — prompt llama3

หรือดู [obsidian-vault/10-ai-prompts/prompts.md](../obsidian-vault/10-ai-prompts/prompts.md) สำหรับ template ที่ tune แล้ว

## เปลี่ยน knowledge base

แก้ `disease_kb.json` → restart server

โครงสร้าง:
```json
{
  "diseases": [
    {
      "name": "ชื่อโรค",
      "scientific": "ชื่อวิทยาศาสตร์",
      "symptoms_keywords": ["keyword สำหรับ matching"],
      "description": "คำอธิบาย",
      "severity": "ระดับความรุนแรง",
      "treatment_steps": ["step 1", "step 2"],
      "chemicals": [{"name": "...", "dosage": "..."}],
      "prevention": "วิธีป้องกัน"
    }
  ]
}
```

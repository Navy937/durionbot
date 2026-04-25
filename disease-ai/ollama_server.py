"""
ollama_server.py — FastAPI wrapper รอบ Ollama

หน้าที่:
1. รับ HTTP request จาก Cloudflare Worker
2. โหลด prompt template ที่เหมาะสม
3. ส่งไป Ollama (localhost:11434)
4. แปลงผลลัพธ์เป็น JSON ที่ structured

วิธีรัน:
    pip install fastapi uvicorn requests pillow
    python ollama_server.py

จะรันที่ http://localhost:8000

ใช้กับ Cloudflare Tunnel เพื่อให้ Worker เข้าถึงได้
"""

import os
import io
import json
import base64
import logging
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from PIL import Image

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("ollama-wrapper")

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
TEXT_MODEL = os.environ.get("TEXT_MODEL", "llama3.2:3b")
IMAGE_MODEL = os.environ.get("IMAGE_MODEL", "llava:7b")

app = FastAPI(title="DurionBot Ollama Wrapper")


# โหลด disease knowledge base
KB_PATH = os.path.join(os.path.dirname(__file__), "disease_kb.json")
DISEASE_KB = {}
if os.path.exists(KB_PATH):
    with open(KB_PATH, encoding="utf-8") as f:
        DISEASE_KB = json.load(f)


class DiagnoseRequest(BaseModel):
    description: Optional[str] = None
    image_base64: Optional[str] = None
    mode: str = "text"  # "text" or "image"


class DiagnoseResponse(BaseModel):
    disease_name: str
    confidence: str
    description: str
    treatment_steps: list
    chemicals: list
    tips: str
    source: str


# ─────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    """ตรวจว่า Ollama พร้อม"""
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if r.ok:
            models = [m["name"] for m in r.json().get("models", [])]
            return {
                "status": "ok",
                "ollama": "connected",
                "models": models,
                "kb_diseases": len(DISEASE_KB.get("diseases", []))
            }
    except Exception as e:
        return {"status": "error", "ollama": str(e)}


@app.post("/diagnose", response_model=DiagnoseResponse)
def diagnose(req: DiagnoseRequest):
    """วินิจฉัยโรคจากรูปหรือข้อความ"""
    
    if req.mode == "image" and req.image_base64:
        return diagnose_image(req.image_base64)
    
    if req.mode == "text" and req.description:
        return diagnose_text(req.description)
    
    raise HTTPException(400, "Provide description (mode=text) or image_base64 (mode=image)")


# ─────────────────────────────────────────────────────────────────
# Image diagnosis with llava
# ─────────────────────────────────────────────────────────────────

def diagnose_image(image_b64: str) -> dict:
    """ใช้ llava วิเคราะห์รูป → match KB → return"""
    
    # 1. resize รูปให้เล็กลง (เร็วขึ้น)
    image_b64_resized = resize_image_b64(image_b64, max_size=512)
    
    prompt = """Analyze this durian (Thai fruit) plant image. Look for:
1. Disease symptoms on leaves (spots, holes, yellowing, browning)
2. Disease symptoms on fruits (rot, cracks, holes, fungus)
3. Disease symptoms on bark/trunk (cracks, sap, fungus)
4. Pest signs (insects, eggs, webs)

Respond in this EXACT format (English):
SYMPTOMS: <list visible symptoms>
LIKELY_DISEASE: <one disease name in Thai>
CONFIDENCE: low/medium/high
SEVERITY: low/medium/high
"""
    
    try:
        r = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": IMAGE_MODEL,
                "prompt": prompt,
                "images": [image_b64_resized],
                "stream": False,
                "options": {"temperature": 0.3}  # ต้องการความสม่ำเสมอ
            },
            timeout=120
        )
        r.raise_for_status()
        ollama_response = r.json().get("response", "")
        log.info(f"llava response: {ollama_response[:200]}")
    except Exception as e:
        log.error(f"llava failed: {e}")
        raise HTTPException(503, f"AI image model unavailable: {e}")
    
    # 2. parse และ match กับ KB
    disease_name, confidence = parse_llava_response(ollama_response)
    
    # 3. enrich จาก KB
    return enrich_with_kb(disease_name, confidence, "llava image analysis")


def parse_llava_response(text: str):
    """แยก disease name + confidence จาก response"""
    disease = "ไม่สามารถวินิจฉัยได้"
    confidence = "ต่ำ"
    
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("LIKELY_DISEASE:"):
            disease = line.replace("LIKELY_DISEASE:", "").strip()
        elif line.startswith("CONFIDENCE:"):
            c = line.replace("CONFIDENCE:", "").strip().lower()
            if "high" in c: confidence = "สูง"
            elif "medium" in c: confidence = "ปานกลาง"
            else: confidence = "ต่ำ"
    
    return disease, confidence


# ─────────────────────────────────────────────────────────────────
# Text diagnosis
# ─────────────────────────────────────────────────────────────────

def diagnose_text(description: str) -> dict:
    """ใช้ llama3 + KB matching"""
    
    # 1. ลอง keyword match กับ KB ก่อน (ฟรี เร็ว)
    matched = match_kb_keywords(description)
    if matched:
        return matched
    
    # 2. ถ้าไม่ match → ใช้ llama3
    diseases_list = "\n".join([
        f"- {d['name']}: {', '.join(d['symptoms_keywords'][:5])}"
        for d in DISEASE_KB.get("diseases", [])
    ])
    
    prompt = f"""You are an expert in durian (ทุเรียน) plant diseases.
A farmer describes the symptoms in Thai. Match to ONE disease from this list:

{diseases_list}

Farmer's description: "{description}"

Respond in this EXACT format:
DISEASE: <one disease name in Thai exactly as listed>
CONFIDENCE: low/medium/high
"""
    
    try:
        r = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": TEXT_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.2}
            },
            timeout=60
        )
        r.raise_for_status()
        response = r.json().get("response", "")
    except Exception as e:
        log.error(f"llama failed: {e}")
        # fallback: คืนข้อมูล generic
        return {
            "disease_name": "ไม่สามารถวินิจฉัยได้",
            "confidence": "ต่ำ",
            "description": description,
            "treatment_steps": ["ปรึกษานักวิชาการเกษตรในพื้นที่"],
            "chemicals": [],
            "tips": "AI ขัดข้อง — ลองอ่านในวิกิ",
            "source": "fallback"
        }
    
    # parse llama response
    disease = "ไม่สามารถวินิจฉัยได้"
    confidence = "ต่ำ"
    for line in response.splitlines():
        if line.startswith("DISEASE:"):
            disease = line.replace("DISEASE:", "").strip()
        elif line.startswith("CONFIDENCE:"):
            c = line.replace("CONFIDENCE:", "").strip().lower()
            if "high" in c: confidence = "สูง"
            elif "medium" in c: confidence = "ปานกลาง"
            else: confidence = "ต่ำ"
    
    return enrich_with_kb(disease, confidence, "llama3 text analysis")


def match_kb_keywords(description: str):
    """Keyword-based matching จาก KB (ไม่ใช้ AI)"""
    desc = description.lower()
    matches = []
    
    for d in DISEASE_KB.get("diseases", []):
        score = sum(1 for k in d["symptoms_keywords"] if k.lower() in desc)
        if score >= 2:
            matches.append((score, d))
    
    if not matches:
        return None
    
    matches.sort(reverse=True, key=lambda x: x[0])
    score, best = matches[0]
    
    return {
        "disease_name": best["name"],
        "confidence": "สูง" if score >= 3 else "ปานกลาง",
        "description": best["description"],
        "treatment_steps": best["treatment_steps"],
        "chemicals": best.get("chemicals", []),
        "tips": best.get("prevention", ""),
        "source": "knowledge base (keyword match)"
    }


def enrich_with_kb(disease_name: str, confidence: str, source: str):
    """ถ้า AI ตอบมา ดูใน KB แล้วเอา treatment ของจริงมาตอบ"""
    for d in DISEASE_KB.get("diseases", []):
        if d["name"] in disease_name or disease_name in d["name"]:
            return {
                "disease_name": d["name"],
                "confidence": confidence,
                "description": d["description"],
                "treatment_steps": d["treatment_steps"],
                "chemicals": d.get("chemicals", []),
                "tips": d.get("prevention", ""),
                "source": source
            }
    
    # ไม่เจอใน KB → คืน AI raw
    return {
        "disease_name": disease_name,
        "confidence": "ต่ำ",
        "description": "AI ระบุชื่อโรคไม่ตรงกับฐานข้อมูลของเรา",
        "treatment_steps": [
            "ลองส่งรูปอีกมุม (ใบ + ผล + ลำต้น)",
            "อธิบายอาการเป็นข้อความเพิ่มเติม",
            "ปรึกษานักวิชาการเกษตรในพื้นที่"
        ],
        "chemicals": [],
        "tips": "การวินิจฉัยควรดูประกอบสภาพอากาศ ดิน และประวัติการดูแล",
        "source": source
    }


# ─────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────

def resize_image_b64(b64_str: str, max_size: int = 512) -> str:
    """Resize รูป base64 ให้ขนาดไม่เกิน max_size px (เพื่อให้ llava เร็วขึ้น)"""
    try:
        img_bytes = base64.b64decode(b64_str)
        img = Image.open(io.BytesIO(img_bytes))
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        buf = io.BytesIO()
        if img.mode == "RGBA":
            img = img.convert("RGB")
        img.save(buf, format="JPEG", quality=85)
        return base64.b64encode(buf.getvalue()).decode("ascii")
    except Exception as e:
        log.warning(f"resize failed, using original: {e}")
        return b64_str


# ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    log.info(f"Starting on port {port}, Ollama at {OLLAMA_URL}")
    log.info(f"Models: text={TEXT_MODEL}, image={IMAGE_MODEL}")
    log.info(f"KB loaded: {len(DISEASE_KB.get('diseases', []))} diseases")
    uvicorn.run(app, host="0.0.0.0", port=port)

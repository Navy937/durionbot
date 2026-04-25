---
title: AI Prompt Templates
category: 10-ai-prompts
tags: [Ollama, prompts]
date-created: 2026-04-25
---

# 🤖 Prompt Templates สำหรับ Ollama

ใช้ใน `disease-ai/ollama_server.py` หรือเรียกตรงผ่าน `ollama run`

---

## 🦠 วินิจฉัยโรคจากรูป (llava)

````
Analyze this durian (Thai fruit) plant image. Look for:
1. Disease symptoms on leaves (spots, holes, yellowing, browning)
2. Disease symptoms on fruits (rot, cracks, holes, fungus)
3. Disease symptoms on bark/trunk (cracks, sap, fungus)
4. Pest signs (insects, eggs, webs)

Respond in this EXACT format:
SYMPTOMS: <list visible symptoms>
LIKELY_DISEASE: <one disease name in Thai>
CONFIDENCE: low/medium/high
SEVERITY: low/medium/high
````

**Tips ปรับปรุงผล**:
- ถ้า llava ตอบกว้างเกิน → เพิ่ม "Choose ONLY from this list: [โรคไฟทอป, ใบจุดสาหร่าย, แอนแทรคโนส, ราน้ำมัน, เพลี้ยไก่แจ้, หนอนเจาะผล, ผลเน่า]"
- ถ้าภาพเบลอ → return CONFIDENCE: low เสมอ

---

## 📝 วินิจฉัยจากคำอธิบาย (llama3.2)

````
You are an expert in durian (ทุเรียน) plant diseases.
A farmer describes the symptoms in Thai. Match to ONE disease from this list:

- โรคไฟทอปเทอรา: รากเน่า, โคนเน่า, น้ำยาง, ใบเหลือง, ยืนต้นตาย
- โรคใบจุดสาหร่าย: จุดสีน้ำตาล, จุดส้ม, ปื้น
- โรคแอนแทรคโนส: ใบไหม้, ใบจุดดำ, ผลเน่าดำ, ดอกร่วง
- โรคราน้ำมัน: ปื้นน้ำมัน, ใบเปื้อน, ใบเหลืองชื้น
- เพลี้ยไก่แจ้: ใบหงิก, ใบม้วน, ยอดอ่อนหงิก
- หนอนเจาะผล: ผลเป็นรู, ขี้หนอน, ผลร่วงก่อนสุก
- โรคผลเน่า: ขั้วเน่า, ผลร่วง, เน่าก่อนสุก

Farmer's description: "{description}"

Respond in this EXACT format:
DISEASE: <one disease name in Thai exactly as listed>
CONFIDENCE: low/medium/high
````

---

## 🌧️ สรุปแนวโน้มฝน

````
You are a weather analyst for Thai durian farmers.
Given this 7-day forecast for ต.ควนกลาง อ.พิปูน นครศรีธรรมราช:

{forecast_data}

Provide a 2-sentence summary in Thai for a farmer:
- Highlight days with heavy rain (>20mm)
- Recommend timing for spraying or harvesting
````

---

## 🍈 สรุปสถานการณ์ราคา

````
You are a market analyst for durian.
Given:
- Today's price: {today_price}
- Last 7 days history: {history}
- Current month: {month}

Write 2-3 sentences in Thai answering:
1. ราคาตอนนี้สูง/ต่ำเทียบกับช่วงเดียวกันปีที่แล้ว
2. ควรเก็บผลขายเร็วๆ หรือรอดู
````

---

## 💡 Best practices

1. **อย่าใช้ AI ตอบสิ่งที่ดึงข้อมูลตรงได้** — เปลืองเวลา + ความแม่นไม่เพิ่ม
2. **บังคับ format ตอบ** — ใช้ `EXACT format` + ตัวอักษรพิมพ์ใหญ่ทำให้ parse ง่าย
3. **Temperature ต่ำ** (0.2-0.3) สำหรับงานที่ต้องการความสม่ำเสมอ
4. **เลี่ยง chain prompts** — Ollama ช้า ตอบ 2-3 รอบจะเกิน LINE timeout
5. **ใส่ตัวอย่าง (few-shot)** ถ้า output ไม่นิ่ง

---

## 🔬 Fine-tuning roadmap (อนาคต)

ถ้าต้องการให้แม่นกว่านี้ ทำตามลำดับ:

1. **เก็บรูปโรคจริงจากสวน** ≥ 50 รูป/โรค (รวม 350+)
2. **Annotate**: ใส่ label ในแต่ละรูป (ใช้ LabelStudio ฟรี)
3. **Fine-tune llava** ด้วย Unsloth + LoRA (รันบน Colab T4 ฟรี)
4. **Replace** model ใน `ollama_server.py` env: `IMAGE_MODEL=llava-durian-v1`

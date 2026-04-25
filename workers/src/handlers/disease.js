/**
 * Disease Handler — วินิจฉัยโรคทุเรียน
 *
 * Flow:
 *  1. ถ้าเป็น "image" → ดาวน์โหลดรูปจาก LINE → ส่งไป Ollama (llava) → ตอบกลับ
 *  2. ถ้าเป็น "text" → ลอง match กับ knowledge base ก่อน → ถ้าไม่ match → ส่งไป Ollama
 *
 * Token Claude ที่ใช้: 0 (ใช้ Ollama ทั้งหมด)
 */

import { getMessageContent } from '../lib/line-reply.js';

export async function handleDisease({ type, messageId, description, env }) {
  // ส่งข้อความ "กำลังวิเคราะห์..." รอไม่ได้ใน webhook
  // (จริงๆ ต้องตอบใน 5 วิ → ส่ง Ollama ไม่ทัน)
  // วิธีแก้: rule-based ก่อน + ส่ง follow-up ทีหลัง
  // → ในตัวอย่างนี้ใช้ rule-based + simple analysis

  if (type === 'image') {
    return await diagnoseFromImage(messageId, env);
  }

  if (type === 'text') {
    return await diagnoseFromText(description, env);
  }
}

/**
 * วินิจฉัยจากรูป — ส่งไป Ollama llava
 */
async function diagnoseFromImage(messageId, env) {
  try {
    // 1. ดึงรูปจาก LINE
    const imageBuffer = await getMessageContent(messageId, env.LINE_CHANNEL_ACCESS_TOKEN);

    // 2. encode base64
    const base64Image = arrayBufferToBase64(imageBuffer);

    // 3. ส่งไป Ollama (ผ่าน Cloudflare Tunnel)
    const ollamaUrl = env.OLLAMA_TUNNEL_URL || 'https://durionbot-ai.YOUR-DOMAIN.com';

    const response = await Promise.race([
      fetch(`${ollamaUrl}/diagnose`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          image_base64: base64Image,
          mode: 'image'
        })
      }),
      // timeout 4.5 วินาที (LINE timeout 5 วิ)
      new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 4500))
    ]);

    if (!response.ok) {
      throw new Error(`Ollama returned ${response.status}`);
    }

    const result = await response.json();
    return [buildDiseaseFlex(result)];

  } catch (err) {
    console.error('diagnoseFromImage error:', err);

    if (err.message === 'timeout') {
      return [{
        type: 'text',
        text: '⏳ รูปกำลังประมวลผล... อาจใช้เวลาสักครู่\n\nเดี๋ยวระบบจะส่งผลให้ผ่านข้อความ หรือลองส่งรูปที่ชัดกว่านี้ครับ'
      }];
    }

    return [{
      type: 'text',
      text: '⚠️ AI ที่บ้านขัดข้องชั่วคราว ลองพิมพ์อาการเป็นข้อความแทนได้ครับ\n\nเช่น: "ใบทุเรียนมีจุดสีน้ำตาล ขอบใบไหม้"'
    }];
  }
}

/**
 * วินิจฉัยจากข้อความ
 * Step 1: ลอง match กับ disease knowledge base ใน KV
 * Step 2: ถ้า match ไม่ได้ → ส่งไป Ollama
 */
async function diagnoseFromText(description, env) {
  // 1. ลอง match กับฐานความรู้ก่อน (ฟรี เร็ว)
  const matched = await matchDiseaseFromKB(description, env);
  if (matched) {
    return [buildDiseaseFlex(matched)];
  }

  // 2. ถ้าไม่ match → ส่งไป Ollama
  try {
    const ollamaUrl = env.OLLAMA_TUNNEL_URL;
    const response = await fetch(`${ollamaUrl}/diagnose`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description, mode: 'text' })
    });

    if (!response.ok) throw new Error('Ollama unavailable');

    const result = await response.json();
    return [buildDiseaseFlex(result)];

  } catch (err) {
    return [{
      type: 'text',
      text: '⚠️ ไม่สามารถวินิจฉัยอัตโนมัติได้ตอนนี้\n\nลองอ่านข้อมูลโรคทุเรียนใน Wiki:\nhttps://github.com/YOUR-NAME/durionbot/tree/main/obsidian-vault/01-diseases'
    }];
  }
}

/**
 * Knowledge base matching — keyword-based
 * เก็บ symptoms → disease ใน KV
 */
async function matchDiseaseFromKB(description, env) {
  const kb = await env.DURIONBOT_KV.get('diseases:kb', 'json');
  if (!kb) return null;

  const desc = description.toLowerCase();
  const matches = [];

  for (const disease of kb.diseases) {
    let score = 0;
    for (const keyword of disease.symptoms_keywords) {
      if (desc.includes(keyword.toLowerCase())) score++;
    }
    if (score >= 2) {  // ต้องเจอ keyword อย่างน้อย 2 ตัว
      matches.push({ disease, score });
    }
  }

  if (matches.length === 0) return null;

  matches.sort((a, b) => b.score - a.score);
  const best = matches[0].disease;

  return {
    disease_name: best.name,
    confidence: matches[0].score >= 3 ? 'สูง' : 'ปานกลาง',
    description: best.description,
    treatment_steps: best.treatment_steps,
    chemicals: best.chemicals,
    tips: best.prevention,
    source: 'knowledge base (rule-based)'
  };
}

function buildDiseaseFlex(result) {
  return {
    type: 'flex',
    altText: `วินิจฉัย: ${result.disease_name}`,
    contents: {
      type: 'bubble', size: 'mega',
      header: {
        type: 'box', layout: 'vertical',
        backgroundColor: '#E74C3C', paddingAll: 'lg',
        contents: [
          { type: 'text', text: '🦠 วินิจฉัยโรค', color: '#FFFFFF', size: 'sm' },
          { type: 'text', text: result.disease_name, color: '#FFFFFF', weight: 'bold', size: 'lg', wrap: true }
        ]
      },
      body: {
        type: 'box', layout: 'vertical', spacing: 'md',
        contents: [
          { type: 'box', layout: 'horizontal', contents: [
            { type: 'text', text: 'ความมั่นใจ', flex: 2, size: 'sm', color: '#666666' },
            { type: 'text', text: result.confidence, flex: 3, size: 'sm', weight: 'bold',
              color: confidenceColor(result.confidence), align: 'end' }
          ]},
          { type: 'separator' },
          { type: 'text', text: '📝 ลักษณะ', weight: 'bold', color: '#666666' },
          { type: 'text', text: result.description, wrap: true, size: 'sm' },
          { type: 'separator' },
          { type: 'text', text: '💊 วิธีแก้', weight: 'bold', color: '#666666' },
          ...result.treatment_steps.slice(0, 4).map((step, i) => ({
            type: 'text',
            text: `${i+1}. ${step}`,
            wrap: true, size: 'sm', color: '#333333'
          })),
          ...(result.chemicals && result.chemicals.length > 0 ? [
            { type: 'separator' },
            { type: 'text', text: '🧪 สารเคมีที่แนะนำ', weight: 'bold', color: '#666666' },
            ...result.chemicals.slice(0, 3).map(c => ({
              type: 'text',
              text: `• ${c.name} ${c.dosage}`,
              wrap: true, size: 'xs', color: '#333333'
            }))
          ] : []),
          ...(result.tips ? [
            { type: 'separator' },
            { type: 'text', text: '💡 ป้องกัน', weight: 'bold', color: '#666666' },
            { type: 'text', text: result.tips, wrap: true, size: 'sm', color: '#666666' }
          ] : [])
        ]
      },
      footer: {
        type: 'box', layout: 'vertical',
        contents: [
          { type: 'text', text: '⚠️ การวินิจฉัยเบื้องต้น ปรึกษานักวิชาการเกษตรหากไม่แน่ใจ',
            size: 'xxs', color: '#999999', align: 'center', wrap: true }
        ]
      }
    }
  };
}

function confidenceColor(level) {
  if (level === 'สูง') return '#27AE60';
  if (level === 'ปานกลาง') return '#F39C12';
  return '#E74C3C';
}

function arrayBufferToBase64(buffer) {
  const bytes = new Uint8Array(buffer);
  let binary = '';
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

/**
 * DurionBot — Cloudflare Worker
 * รับ webhook จาก LINE → จำแนกคำถาม → ตอบกลับ
 *
 * ⚠️ ออกแบบให้ใช้ Claude API "เท่าที่จำเป็น" เท่านั้น
 * - คำถามที่ดึงข้อมูลตรงได้ (ฝน/ราคา/ปุ๋ย) → ตอบจาก KV cache (0 token)
 * - คำถามวินิจฉัยโรค → ส่งไป Ollama ที่บ้าน (0 token)
 * - คำถามคลุมเครือ ที่ rule-based ไม่เข้าใจ → ตอบ default + แนะนำคำสั่ง
 */

import { handleWeather }     from './handlers/weather.js';
import { handleDurianPrice } from './handlers/durian.js';
import { handleRubberPrice } from './handlers/rubber.js';
import { handleFertilizer }  from './handlers/fertilizer.js';
import { handleDisease }     from './handlers/disease.js';
import { handleHelp }        from './handlers/help.js';
import { classifyIntent }    from './intent.js';
import { verifySignature }   from './lib/line-signature.js';
import { replyMessage }      from './lib/line-reply.js';

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // health check endpoint
    if (url.pathname === '/health') {
      return new Response('OK', { status: 200 });
    }

    // LINE webhook endpoint
    if (url.pathname === '/webhook' && request.method === 'POST') {
      return await handleLineWebhook(request, env, ctx);
    }

    return new Response('Not Found', { status: 404 });
  },

  // GitHub Actions จะเรียก endpoint นี้เพื่อ push ข้อมูลใหม่
  // (จริงๆ แล้วใช้ HTTP request ก็ใช้ fetch handler ได้)
  async scheduled(event, env, ctx) {
    // optional: cron trigger to refresh cache
  }
};

async function handleLineWebhook(request, env, ctx) {
  // 1. ตรวจสอบ signature ป้องกันคนปลอม
  const body = await request.text();
  const signature = request.headers.get('x-line-signature');

  const valid = await verifySignature(body, signature, env.LINE_CHANNEL_SECRET);
  if (!valid) {
    return new Response('Invalid signature', { status: 401 });
  }

  // 2. parse events
  const { events } = JSON.parse(body);

  // 3. process แต่ละ event แบบขนาน
  ctx.waitUntil(Promise.all(
    events.map(event => processEvent(event, env))
  ));

  // ตอบ 200 ทันที (LINE timeout 5 วินาที)
  return new Response('OK', { status: 200 });
}

async function processEvent(event, env) {
  // เราสนใจแค่ message events
  if (event.type !== 'message') return;

  const replyToken = event.replyToken;
  const message = event.message;

  try {
    let messages;

    if (message.type === 'image') {
      // 🦠 ส่งรูป → วินิจฉัยโรค (ไป Ollama)
      messages = await handleDisease({
        type: 'image',
        messageId: message.id,
        env
      });
    } else if (message.type === 'text') {
      // 📝 ข้อความ → จำแนก intent
      const intent = classifyIntent(message.text);
      messages = await routeByIntent(intent, message.text, env);
    } else {
      // sticker, video, audio... ไม่รองรับ
      messages = [{
        type: 'text',
        text: 'ขอโทษครับ ตอนนี้รับเฉพาะ ข้อความ และ รูปภาพ เท่านั้น 🙏'
      }];
    }

    await replyMessage(replyToken, messages, env.LINE_CHANNEL_ACCESS_TOKEN);

  } catch (err) {
    console.error('processEvent error:', err);
    // ยังต้อง reply แม้จะ error เพื่อให้ user รู้
    await replyMessage(replyToken, [{
      type: 'text',
      text: '😅 ระบบขัดข้องชั่วคราว ลองใหม่อีกครั้งภายหลังครับ'
    }], env.LINE_CHANNEL_ACCESS_TOKEN);
  }
}

async function routeByIntent(intent, text, env) {
  switch (intent.category) {
    case 'weather':
      return await handleWeather({ text, days: intent.days, env });

    case 'durian':
      return await handleDurianPrice({ text, variety: intent.variety, env });

    case 'rubber':
      return await handleRubberPrice({ text, env });

    case 'fertilizer':
      return await handleFertilizer({ text, formula: intent.formula, env });

    case 'disease':
      // อธิบายอาการเป็นข้อความ (ไม่ใช่รูป)
      return await handleDisease({ type: 'text', description: text, env });

    case 'help':
      return handleHelp();

    case 'unknown':
    default:
      return [{
        type: 'text',
        text: `❓ ขอโทษครับ ผมไม่เข้าใจ ลองพิมพ์:

🌧️ "ฝน" — เช็คพยากรณ์
🍈 "ราคาทุเรียน" — ราคา + แนวโน้ม
🌳 "ราคายาง" — ตลาดยางพารา
🌱 "ปุ๋ย 15-15-15" — เปรียบเทียบราคา
🦠 ส่งรูปใบ/ผล — วินิจฉัยโรค
❓ "ช่วย" — เมนูทั้งหมด`
      }];
  }
}

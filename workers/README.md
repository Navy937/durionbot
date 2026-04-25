# Cloudflare Worker — DurionBot

LINE webhook handler

## โครงสร้าง

```
src/
├── index.js                # main entry — รับ webhook
├── intent.js               # rule-based intent classifier
├── lib/
│   ├── line-signature.js   # ตรวจ HMAC signature
│   └── line-reply.js       # ส่ง reply messages
└── handlers/
    ├── weather.js          # ฝน
    ├── durian.js           # ราคาทุเรียน
    ├── rubber.js           # ราคายาง
    ├── fertilizer.js       # ราคาปุ๋ย
    ├── disease.js          # วินิจฉัยโรค (เรียก Ollama)
    └── help.js             # เมนู
```

## ติดตั้ง
```bash
npm install
```

## Dev
```bash
npm run dev
# → http://localhost:8787
```

## Deploy
```bash
npm run deploy
```

## ดู log realtime
```bash
npm run tail
```

## Secrets ที่ต้องตั้ง
```bash
wrangler secret put LINE_CHANNEL_SECRET
wrangler secret put LINE_CHANNEL_ACCESS_TOKEN
wrangler secret put OLLAMA_TUNNEL_URL
```

## ตรวจ KV
```bash
npm run kv:list
wrangler kv:key get "weather:khuanklang" --binding DURIONBOT_KV
```

## เพิ่ม intent ใหม่

1. เพิ่ม keyword ใน `src/intent.js` → `KEYWORDS` object
2. สร้าง handler ใหม่ใน `src/handlers/<topic>.js`
3. import + เพิ่ม case ใน `src/index.js` → `routeByIntent()`

## ดูตัวอย่าง Flex Message

ใช้ LINE Flex Message Simulator: https://developers.line.biz/flex-simulator/

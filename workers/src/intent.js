/**
 * Intent Classifier — Rule-based (ไม่ใช้ AI)
 *
 * เหตุผลที่ rule-based: คำสั่งของเกษตรกรมี pattern ชัดเจน
 * ใช้ keyword matching ก็แม่นพอ + เร็ว + ไม่ต้องเสีย token
 *
 * ตัวอย่าง mapping:
 *   "ฝนวันนี้" → { category: 'weather', days: 1 }
 *   "ราคาหมอนทอง" → { category: 'durian', variety: 'หมอนทอง' }
 *   "ปุ๋ย 15-15-15" → { category: 'fertilizer', formula: '15-15-15' }
 */

const KEYWORDS = {
  weather: ['ฝน', 'อากาศ', 'พยากรณ์', 'อุณหภูมิ', 'ความชื้น', 'rain', 'weather'],
  durian:  ['ทุเรียน', 'หมอนทอง', 'ชะนี', 'ก้านยาว', 'กระดุม', 'พวงมณี', 'durian'],
  rubber:  ['ยาง', 'ยางพารา', 'น้ำยาง', 'ยางก้อน', 'ยางแผ่น', 'rubber'],
  fertilizer: ['ปุ๋ย', 'fertilizer', '15-15-15', '16-16-16', '13-13-21', '46-0-0', '21-0-0', '8-24-24'],
  disease: ['โรค', 'ใบไหม้', 'ราน้ำ', 'แอนแทรค', 'ไฟทอป', 'จุด', 'ดำ', 'เน่า', 'อาการ', 'รักษา', 'แมลง', 'ศัตรูพืช'],
  help: ['ช่วย', 'help', 'menu', 'เมนู', 'คำสั่ง', 'วิธี', 'ใช้ยังไง', 'ถามอะไรได้']
};

const VARIETIES = ['หมอนทอง', 'ชะนี', 'ก้านยาว', 'กระดุม', 'พวงมณี', 'มูซานคิง'];

const FERTILIZER_FORMULAS = [
  '15-15-15', '16-16-16', '13-13-21', '46-0-0', '21-0-0',
  '8-24-24', '0-3-0', '15-7-18', '12-12-17', '20-20-0'
];

export function classifyIntent(text) {
  const t = text.toLowerCase().trim();

  // 1. ตรวจ "ช่วย" ก่อน เพราะ keyword สั้น
  if (matchAny(t, KEYWORDS.help)) {
    return { category: 'help' };
  }

  // 2. ตรวจ disease (มี keyword เฉพาะ)
  if (matchAny(t, KEYWORDS.disease)) {
    return { category: 'disease' };
  }

  // 3. ตรวจ fertilizer + ดึงสูตร
  if (matchAny(t, KEYWORDS.fertilizer)) {
    const formula = FERTILIZER_FORMULAS.find(f => t.includes(f));
    return { category: 'fertilizer', formula: formula || null };
  }

  // 4. ตรวจ rubber (ก่อน durian เพราะ "ยาง" เฉพาะกว่า)
  if (matchAny(t, KEYWORDS.rubber) && !t.includes('ทุเรียน')) {
    return { category: 'rubber' };
  }

  // 5. ตรวจ durian + ดึงพันธุ์
  if (matchAny(t, KEYWORDS.durian)) {
    const variety = VARIETIES.find(v => t.includes(v));
    return { category: 'durian', variety: variety || 'หมอนทอง' };
  }

  // 6. ตรวจ weather + จำนวนวัน
  if (matchAny(t, KEYWORDS.weather)) {
    let days = 1; // default วันนี้
    if (t.includes('พรุ่งนี้') || t.includes('tomorrow')) days = 2;
    else if (t.includes('สัปดาห์') || t.includes('7 วัน') || t.includes('week')) days = 7;
    else if (t.includes('3 วัน')) days = 3;
    return { category: 'weather', days };
  }

  // 7. unknown
  return { category: 'unknown' };
}

function matchAny(text, keywords) {
  return keywords.some(k => text.includes(k.toLowerCase()));
}

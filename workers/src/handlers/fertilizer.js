/**
 * Fertilizer Comparison Handler
 *
 * ฟีเจอร์ตามที่ user ต้องการ:
 * 🌱 ราคาปุ๋ยแต่ละเจ้าตามสูตรที่ต้องใช้ (กรมวิชาการเกษตร)
 *    + เปรียบเทียบว่าเจ้าไหนในสูตรเดียวกันถูกกว่ากัน
 *    + ควรซื้อช่วงไหนจึงจะถูกที่สุด
 */

export async function handleFertilizer({ formula, env }) {
  // ถ้ายังไม่ระบุสูตร → ให้ user เลือก
  if (!formula) {
    return [showFormulaPicker()];
  }

  const cached = await env.DURIONBOT_KV.get('fertilizer:price', 'json');
  if (!cached) {
    return [{ type: 'text', text: '🌱 ข้อมูลราคาปุ๋ยยังไม่พร้อม' }];
  }

  const formulaData = cached.formulas[formula];
  if (!formulaData) {
    return [{
      type: 'text',
      text: `ขอโทษครับ ยังไม่มีข้อมูลสูตร ${formula}\n\nสูตรที่มี: ${Object.keys(cached.formulas).join(', ')}`
    }];
  }

  // เรียงจากถูกไปแพง
  const sorted = [...formulaData.brands].sort((a, b) => a.price - b.price);
  const cheapest = sorted[0];
  const expensive = sorted[sorted.length - 1];
  const savings = expensive.price - cheapest.price;

  return [buildFertilizerFlex(formula, sorted, cached, savings)];
}

function showFormulaPicker() {
  return {
    type: 'flex',
    altText: 'เลือกสูตรปุ๋ย',
    contents: {
      type: 'bubble',
      header: {
        type: 'box', layout: 'vertical',
        backgroundColor: '#8E44AD', paddingAll: 'md',
        contents: [
          { type: 'text', text: '🌱 เลือกสูตรปุ๋ย', color: '#FFFFFF', weight: 'bold' }
        ]
      },
      body: {
        type: 'box', layout: 'vertical', spacing: 'sm',
        contents: [
          { type: 'text', text: 'สูตรไหนที่ใช้บ่อย? (ตามช่วงต้นทุเรียน)', size: 'sm', color: '#666666', wrap: true },
          formulaButton('15-15-15', 'ก่อนเก็บผล (Balance)'),
          formulaButton('16-16-16', 'ทดแทน 15-15-15'),
          formulaButton('13-13-21', 'ตัดดอก/ติดผล (K สูง)'),
          formulaButton('46-0-0', 'ใบเขียว (ยูเรีย)'),
          formulaButton('8-24-24', 'หลังเก็บผล (P+K สูง)')
        ]
      }
    }
  };
}

function formulaButton(formula, description) {
  return {
    type: 'button', style: 'secondary', height: 'sm', margin: 'sm',
    action: {
      type: 'message',
      label: `${formula} (${description})`,
      text: `ปุ๋ย ${formula}`
    }
  };
}

function buildFertilizerFlex(formula, sortedBrands, cached, savings) {
  return {
    type: 'flex',
    altText: `เปรียบเทียบราคาปุ๋ย ${formula}`,
    contents: {
      type: 'bubble', size: 'giga',
      header: {
        type: 'box', layout: 'vertical',
        backgroundColor: '#8E44AD', paddingAll: 'lg',
        contents: [
          { type: 'text', text: `🌱 ปุ๋ย ${formula}`, color: '#FFFFFF', weight: 'bold', size: 'lg' },
          { type: 'text', text: `กระสอบ 50 กก. — ${sortedBrands.length} ยี่ห้อ`, color: '#F0E6F5', size: 'xs' }
        ]
      },
      body: {
        type: 'box', layout: 'vertical', spacing: 'sm',
        contents: [
          { type: 'text', text: 'เรียงจากถูกที่สุด', size: 'xs', color: '#666666' },
          ...sortedBrands.slice(0, 6).map((b, i) => ({
            type: 'box', layout: 'horizontal',
            contents: [
              { type: 'text', text: i === 0 ? '🥇' : (i === 1 ? '🥈' : (i === 2 ? '🥉' : `${i+1}.`)), flex: 1, size: 'sm' },
              { type: 'text', text: b.brand, flex: 5, size: 'sm', wrap: true },
              { type: 'text', text: `฿${b.price}`, flex: 2, size: 'sm', weight: 'bold', align: 'end',
                color: i === 0 ? '#27AE60' : '#333333' }
            ]
          })),
          { type: 'separator', margin: 'md' },
          { type: 'text', text: '💰 ความต่างราคา', weight: 'bold', color: '#666666', size: 'sm' },
          { type: 'text', text: `ประหยัดได้ ${savings} บาท/กระสอบ ถ้าซื้อยี่ห้อถูกที่สุด`, size: 'sm', color: '#27AE60', wrap: true },
          { type: 'separator' },
          { type: 'text', text: '🎯 ควรซื้อตอนไหน?', weight: 'bold', color: '#666666', size: 'sm' },
          { type: 'text', text: getBestBuyTime(formula, cached.seasonal_trends?.[formula]), wrap: true, size: 'sm', color: '#333333' }
        ]
      },
      footer: {
        type: 'box', layout: 'vertical',
        contents: [{
          type: 'text', text: `ที่มา: กรมการค้าภายใน + ร้านในพื้นที่ | อัปเดต: ${formatTime(cached.updated_at)}`,
          size: 'xxs', color: '#999999', align: 'center', wrap: true
        }]
      }
    }
  };
}

/**
 * แนะนำช่วงเวลาซื้อปุ๋ย
 *
 * Logic:
 * - ปุ๋ยจะถูกที่สุดตอน "ก่อนฤดูใส่" (low demand)
 * - 15-15-15 / 16-16-16 ใช้ก่อนเก็บผล → ราคาลดช่วง ม.ค.-ก.พ. (ก่อน peak ใช้ มี.ค.-พ.ค.)
 * - 13-13-21 ใช้ตัดดอก/ติดผล → ราคาลดช่วง พ.ย.-ธ.ค. (ก่อน peak ม.ค.-ก.พ.)
 * - 8-24-24 ใช้หลังเก็บผล → ราคาลดช่วง พ.ค.-มิ.ย. (ก่อน peak ส.ค.-ก.ย.)
 */
function getBestBuyTime(formula, trends) {
  const month = new Date().getMonth() + 1;

  const recommendations = {
    '15-15-15': {
      bestMonths: [1, 2],
      reason: 'ราคาต่ำสุดมัก ม.ค.-ก.พ. (ก่อน peak การใช้ มี.ค.-พ.ค.) แนะนำซื้อตุนช่วงนี้'
    },
    '16-16-16': {
      bestMonths: [1, 2],
      reason: 'ราคาต่ำสุดมัก ม.ค.-ก.พ. คล้าย 15-15-15'
    },
    '13-13-21': {
      bestMonths: [10, 11, 12],
      reason: 'ราคาต่ำสุด พ.ย.-ธ.ค. (ก่อน peak ม.ค.-ก.พ. ตอนตัดดอก) แนะนำซื้อตุน'
    },
    '8-24-24': {
      bestMonths: [5, 6],
      reason: 'ราคาต่ำสุด พ.ค.-มิ.ย. (ก่อน peak ส.ค.-ก.ย. หลังเก็บผล)'
    },
    '46-0-0': {
      bestMonths: [4, 5, 11, 12],
      reason: 'ราคาขึ้นลงตามนำเข้าจากตะวันออกกลาง ดูราคาตลาด USD/MT บ่อยๆ'
    }
  };

  const rec = recommendations[formula];
  if (!rec) return 'ติดตามราคา 1-2 สัปดาห์ก่อนซื้อจะดีกว่า';

  if (rec.bestMonths.includes(month)) {
    return `🟢 ตอนนี้คือช่วงดี! ${rec.reason}`;
  }
  return `🟡 ${rec.reason}`;
}

function formatTime(iso) {
  const d = new Date(iso);
  return `${d.getDate()}/${d.getMonth()+1}`;
}

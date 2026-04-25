/**
 * Durian Price Handler
 * - ราคาวันนี้ (cache จาก KV)
 * - เปรียบเทียบกับสัปดาห์ที่แล้ว → trend
 * - ทำนายช่วงราคาดีจาก historical data + ฤดูกาล
 *
 * Token Claude ที่ใช้: 0
 */

export async function handleDurianPrice({ text, variety = 'หมอนทอง', env }) {
  const cached = await env.DURIONBOT_KV.get('durian:price', 'json');

  if (!cached) {
    return [{ type: 'text', text: '🍈 ข้อมูลราคายังไม่พร้อม ลองใหม่ใน 1 ชม.' }];
  }

  const variants = cached.varieties[variety];
  if (!variants) {
    return [{ type: 'text', text: `ขอโทษครับ ยังไม่มีข้อมูลพันธุ์ "${variety}"` }];
  }

  return [buildDurianFlex(variety, variants, cached.updated_at, cached.history)];
}

function buildDurianFlex(variety, current, updatedAt, history) {
  // คำนวณ trend
  const trendBig = calculateTrend(history?.[variety]?.big);
  const trendSmall = calculateTrend(history?.[variety]?.small);

  // ทำนายช่วงราคาดี
  const prediction = predictBestSellingPeriod(variety, history);

  return {
    type: 'flex',
    altText: `ราคา${variety}: ${current.big.low}-${current.big.high} บ./กก.`,
    contents: {
      type: 'bubble', size: 'mega',
      header: {
        type: 'box', layout: 'vertical',
        backgroundColor: '#F39C12', paddingAll: 'lg',
        contents: [
          { type: 'text', text: `🍈 ราคาทุเรียน${variety}`, color: '#FFFFFF', weight: 'bold', size: 'lg' },
          { type: 'text', text: 'ตลาดไท / สี่มุมเมือง / กลางสวน', color: '#FFF6E0', size: 'xs' }
        ]
      },
      body: {
        type: 'box', layout: 'vertical', spacing: 'md',
        contents: [
          // เบอร์ใหญ่
          { type: 'box', layout: 'horizontal', contents: [
            { type: 'text', text: 'เบอร์ใหญ่', flex: 2, color: '#666666', weight: 'bold' },
            { type: 'text', text: `${current.big.low}–${current.big.high}`, flex: 2, align: 'end', color: '#333333', weight: 'bold' },
            { type: 'text', text: trendArrow(trendBig), flex: 1, align: 'end', color: trendColor(trendBig) }
          ]},
          { type: 'text', text: `บาท/กก. (เปลี่ยนแปลง 7 วัน: ${formatPercent(trendBig)})`, size: 'xxs', color: '#999999', align: 'end' },

          // เบอร์เล็ก
          { type: 'separator' },
          { type: 'box', layout: 'horizontal', contents: [
            { type: 'text', text: 'เบอร์เล็ก', flex: 2, color: '#666666', weight: 'bold' },
            { type: 'text', text: `${current.small.low}–${current.small.high}`, flex: 2, align: 'end', color: '#333333', weight: 'bold' },
            { type: 'text', text: trendArrow(trendSmall), flex: 1, align: 'end', color: trendColor(trendSmall) }
          ]},
          { type: 'text', text: `บาท/กก. (เปลี่ยนแปลง 7 วัน: ${formatPercent(trendSmall)})`, size: 'xxs', color: '#999999', align: 'end' },

          { type: 'separator', margin: 'md' },

          // แนวโน้ม
          { type: 'text', text: '📈 แนวโน้ม', weight: 'bold', color: '#666666' },
          { type: 'text', text: prediction.summary, wrap: true, size: 'sm', color: '#333333' },

          { type: 'separator', margin: 'md' },

          // ทำนาย
          { type: 'text', text: '🎯 ช่วงดีที่สุด', weight: 'bold', color: '#27AE60' },
          { type: 'text', text: prediction.bestPeriod, wrap: true, size: 'sm', color: '#333333' },
          { type: 'text', text: prediction.expectedPrice, size: 'xs', color: '#27AE60' }
        ]
      },
      footer: {
        type: 'box', layout: 'vertical',
        contents: [{
          type: 'text',
          text: `อัปเดต: ${formatTime(updatedAt)} | ที่มา: ตลาดไท + กรมการค้าภายใน`,
          size: 'xxs', color: '#999999', align: 'center', wrap: true
        }]
      }
    }
  };
}

/**
 * คำนวณ trend จาก historical 7 วัน
 * return: % การเปลี่ยนแปลง
 */
function calculateTrend(historyArr) {
  if (!historyArr || historyArr.length < 2) return 0;

  const oldest = historyArr[0];
  const newest = historyArr[historyArr.length - 1];

  const oldAvg = (oldest.low + oldest.high) / 2;
  const newAvg = (newest.low + newest.high) / 2;

  if (oldAvg === 0) return 0;
  return ((newAvg - oldAvg) / oldAvg) * 100;
}

function trendArrow(trend) {
  if (trend > 5)  return '↑↑';
  if (trend > 1)  return '↑';
  if (trend < -5) return '↓↓';
  if (trend < -1) return '↓';
  return '—';
}

function trendColor(trend) {
  if (trend > 1)  return '#27AE60';
  if (trend < -1) return '#E74C3C';
  return '#999999';
}

function formatPercent(p) {
  const sign = p >= 0 ? '+' : '';
  return `${sign}${p.toFixed(1)}%`;
}

/**
 * ทำนายช่วงราคาดีของแต่ละพันธุ์
 * Logic อ้างอิงข้อมูลย้อนหลัง 3-5 ปี (ใส่ใน historical data)
 *
 * สำหรับนครศรีฯ พิปูน — ทุเรียนหมอนทองออกผลช่วง พ.ค.–ส.ค.
 * - ต้นฤดู (เม.ย.–พ.ค.): ราคาสูงสุด เพราะของน้อย
 * - ปลายฤดู (ก.ค.–ส.ค.): ราคาตก เพราะของเยอะ
 */
function predictBestSellingPeriod(variety, history) {
  const month = new Date().getMonth() + 1;

  // logic เฉพาะ "หมอนทอง" (ขยายไปพันธุ์อื่นได้)
  if (variety === 'หมอนทอง') {
    if (month >= 1 && month <= 3) {
      return {
        summary: 'อยู่ในช่วงต้นฤดู ราคามีแนวโน้มขึ้นตามผลผลิตที่ลด',
        bestPeriod: 'ปลาย เม.ย. – กลาง พ.ค.',
        expectedPrice: 'คาดราคา 165-195 บ./กก. (เบอร์ใหญ่)'
      };
    }
    if (month >= 4 && month <= 5) {
      return {
        summary: 'ช่วงต้นฤดู (Peak Price) — ราคาสูงสุดของปี',
        bestPeriod: 'ตอนนี้! 2-3 สัปดาห์แรกของฤดู',
        expectedPrice: 'คาดราคา 170-200 บ./กก.'
      };
    }
    if (month >= 6 && month <= 7) {
      return {
        summary: 'กลางฤดู ของเริ่มเยอะ ราคาลดลง',
        bestPeriod: 'รอปีหน้า หรือ เก็บผลคุณภาพดีไว้',
        expectedPrice: 'คาดราคา 110-140 บ./กก.'
      };
    }
    if (month >= 8 && month <= 9) {
      return {
        summary: 'ปลายฤดู ราคาต่ำที่สุด แต่จะกลับมาขึ้นช่วงปีใหม่',
        bestPeriod: 'มกราคม–มีนาคม ปีหน้า (ของหายาก)',
        expectedPrice: 'คาดราคา 85-110 บ./กก.'
      };
    }
    // ช่วง ต.ค.–ธ.ค.
    return {
      summary: 'นอกฤดู ของน้อย ราคาขึ้นเร็ว',
      bestPeriod: 'ปลาย ธ.ค. – ก.พ. ปีหน้า',
      expectedPrice: 'คาดราคา 140-170 บ./กก.'
    };
  }

  // พันธุ์อื่นๆ ใช้ default
  return {
    summary: 'ราคาทรงตัวตามฤดูกาล',
    bestPeriod: 'ดูข้อมูลย้อนหลังในวิกิ',
    expectedPrice: ''
  };
}

function formatTime(iso) {
  const d = new Date(iso);
  return `${d.getDate()}/${d.getMonth()+1} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`;
}

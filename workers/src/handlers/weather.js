/**
 * Weather Handler — ตอบเรื่องฝน/อากาศ ต.ควนกลาง อ.พิปูน นครศรีฯ
 *
 * Token Claude ที่ใช้: 0
 * (ดึงจาก KV ซึ่ง GitHub Actions push ไว้ทุก 6 ชม.)
 */

const TARGET_AREA = 'ต.ควนกลาง อ.พิปูน จ.นครศรีธรรมราช';

export async function handleWeather({ text, days = 1, env }) {
  // ดึง cache จาก KV
  const cached = await env.DURIONBOT_KV.get('weather:khuanklang', 'json');

  if (!cached) {
    return [{
      type: 'text',
      text: '🌧️ ขอโทษครับ ข้อมูลพยากรณ์ฝนยังไม่พร้อม กรุณาลองใหม่ใน 1 ชั่วโมง'
    }];
  }

  // กรองตามจำนวนวันที่ขอ
  const forecast = cached.forecast.slice(0, days);

  // สร้าง Flex Message
  return [buildWeatherFlex(forecast, cached.updated_at)];
}

function buildWeatherFlex(forecast, updatedAt) {
  const today = forecast[0];
  const advice = generateAdvice(forecast);

  // ถ้าขอ 1 วัน → card เดียว
  if (forecast.length === 1) {
    return {
      type: 'flex',
      altText: `ฝน ${TARGET_AREA}: ${today.condition}`,
      contents: {
        type: 'bubble',
        size: 'kilo',
        header: {
          type: 'box', layout: 'vertical',
          backgroundColor: '#4A90E2',
          paddingAll: 'lg',
          contents: [
            { type: 'text', text: '🌧️ พยากรณ์ฝน', color: '#FFFFFF', size: 'lg', weight: 'bold' },
            { type: 'text', text: TARGET_AREA, color: '#E0F0FF', size: 'xs' }
          ]
        },
        body: {
          type: 'box', layout: 'vertical', spacing: 'md',
          contents: [
            { type: 'text', text: today.date_label, weight: 'bold', size: 'md' },
            { type: 'box', layout: 'horizontal', contents: [
              { type: 'text', text: today.condition, flex: 3, color: '#333333' },
              { type: 'text', text: `${today.rain_chance}%`, flex: 1, align: 'end', color: '#4A90E2', weight: 'bold' }
            ]},
            { type: 'separator' },
            kvRow('ปริมาณฝน', `${today.rain_mm} มม.`),
            kvRow('อุณหภูมิ', `${today.temp_min}–${today.temp_max} °C`),
            kvRow('ความชื้น', `${today.humidity}%`),
            kvRow('ลม', `${today.wind_kmh} กม./ชม.`),
            { type: 'separator' },
            { type: 'text', text: '💡 คำแนะนำ', weight: 'bold', color: '#666666' },
            { type: 'text', text: advice, wrap: true, size: 'sm', color: '#666666' }
          ]
        },
        footer: {
          type: 'box', layout: 'vertical',
          contents: [{
            type: 'text', text: `อัปเดต: ${formatTime(updatedAt)} | ที่มา: TMD`,
            size: 'xxs', color: '#999999', align: 'center'
          }]
        }
      }
    };
  }

  // หลายวัน → carousel
  return {
    type: 'flex',
    altText: `ฝน ${TARGET_AREA} ${forecast.length} วัน`,
    contents: {
      type: 'carousel',
      contents: forecast.map(day => ({
        type: 'bubble', size: 'micro',
        header: {
          type: 'box', layout: 'vertical',
          backgroundColor: getColorByRainChance(day.rain_chance),
          paddingAll: 'sm',
          contents: [
            { type: 'text', text: day.date_label, color: '#FFFFFF', weight: 'bold', size: 'sm' }
          ]
        },
        body: {
          type: 'box', layout: 'vertical', spacing: 'sm',
          contents: [
            { type: 'text', text: day.condition, size: 'xs', wrap: true },
            { type: 'text', text: `🌧️ ${day.rain_chance}%`, weight: 'bold', size: 'lg', color: '#4A90E2' },
            { type: 'text', text: `💧 ${day.rain_mm} มม.`, size: 'xs', color: '#666666' },
            { type: 'text', text: `🌡️ ${day.temp_min}–${day.temp_max}°`, size: 'xs', color: '#666666' }
          ]
        }
      }))
    }
  };
}

function getColorByRainChance(chance) {
  if (chance >= 70) return '#1E5BA8'; // ฟ้าเข้ม - ฝนแน่นอน
  if (chance >= 40) return '#4A90E2'; // ฟ้า - น่าจะฝน
  if (chance >= 20) return '#7BB3F0'; // ฟ้าอ่อน - อาจฝน
  return '#A8D5F5'; // ฟ้าจาง - แดด
}

/**
 * สร้างคำแนะนำเชิงเกษตร จากข้อมูลฝน
 * (rule-based ไม่ใช้ AI)
 */
function generateAdvice(forecast) {
  const today = forecast[0];
  const next3days = forecast.slice(0, 3);
  const heavyRainDays = next3days.filter(d => d.rain_mm >= 20).length;

  // logic แนะนำตามข้อมูลจริง
  if (today.rain_chance >= 70 && today.rain_mm >= 20) {
    return '⛈️ ฝนตกหนัก แนะนำ: เลื่อนการพ่นยา/ปุ๋ย, ตรวจการระบายน้ำในร่อง';
  }
  if (today.rain_chance >= 50) {
    return '☔ มีโอกาสฝน ควรพ่นยาก่อน 9 โมงเช้า หรือเลื่อนไปวันที่ฝนน้อยกว่า';
  }
  if (heavyRainDays >= 2) {
    return '⚠️ 3 วันข้างหน้ามีฝนหนักหลายวัน เฝ้าระวังโรครากเน่า/ราน้ำมัน, ตรวจร่องน้ำ';
  }
  if (today.rain_chance < 20 && today.temp_max >= 35) {
    return '☀️🔥 ร้อนแห้ง รดน้ำเช้า-เย็น ระวังเพลี้ยไฟ + ไรแดง';
  }
  if (today.rain_chance < 30) {
    return '☀️ อากาศเหมาะ พ่นยา/ปุ๋ยได้ปกติ';
  }
  return '🌤️ อากาศปกติ ดำเนินงานตามแผนได้';
}

function kvRow(key, value) {
  return {
    type: 'box', layout: 'horizontal',
    contents: [
      { type: 'text', text: key, size: 'sm', color: '#666666', flex: 2 },
      { type: 'text', text: value, size: 'sm', color: '#333333', flex: 3, align: 'end' }
    ]
  };
}

function formatTime(iso) {
  const d = new Date(iso);
  return `${d.getDate()}/${d.getMonth()+1} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`;
}

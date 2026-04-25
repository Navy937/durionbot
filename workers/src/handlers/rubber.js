/**
 * Rubber Price Handler
 * ราคายาง 5 ตลาด: หาดใหญ่, สุราษฎร์ธานี, นครศรีฯ, ยะลา, บุรีรัมย์
 */

export async function handleRubberPrice({ env }) {
  const cached = await env.DURIONBOT_KV.get('rubber:price', 'json');

  if (!cached) {
    return [{ type: 'text', text: '🌳 ข้อมูลราคายางยังไม่พร้อม' }];
  }

  return [buildRubberFlex(cached)];
}

function buildRubberFlex(data) {
  const markets = data.markets || [];

  return {
    type: 'flex',
    altText: `ราคายางพารา ${data.updated_at_label}`,
    contents: {
      type: 'bubble', size: 'mega',
      header: {
        type: 'box', layout: 'vertical',
        backgroundColor: '#27AE60', paddingAll: 'lg',
        contents: [
          { type: 'text', text: '🌳 ราคายางพารา', color: '#FFFFFF', weight: 'bold', size: 'lg' },
          { type: 'text', text: data.updated_at_label, color: '#E0F5E0', size: 'xs' }
        ]
      },
      body: {
        type: 'box', layout: 'vertical', spacing: 'sm',
        contents: [
          { type: 'text', text: 'ยางแผ่นดิบคุณภาพดี (บาท/กก.)', size: 'xs', color: '#666666' },
          ...markets.map(m => ({
            type: 'box', layout: 'horizontal',
            contents: [
              { type: 'text', text: m.name, flex: 4, size: 'sm', color: '#333333' },
              { type: 'text', text: `${m.price.toFixed(2)}`, flex: 2, align: 'end', size: 'sm', weight: 'bold' },
              { type: 'text', text: trendIcon(m.change), flex: 1, align: 'end', size: 'sm', color: trendColor(m.change) }
            ]
          })),
          { type: 'separator', margin: 'md' },
          { type: 'text', text: `📊 ยางก้อนถ้วย: ${data.lump?.toFixed(2) || '–'} บ./กก.`, size: 'sm', color: '#666666' },
          { type: 'text', text: `💧 น้ำยางสด: ${data.fresh?.toFixed(2) || '–'} บ./กก.`, size: 'sm', color: '#666666' },
          { type: 'separator' },
          { type: 'text', text: `📈 SICOM (ตลาดสิงคโปร์): ${data.sicom || '–'} ¢/กก.`, size: 'xs', color: '#999999' }
        ]
      },
      footer: {
        type: 'box', layout: 'vertical',
        contents: [{
          type: 'text', text: 'ที่มา: rakayang.net + ตลาดกลางหาดใหญ่',
          size: 'xxs', color: '#999999', align: 'center'
        }]
      }
    }
  };
}

function trendIcon(change) {
  if (change > 0.5) return '↑';
  if (change < -0.5) return '↓';
  return '—';
}

function trendColor(change) {
  if (change > 0.5) return '#27AE60';
  if (change < -0.5) return '#E74C3C';
  return '#999999';
}

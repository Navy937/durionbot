/**
 * Help Handler — ตอบเมื่อขอความช่วยเหลือ
 */
export function handleHelp() {
  return [{
    type: 'flex',
    altText: 'เมนู DurionBot',
    contents: {
      type: 'bubble', size: 'mega',
      header: {
        type: 'box', layout: 'vertical',
        backgroundColor: '#2C3E50', paddingAll: 'lg',
        contents: [
          { type: 'text', text: '🥭 DurionBot', color: '#FFFFFF', weight: 'bold', size: 'xl' },
          { type: 'text', text: 'ผู้ช่วยเกษตรกรทุเรียน', color: '#BDC3C7', size: 'sm' }
        ]
      },
      body: {
        type: 'box', layout: 'vertical', spacing: 'md',
        contents: [
          helpRow('🌧️', 'พิมพ์ "ฝน"', 'พยากรณ์ฝน 7 วัน ต.ควนกลาง'),
          helpRow('🍈', 'พิมพ์ "ราคาทุเรียน"', 'ราคา + แนวโน้ม + ทำนายช่วงดี'),
          helpRow('🌳', 'พิมพ์ "ราคายาง"', 'ราคา 5 ตลาด + ยางก้อน + น้ำยางสด'),
          helpRow('🌱', 'พิมพ์ "ปุ๋ย 15-15-15"', 'เปรียบเทียบราคาแต่ละยี่ห้อ'),
          helpRow('🦠', 'ส่งรูปใบ/ผลที่ผิดปกติ', 'AI วินิจฉัยโรค (ใช้เวลา ~10 วิ)'),
          helpRow('📝', 'อธิบายอาการ', 'เช่น "ใบไหม้ ขอบใบเหลือง"'),
          { type: 'separator' },
          { type: 'text', text: '💡 Tip: กดปุ่มเมนูด้านล่าง สะดวกกว่าพิมพ์',
            wrap: true, size: 'xs', color: '#666666' }
        ]
      }
    }
  }];
}

function helpRow(icon, command, description) {
  return {
    type: 'box', layout: 'vertical', spacing: 'xs',
    contents: [
      { type: 'box', layout: 'horizontal', contents: [
        { type: 'text', text: icon, flex: 1, size: 'lg' },
        { type: 'text', text: command, flex: 6, weight: 'bold', size: 'sm', color: '#2C3E50' }
      ]},
      { type: 'text', text: description, size: 'xs', color: '#7F8C8D', margin: 'none', offsetStart: 'xl' }
    ]
  };
}

/**
 * ส่ง reply messages กลับไป LINE
 * ⭐ เน้นว่าใช้ "reply" ไม่ใช่ "push" — reply ฟรีไม่นับโควต้า
 */
export async function replyMessage(replyToken, messages, accessToken) {
  // LINE จำกัด 5 messages ต่อ reply
  const safeMessages = messages.slice(0, 5);

  const res = await fetch('https://api.line.me/v2/bot/message/reply', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`
    },
    body: JSON.stringify({
      replyToken: replyToken,
      messages: safeMessages
    })
  });

  if (!res.ok) {
    const err = await res.text();
    console.error('LINE reply failed:', res.status, err);
    throw new Error(`LINE reply failed: ${res.status}`);
  }

  return res;
}

/**
 * ดึงรูปจาก LINE (สำหรับ image messages)
 * ใช้ตอนวินิจฉัยโรค
 */
export async function getMessageContent(messageId, accessToken) {
  const res = await fetch(
    `https://api-data.line.me/v2/bot/message/${messageId}/content`,
    { headers: { 'Authorization': `Bearer ${accessToken}` } }
  );

  if (!res.ok) {
    throw new Error(`Failed to get content: ${res.status}`);
  }

  return await res.arrayBuffer();
}

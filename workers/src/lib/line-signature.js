/**
 * ตรวจสอบ signature ของ LINE webhook
 * ป้องกันไม่ให้คนอื่นยิง endpoint ของเราได้โดยตรง
 *
 * อ้างอิง: https://developers.line.biz/en/reference/messaging-api/#signature-validation
 */
export async function verifySignature(body, signature, channelSecret) {
  if (!signature || !channelSecret) return false;

  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey(
    'raw',
    encoder.encode(channelSecret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  );

  const sig = await crypto.subtle.sign(
    'HMAC',
    key,
    encoder.encode(body)
  );

  const expectedSignature = btoa(String.fromCharCode(...new Uint8Array(sig)));
  return signature === expectedSignature;
}

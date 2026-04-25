"""
push_to_kv.py — push ข้อมูลที่ scrape มา ขึ้น Cloudflare KV

อ่านไฟล์ JSON จาก obsidian-vault/09-daily-data/ → ใช้ Cloudflare API ส่งขึ้น KV

ENV ที่ต้องมี:
    CF_ACCOUNT_ID
    CF_API_TOKEN
    CF_KV_NAMESPACE_ID
"""

import os
import json
import sys
import requests

ACCOUNT_ID = os.environ.get("CF_ACCOUNT_ID")
API_TOKEN = os.environ.get("CF_API_TOKEN")
NAMESPACE_ID = os.environ.get("CF_KV_NAMESPACE_ID")


# Mapping ไฟล์ → KV key
KV_MAPPING = {
    "obsidian-vault/09-daily-data/weather.json":         "weather:khuanklang",
    "obsidian-vault/09-daily-data/durian-price.json":    "durian:price",
    "obsidian-vault/09-daily-data/rubber-price.json":    "rubber:price",
    "obsidian-vault/09-daily-data/fertilizer-price.json": "fertilizer:price",
    "disease-ai/disease_kb.json":                        "diseases:kb",
}


def push_kv(key, value):
    """ใช้ Cloudflare API ส่งค่าเข้า KV"""
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/storage/kv/namespaces/{NAMESPACE_ID}/values/{key}"
    
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }
    
    r = requests.put(url, headers=headers, data=json.dumps(value).encode("utf-8"))
    
    if r.ok:
        return True
    else:
        print(f"[ERROR] PUT {key} failed: {r.status_code} {r.text}", file=sys.stderr)
        return False


def main():
    if not all([ACCOUNT_ID, API_TOKEN, NAMESPACE_ID]):
        print("[ERROR] Missing CF_ACCOUNT_ID / CF_API_TOKEN / CF_KV_NAMESPACE_ID", file=sys.stderr)
        sys.exit(1)
    
    success = 0
    failed = 0
    
    for filepath, key in KV_MAPPING.items():
        if not os.path.exists(filepath):
            print(f"[SKIP] {filepath} not found")
            continue
        
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
        
        if push_kv(key, data):
            print(f"[OK] {key} ← {filepath}")
            success += 1
        else:
            failed += 1
    
    print(f"\nResults: {success} OK, {failed} failed")
    
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()

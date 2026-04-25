"""
scrape_tiktok.py — เก็บลิงก์วิดีโอ TikTok เกี่ยวกับทุเรียน

⚠️ ข้อจำกัดสำคัญ:
- TikTok ไม่มี public API ฟรี (TikTok Research API จำกัดเฉพาะนักวิจัย)
- การ scrape โดยตรงผิด ToS ของ TikTok และอาจถูก block

ทางเลือกที่เราใช้:
1. **Manual entry** — เกษตรกร paste URL วิดีโอที่เจอเข้า Wiki เอง
2. **RSS feeds** — เว็บ third-party บางที่ทำ feed ของ TikTok hashtag
   (ความเสถียรต่ำ ใช้ได้บางช่วง)
3. **Bookmark in LINE** — เกษตรกรส่ง URL ใน LINE → Bot บันทึก

ตัว script นี้ทำหน้าที่:
- รวบรวม URL ที่เก็บมา (ไม่ scrape เอง)
- merge เข้า Wiki

ถ้าต้องการ scrape จริงๆ → ใช้ playwright + proxy (ผิด ToS — ไม่แนะนำ)
"""

import os
import json
import sys
from datetime import datetime, timezone

OUTPUT_PATH = "obsidian-vault/09-daily-data/tiktok-bookmarks.json"
INPUT_PATH = "obsidian-vault/08-sources/tiktok-bookmarks-input.txt"  # manual list


def main():
    # อ่าน manual entries (บรรทัดละ URL)
    entries = []
    
    if os.path.exists(INPUT_PATH):
        with open(INPUT_PATH, encoding="utf-8") as f:
            for line in f:
                url = line.strip()
                if url and (url.startswith("http") and "tiktok.com" in url):
                    entries.append({
                        "url": url,
                        "added_date": datetime.now().strftime("%Y-%m-%d"),
                        "source": "manual"
                    })
    
    output = {
        "entries": entries,
        "count": len(entries),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "note": (
            "TikTok ไม่มี public API — รวบรวมจาก manual entry. "
            "เพิ่ม URL ในไฟล์ obsidian-vault/08-sources/tiktok-bookmarks-input.txt บรรทัดละ 1 URL"
        )
    }
    
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] TikTok bookmarks: {len(entries)}")


if __name__ == "__main__":
    main()

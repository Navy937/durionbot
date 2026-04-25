"""
scrape_youtube.py — ดึงวิดีโอใหม่จาก YouTube (เกี่ยวกับทุเรียน)

ใช้ YouTube Data API v3 (official) — ฟรี 10,000 quota/วัน
1 search call = 100 quota → เราใช้ ~5-10 calls/วัน = พอเหมาะ

หมายเหตุ: ห้ามใช้ scraping unofficial — ผิด YouTube ToS
"""

import os
import json
import sys
from datetime import datetime, timedelta, timezone
import requests

OUTPUT_PATH = "obsidian-vault/09-daily-data/youtube-new-videos.json"
VAULT_PATH = "obsidian-vault/08-sources/youtube-collected.md"

# Keywords ที่จะค้นหา
SEARCH_QUERIES = [
    "ทุเรียน โรค",
    "ทุเรียน ปุ๋ย",
    "ทุเรียน ออกดอก",
    "ทุเรียน เก็บเกี่ยว",
    "ทุเรียนหมอนทอง พิปูน",
    "ทุเรียนนครศรีธรรมราช",
]


def search_youtube(api_key, query, max_results=5, days_back=7):
    """
    ค้นหา video ใหม่ตาม keyword
    """
    url = "https://www.googleapis.com/youtube/v3/search"
    
    published_after = (datetime.now(timezone.utc) - timedelta(days=days_back)).isoformat()
    
    params = {
        "key": api_key,
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "order": "date",
        "publishedAfter": published_after,
        "relevanceLanguage": "th",
        "regionCode": "TH",
    }
    
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        
        videos = []
        for item in data.get("items", []):
            videos.append({
                "id": item["id"]["videoId"],
                "title": item["snippet"]["title"],
                "channel": item["snippet"]["channelTitle"],
                "published": item["snippet"]["publishedAt"],
                "description": item["snippet"]["description"][:200],
                "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"],
                "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                "query": query,
            })
        return videos
    except Exception as e:
        print(f"[YouTube] '{query}' failed: {e}", file=sys.stderr)
        return []


def main():
    api_key = os.environ.get("YOUTUBE_API_KEY")
    
    if not api_key:
        print("[WARN] YOUTUBE_API_KEY not set, skipping", file=sys.stderr)
        # สร้างไฟล์ว่างเพื่อไม่ให้ pipeline พัง
        empty = {
            "videos": [],
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "note": "ไม่ได้ตั้งค่า YOUTUBE_API_KEY"
        }
        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(empty, f, ensure_ascii=False, indent=2)
        return
    
    all_videos = []
    seen_ids = set()
    
    for query in SEARCH_QUERIES:
        videos = search_youtube(api_key, query, max_results=5, days_back=7)
        for v in videos:
            if v["id"] not in seen_ids:
                seen_ids.add(v["id"])
                all_videos.append(v)
    
    # เรียงจากใหม่สุด
    all_videos.sort(key=lambda v: v["published"], reverse=True)
    
    output = {
        "videos": all_videos,
        "count": len(all_videos),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Found {len(all_videos)} new YouTube videos")
    
    update_vault_md(output)


def update_vault_md(data):
    """Append วิดีโอใหม่เข้า vault markdown (เก็บประวัติ)"""
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    new_section = [
        "",
        f"## ดึงวันที่ {today_str}",
        ""
    ]
    
    for v in data["videos"]:
        new_section.append(f"- [{v['title']}]({v['url']}) — {v['channel']} ({v['published'][:10]})")
        new_section.append(f"  > tags: {v['query']}")
    
    new_section.append("")
    
    # ถ้าไฟล์ยังไม่มี สร้าง header
    if not os.path.exists(VAULT_PATH):
        os.makedirs(os.path.dirname(VAULT_PATH), exist_ok=True)
        with open(VAULT_PATH, "w", encoding="utf-8") as f:
            f.write("# 📺 YouTube Videos Collected\n\n")
            f.write("วิดีโอใหม่ที่ scraper ดึงมาตามคำค้นหาที่ตั้งไว้\n")
    
    with open(VAULT_PATH, "a", encoding="utf-8") as f:
        f.write("\n".join(new_section))


if __name__ == "__main__":
    main()

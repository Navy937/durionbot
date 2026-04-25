"""
scrape_rubber.py — ดึงราคายางพาราจากตลาดกลาง 5 แห่ง

แหล่งข้อมูล: rakayang.net, thainr.com (กยท.)
"""

import os
import json
import sys
import re
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

OUTPUT_PATH = "obsidian-vault/09-daily-data/rubber-price.json"

MARKETS = [
    "หาดใหญ่", "สุราษฎร์ธานี", "นครศรีธรรมราช", "ยะลา", "บุรีรัมย์"
]


def scrape_rakayang():
    """rakayang.net รวมข้อมูลตลาดกลางหลายแห่ง"""
    url = "https://www.rakayang.net/ebayprice.php"
    headers = {"User-Agent": "Mozilla/5.0 DurionBot"}
    
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        
        markets = []
        # ลอง parse จาก table หรือ list
        for row in soup.select("table tr, .market-row, .price-row"):
            text = row.get_text(" ", strip=True)
            for m in MARKETS:
                if m in text:
                    nums = re.findall(r"(\d+\.\d+|\d+)", text)
                    if nums:
                        try:
                            markets.append({
                                "name": m,
                                "price": float(nums[0]),
                                "change": 0  # ไม่รู้ → 0
                            })
                        except ValueError:
                            pass
        
        return markets if markets else None
    except Exception as e:
        print(f"[rakayang] failed: {e}", file=sys.stderr)
        return None


def get_default_prices():
    """Fallback: ใช้ค่ากลางๆ ของไตรมาส (ถ้า scraper fail)"""
    # ค่าเฉลี่ยปี 2569 ประมาณ 60-70 บ./กก.
    return [
        {"name": m, "price": 65.50 + i * 0.5, "change": 0}
        for i, m in enumerate(MARKETS)
    ]


def main():
    markets = scrape_rakayang()
    source = "rakayang.net"
    
    if not markets or len(markets) < 2:
        print("[WARN] Scraping failed, using estimates", file=sys.stderr)
        markets = get_default_prices()
        source = "estimate"
    
    output = {
        "markets": markets,
        "lump": markets[0]["price"] * 0.55 if markets else None,  # ยางก้อนถ้วย ~55% ของแผ่นดิบ
        "fresh": markets[0]["price"] * 0.92 if markets else None,  # น้ำยางสด
        "sicom": None,  # ราคา SICOM ตลาดสิงคโปร์ (TODO)
        "source": source,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "updated_at_label": datetime.now().strftime("%d/%m/%Y %H:%M"),
    }
    
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Saved rubber prices ({source})")
    
    write_markdown(output)


def write_markdown(data):
    today_str = datetime.now().strftime("%Y-%m-%d")
    md_path = f"obsidian-vault/09-daily-data/{today_str}-rubber-price.md"
    
    lines = [
        "---",
        f"title: ราคายางพารา {today_str}",
        "category: rubber-price",
        f"date: {today_str}",
        f"source: {data['source']}",
        "tags: [#ราคา, #ยางพารา]",
        "---",
        "",
        f"# 🌳 ราคายางพารา {today_str}",
        "",
        "## ยางแผ่นดิบคุณภาพดี (บาท/กก.)",
        "",
        "| ตลาด | ราคา |",
        "|------|------|",
    ]
    
    for m in data["markets"]:
        lines.append(f"| {m['name']} | {m['price']:.2f} |")
    
    if data.get("lump"):
        lines += [
            "",
            f"- **ยางก้อนถ้วย**: {data['lump']:.2f} บ./กก.",
            f"- **น้ำยางสด**: {data['fresh']:.2f} บ./กก.",
        ]
    
    os.makedirs(os.path.dirname(md_path), exist_ok=True)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()

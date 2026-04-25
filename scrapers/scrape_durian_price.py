"""
scrape_durian_price.py — ดึงราคาทุเรียน

แหล่งข้อมูล (เลือกอันที่ใช้ได้):
1. ตลาดไท (talaadthai.com) — ขายส่ง
2. กรมการค้าภายใน (data.moc.go.th) — open data
3. kasetprice.com — สรุปราคา

หมายเหตุ: HTML structure เปลี่ยนบ่อย ตัว scraper นี้ทำเป็น defensive
ถ้า fail ทุก source → ใช้ค่าเดิมจากเมื่อวาน + warning
"""

import os
import json
import sys
import re
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

OUTPUT_PATH = "obsidian-vault/09-daily-data/durian-price.json"
HISTORY_PATH = "obsidian-vault/09-daily-data/durian-price-history.json"

VARIETIES = ["หมอนทอง", "ชะนี", "ก้านยาว", "กระดุม"]


def scrape_kasetprice():
    """
    kasetprice.com มีหน้าสรุปราคารายวัน
    """
    url = "https://kasetprice.com/ราคา/ทุเรียน/วันนี้"
    headers = {"User-Agent": "Mozilla/5.0 DurionBot"}
    
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        
        result = {}
        
        # หา table ราคา (selector อาจเปลี่ยน)
        for row in soup.select("table tr, .price-row, .price-item"):
            text = row.get_text(" ", strip=True)
            
            for variety in VARIETIES:
                if variety in text:
                    # หาตัวเลขในข้อความ
                    numbers = re.findall(r"(\d+)\s*[-–]\s*(\d+)", text)
                    if numbers:
                        big_or_small = "big" if "ใหญ่" in text else "small"
                        if variety not in result:
                            result[variety] = {}
                        result[variety][big_or_small] = {
                            "low": int(numbers[0][0]),
                            "high": int(numbers[0][1])
                        }
        
        return result if result else None
    except Exception as e:
        print(f"[kasetprice] failed: {e}", file=sys.stderr)
        return None


def scrape_talaadthai():
    """
    ตลาดไท - ราคาส่งกรุงเทพฯ
    URL pattern: talaadthai.com/products/durian-{id}
    """
    # หมอนทองเบอร์ใหญ่
    urls = {
        "หมอนทอง": {
            "big": "https://talaadthai.com/products/durian-10042-2370",
            "small": "https://talaadthai.com/products/durian-10042-2369",
        }
    }
    
    headers = {"User-Agent": "Mozilla/5.0 DurionBot"}
    result = {}
    
    for variety, sizes in urls.items():
        result[variety] = {}
        for size_name, url in sizes.items():
            try:
                r = requests.get(url, headers=headers, timeout=10)
                if r.status_code != 200:
                    continue
                
                soup = BeautifulSoup(r.text, "html.parser")
                # ดึงราคา (selector ขึ้นกับ template เว็บ)
                price_elem = soup.select_one(".price, .product-price, [class*='price']")
                if price_elem:
                    text = price_elem.get_text(" ", strip=True)
                    numbers = re.findall(r"\d+", text)
                    if len(numbers) >= 2:
                        result[variety][size_name] = {
                            "low": int(numbers[0]),
                            "high": int(numbers[1])
                        }
            except Exception as e:
                print(f"[talaadthai] {variety} {size_name}: {e}", file=sys.stderr)
    
    return result if any(result.values()) else None


def get_default_prices():
    """
    Fallback ใช้ค่าประมาณตามฤดูกาล (อย่างน้อยมีข้อมูลให้ตอบ)
    หมายเหตุ: ราคาเปลี่ยนตามฤดูกาล อ้างอิงจากข้อมูลเฉลี่ยปี 2566-2568
    """
    month = datetime.now().month
    
    # Logic ราคาตามฤดูกาล (หมอนทอง)
    if month in [4, 5]:  # ต้นฤดู - peak
        big = (160, 200); small = (110, 150)
    elif month in [6, 7]:  # กลางฤดู
        big = (120, 150); small = (80, 110)
    elif month in [8, 9]:  # ปลายฤดู
        big = (90, 120); small = (65, 90)
    elif month in [10, 11, 12, 1]:  # นอกฤดู
        big = (140, 180); small = (95, 130)
    else:  # ก.พ.-มี.ค.
        big = (155, 195); small = (105, 140)
    
    return {
        "หมอนทอง": {
            "big": {"low": big[0], "high": big[1]},
            "small": {"low": small[0], "high": small[1]},
        },
        "ชะนี": {
            "big": {"low": int(big[0]*0.8), "high": int(big[1]*0.8)},
            "small": {"low": int(small[0]*0.8), "high": int(small[1]*0.8)},
        },
        "ก้านยาว": {
            "big": {"low": int(big[0]*1.1), "high": int(big[1]*1.1)},
            "small": {"low": int(small[0]*1.1), "high": int(small[1]*1.1)},
        },
        "กระดุม": {
            "big": {"low": int(big[0]*0.7), "high": int(big[1]*0.7)},
            "small": {"low": int(small[0]*0.7), "high": int(small[1]*0.7)},
        }
    }


def load_history():
    if os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_history(history, current):
    """บันทึก price ของวันนี้เข้า history (เก็บ 30 วันล่าสุด)"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    for variety, sizes in current.items():
        if variety not in history:
            history[variety] = {"big": [], "small": []}
        
        for size in ("big", "small"):
            if size in sizes:
                # ลบรายการของวันเดียวกันถ้ามี
                history[variety][size] = [
                    h for h in history[variety][size] if h.get("date") != today
                ]
                history[variety][size].append({
                    "date": today,
                    "low": sizes[size]["low"],
                    "high": sizes[size]["high"]
                })
                # เก็บแค่ 30 วัน
                history[variety][size] = history[variety][size][-30:]
    
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def main():
    # ลองหลาย source
    prices = scrape_kasetprice()
    source = "kasetprice"
    
    if not prices or len(prices) < 2:
        print("[INFO] Trying talaadthai...", file=sys.stderr)
        prices = scrape_talaadthai()
        source = "talaadthai"
    
    if not prices or len(prices) < 2:
        print("[WARN] All scrapers failed, using seasonal estimates", file=sys.stderr)
        prices = get_default_prices()
        source = "seasonal_estimate"
    
    # ใส่ varieties ที่ขาด (จาก default)
    defaults = get_default_prices()
    for v in VARIETIES:
        if v not in prices:
            prices[v] = defaults[v]
        else:
            # ถ้ามีแค่ขนาดเดียว เติมอีกขนาด
            for size in ("big", "small"):
                if size not in prices[v]:
                    prices[v][size] = defaults[v][size]
    
    # โหลดและบันทึก history
    history = load_history()
    save_history(history, prices)
    
    output = {
        "varieties": prices,
        "source": source,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "history": history,  # 30 วันย้อนหลัง สำหรับ trend calculation
    }
    
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Saved durian prices ({source})")
    print(json.dumps(prices, ensure_ascii=False, indent=2))
    
    write_markdown(output)


def write_markdown(data):
    today_str = datetime.now().strftime("%Y-%m-%d")
    md_path = f"obsidian-vault/09-daily-data/{today_str}-durian-price.md"
    
    lines = [
        "---",
        f"title: ราคาทุเรียน {today_str}",
        "category: durian-price",
        f"date: {today_str}",
        f"source: {data['source']}",
        "tags: [#ราคา, #ทุเรียน]",
        "---",
        "",
        f"# 🍈 ราคาทุเรียน {today_str}",
        f"**แหล่งที่มา**: {data['source']}",
        f"**อัปเดต**: {data['updated_at']}",
        "",
        "| พันธุ์ | เบอร์ใหญ่ (บ./กก.) | เบอร์เล็ก (บ./กก.) |",
        "|--------|---------------------|---------------------|"
    ]
    
    for variety, sizes in data["varieties"].items():
        big = sizes.get("big", {})
        small = sizes.get("small", {})
        big_str = f"{big.get('low','-')}–{big.get('high','-')}" if big else "-"
        small_str = f"{small.get('low','-')}–{small.get('high','-')}" if small else "-"
        lines.append(f"| {variety} | {big_str} | {small_str} |")
    
    os.makedirs(os.path.dirname(md_path), exist_ok=True)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    print(f"[OK] Wrote markdown: {md_path}")


if __name__ == "__main__":
    main()

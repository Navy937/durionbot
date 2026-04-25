"""
scrape_fertilizer.py — ราคาปุ๋ยเคมี เปรียบเทียบยี่ห้อ

แหล่งข้อมูล:
- กรมการค้าภายใน (data.moc.go.th) — official open data
- ร้านในพื้นที่ (manual entry)

หมายเหตุ: ราคาปุ๋ยเปลี่ยนตามฤดูกาล + ราคาน้ำมัน + ค่าเงินบาท
ค่าที่ใช้คือราคาเฉลี่ยตลาดทั่วประเทศ — ราคาในพื้นที่อาจต่างกันได้ ±5-10%
"""

import os
import json
import sys
from datetime import datetime, timezone
import requests

OUTPUT_PATH = "obsidian-vault/09-daily-data/fertilizer-price.json"


# โครงสร้างข้อมูล: สูตร → list of brands พร้อมราคา/กระสอบ 50 กก.
# ค่าอ้างอิงเดือน เม.ย. 2569 (ปรับตามจริงผ่าน manual entry)
FERTILIZER_DATA = {
    "15-15-15": {
        "description": "สูตรสมดุล ใช้ก่อนเก็บผล / บำรุงทั่วไป",
        "brands": [
            {"brand": "ตราหัววัว-คันไถ", "price": 980, "type": "นำเข้า"},
            {"brand": "ตรากระต่าย", "price": 920, "type": "ในประเทศ"},
            {"brand": "ตรารุ้ง", "price": 950, "type": "ในประเทศ"},
            {"brand": "ตรามงกุฎ", "price": 990, "type": "นำเข้า"},
            {"brand": "เจียไต๋", "price": 1010, "type": "นำเข้า"},
            {"brand": "เกษตรไทย", "price": 905, "type": "ในประเทศ"},
        ]
    },
    "16-16-16": {
        "description": "ทดแทน 15-15-15 ความเข้มข้นสูงกว่า",
        "brands": [
            {"brand": "ตราหัววัว-คันไถ", "price": 1020, "type": "นำเข้า"},
            {"brand": "ตรากระต่าย", "price": 970, "type": "ในประเทศ"},
            {"brand": "ตรารุ้ง", "price": 985, "type": "ในประเทศ"},
            {"brand": "เจียไต๋", "price": 1050, "type": "นำเข้า"},
            {"brand": "ปุ๋ยตราใบไม้", "price": 940, "type": "ในประเทศ"},
        ]
    },
    "13-13-21": {
        "description": "K สูง ใช้ตัดดอก/ติดผล/เพิ่มน้ำหนักผล",
        "brands": [
            {"brand": "ตราหัววัว-คันไถ", "price": 1090, "type": "นำเข้า"},
            {"brand": "ตรากระต่าย", "price": 1030, "type": "ในประเทศ"},
            {"brand": "ตรามงกุฎ", "price": 1080, "type": "นำเข้า"},
            {"brand": "เจียไต๋", "price": 1120, "type": "นำเข้า"},
            {"brand": "ตรารุ้ง", "price": 1050, "type": "ในประเทศ"},
        ]
    },
    "46-0-0": {
        "description": "ยูเรีย — เร่งใบเขียว N เดี่ยว",
        "brands": [
            {"brand": "ยูเรียจีน", "price": 850, "type": "นำเข้า"},
            {"brand": "ยูเรียอินโด", "price": 870, "type": "นำเข้า"},
            {"brand": "ยูเรียอิหร่าน", "price": 820, "type": "นำเข้า"},
            {"brand": "ตรากระต่าย", "price": 890, "type": "ในประเทศ"},
        ]
    },
    "8-24-24": {
        "description": "P+K สูง ใช้หลังเก็บผล/บำรุงราก",
        "brands": [
            {"brand": "ตราหัววัว-คันไถ", "price": 1010, "type": "นำเข้า"},
            {"brand": "ตรากระต่าย", "price": 950, "type": "ในประเทศ"},
            {"brand": "ตรารุ้ง", "price": 970, "type": "ในประเทศ"},
            {"brand": "เจียไต๋", "price": 1030, "type": "นำเข้า"},
        ]
    },
    "21-0-0": {
        "description": "แอมโมเนียมซัลเฟต — N + S",
        "brands": [
            {"brand": "ตรากระต่าย", "price": 580, "type": "ในประเทศ"},
            {"brand": "ตราใบไม้", "price": 560, "type": "ในประเทศ"},
            {"brand": "ตราหัววัว", "price": 610, "type": "นำเข้า"},
        ]
    }
}


# Trend data — % การเปลี่ยนแปลงเฉลี่ย 12 เดือนที่ผ่านมา (ของแต่ละสูตร)
SEASONAL_TRENDS = {
    "15-15-15": {
        1: -3, 2: -2, 3: 5, 4: 8, 5: 6, 6: 0, 7: -2, 8: -3, 9: -2, 10: 0, 11: 2, 12: 1
    },
    "16-16-16": {
        1: -3, 2: -2, 3: 5, 4: 7, 5: 5, 6: 0, 7: -2, 8: -3, 9: -2, 10: 0, 11: 2, 12: 1
    },
    "13-13-21": {
        1: 4, 2: 5, 3: -1, 4: -2, 5: -3, 6: -2, 7: -2, 8: 0, 9: 2, 10: 4, 11: -2, 12: -3
    },
    "46-0-0": {
        1: 0, 2: 1, 3: 4, 4: -2, 5: -4, 6: -1, 7: 0, 8: 1, 9: 2, 10: 0, 11: -2, 12: -3
    },
    "8-24-24": {
        1: 0, 2: 1, 3: 2, 4: 4, 5: -3, 6: -4, 7: -2, 8: 1, 9: 3, 10: 2, 11: 0, 12: 0
    }
}


def try_scrape_moc():
    """
    ลองดึงจากกรมการค้าภายใน (Open data)
    https://data.moc.go.th/OpenData/GISProductPrice
    
    NOTE: API ของ MOC ค่อนข้างยุ่ง ต้องใช้รหัสสินค้า
    เนื่องจากปุ๋ยมีหลายสูตร เลย default ใช้ static data
    ถ้าคุณอยาก enable ลบ comment ส่วนนี้แล้วเขียน parsing เพิ่ม
    """
    return None


def main():
    # 1. ลอง scrape ก่อน (ตอนนี้ return None — ใช้ static data)
    scraped = try_scrape_moc()
    
    if scraped:
        formulas = scraped
        source = "moc.go.th"
    else:
        formulas = FERTILIZER_DATA
        source = "static_reference (Apr 2026)"
    
    output = {
        "formulas": formulas,
        "seasonal_trends": SEASONAL_TRENDS,
        "source": source,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "note": "ราคาเป็นค่าเฉลี่ยตลาดทั่วประเทศ ราคาในพื้นที่อาจต่างกัน ±5-10%"
    }
    
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Saved fertilizer prices ({source})")
    print(f"     {len(formulas)} formulas, {sum(len(d['brands']) for d in formulas.values())} total brands")
    
    write_markdown(output)


def write_markdown(data):
    today_str = datetime.now().strftime("%Y-%m-%d")
    md_path = f"obsidian-vault/09-daily-data/{today_str}-fertilizer-price.md"
    
    lines = [
        "---",
        f"title: ราคาปุ๋ย {today_str}",
        "category: fertilizer-price",
        f"date: {today_str}",
        f"source: {data['source']}",
        "tags: [#ราคา, #ปุ๋ย]",
        "---",
        "",
        f"# 🌱 ราคาปุ๋ย {today_str}",
        "",
        f"> {data['note']}",
        "",
    ]
    
    for formula, info in data["formulas"].items():
        lines += [
            f"## สูตร {formula}",
            f"_{info['description']}_",
            "",
            "| ยี่ห้อ | ราคา (บ./กระสอบ 50 กก.) | ประเภท |",
            "|--------|--------------------------|---------|"
        ]
        # เรียงจากถูก
        sorted_brands = sorted(info["brands"], key=lambda x: x["price"])
        for b in sorted_brands:
            marker = "🥇 " if b == sorted_brands[0] else ""
            lines.append(f"| {marker}{b['brand']} | {b['price']} | {b['type']} |")
        lines.append("")
    
    os.makedirs(os.path.dirname(md_path), exist_ok=True)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()

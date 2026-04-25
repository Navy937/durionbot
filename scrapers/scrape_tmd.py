"""
scrape_tmd.py — ดึงพยากรณ์อากาศ ต.ควนกลาง อ.พิปูน จ.นครศรีธรรมราช จาก TMD API

วิธีรัน:
    python scrape_tmd.py

ENV ที่ต้องมี:
    TMD_API_KEY = JWT token จาก TMD
    
Output: weather.json (KV value พร้อม push)

ถ้า TMD ใช้ไม่ได้ → fallback ใช้ Open-Meteo (ไม่ต้องสมัคร)
"""

import os
import json
import sys
from datetime import datetime, timedelta, timezone
import requests

# พิกัด ต.ควนกลาง อ.พิปูน นครศรีธรรมราช
LATITUDE = 8.495
LONGITUDE = 99.652

PROVINCE = "นครศรีธรรมราช"
AMPHOE = "พิปูน"
TAMBON = "ควนกลาง"

OUTPUT_PATH = "obsidian-vault/09-daily-data/weather.json"


def fetch_from_tmd(api_key):
    """
    ดึงข้อมูลจาก TMD API v1
    https://data.tmd.go.th/nwpapi/
    """
    url = "https://data.tmd.go.th/nwpapi/v1/forecast/location/daily/place"
    
    params = {
        "province": PROVINCE,
        "amphoe": AMPHOE,
        "tambon": TAMBON,
        "fields": "tc_max,tc_min,rh,rr,wd,wd_dir,cond",
        "duration": 7,
    }
    
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {api_key}",
    }
    
    try:
        r = requests.get(url, params=params, headers=headers, timeout=20)
        r.raise_for_status()
        return parse_tmd_response(r.json())
    except Exception as e:
        print(f"[TMD] failed: {e}", file=sys.stderr)
        return None


def parse_tmd_response(data):
    """แปลง TMD JSON → format ของเรา"""
    forecasts = []
    
    # โครงสร้าง TMD: { "WeatherForecasts": [{ "location": ..., "forecasts": [...] }] }
    weather_forecasts = data.get("WeatherForecasts", [])
    if not weather_forecasts:
        return None
    
    raw_forecasts = weather_forecasts[0].get("forecasts", [])
    
    for f in raw_forecasts:
        d = f.get("data", {})
        date = f.get("time", "")
        
        rain_mm = d.get("rr", 0) or 0
        rain_chance = condition_to_rain_chance(d.get("cond", 0))
        
        forecasts.append({
            "date": date,
            "date_label": format_date_label(date),
            "temp_min": round(d.get("tc_min", 25)),
            "temp_max": round(d.get("tc_max", 33)),
            "humidity": round(d.get("rh", 70)),
            "rain_mm": round(rain_mm, 1),
            "rain_chance": rain_chance,
            "wind_kmh": round(d.get("ws", 5)),
            "condition": cond_to_text(d.get("cond", 1)),
        })
    
    return forecasts


def condition_to_rain_chance(cond):
    """
    TMD condition codes → rain chance %
    ตามคู่มือ TMD:
      1=ท้องฟ้าแจ่มใส, 2=มีเมฆบางส่วน, 3=เมฆเป็นส่วนมาก, 4=มีเมฆมาก
      5=ฝนเล็กน้อย, 6=ฝนปานกลาง, 7=ฝนหนัก, 8=ฝนหนักมาก
      9=ฝนฟ้าคะนอง, 10=อากาศหนาวจัด ...
    """
    mapping = {
        1: 0, 2: 10, 3: 25, 4: 40,
        5: 60, 6: 75, 7: 85, 8: 95,
        9: 80, 10: 5
    }
    return mapping.get(cond, 30)


def cond_to_text(cond):
    mapping = {
        1: "ท้องฟ้าแจ่มใส", 2: "มีเมฆบางส่วน",
        3: "เมฆเป็นส่วนมาก", 4: "มีเมฆมาก",
        5: "ฝนเล็กน้อย", 6: "ฝนปานกลาง",
        7: "ฝนหนัก", 8: "ฝนหนักมาก",
        9: "ฝนฟ้าคะนอง", 10: "อากาศหนาว"
    }
    return mapping.get(cond, "ปกติ")


def fetch_from_openmeteo():
    """
    Fallback: Open-Meteo (ฟรี ไม่ต้อง API key)
    https://open-meteo.com/
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,relative_humidity_2m_max,wind_speed_10m_max,weather_code",
        "timezone": "Asia/Bangkok",
        "forecast_days": 7,
    }
    
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        return parse_openmeteo(r.json())
    except Exception as e:
        print(f"[Open-Meteo] failed: {e}", file=sys.stderr)
        return None


def parse_openmeteo(data):
    daily = data.get("daily", {})
    times = daily.get("time", [])
    
    forecasts = []
    for i, date in enumerate(times):
        wcode = daily["weather_code"][i]
        forecasts.append({
            "date": date,
            "date_label": format_date_label(date),
            "temp_min": round(daily["temperature_2m_min"][i]),
            "temp_max": round(daily["temperature_2m_max"][i]),
            "humidity": round(daily["relative_humidity_2m_max"][i]),
            "rain_mm": round(daily["precipitation_sum"][i], 1),
            "rain_chance": daily["precipitation_probability_max"][i] or 0,
            "wind_kmh": round(daily["wind_speed_10m_max"][i]),
            "condition": wmo_code_to_thai(wcode),
        })
    
    return forecasts


def wmo_code_to_thai(code):
    """WMO weather codes → ไทย"""
    if code == 0: return "ท้องฟ้าแจ่มใส"
    if code in [1, 2]: return "มีเมฆบางส่วน"
    if code == 3: return "เมฆเป็นส่วนมาก"
    if code in [45, 48]: return "หมอก"
    if code in [51, 53, 55]: return "ฝนปรอย"
    if code in [61, 63]: return "ฝนเล็กน้อย-ปานกลาง"
    if code == 65: return "ฝนหนัก"
    if code in [80, 81]: return "ฝนชุก"
    if code == 82: return "ฝนหนักมาก"
    if code in [95, 96, 99]: return "ฝนฟ้าคะนอง"
    return "ปกติ"


def format_date_label(date_str):
    """2026-04-25 → 25/04 (ศ.)"""
    try:
        if "T" in date_str:
            d = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        else:
            d = datetime.strptime(date_str, "%Y-%m-%d")
        days_th = ["จ.", "อ.", "พ.", "พฤ.", "ศ.", "ส.", "อา."]
        return f"{d.day}/{d.month} ({days_th[d.weekday()]})"
    except:
        return date_str


def main():
    api_key = os.environ.get("TMD_API_KEY")
    
    forecasts = None
    source = "TMD"
    
    if api_key:
        forecasts = fetch_from_tmd(api_key)
    
    if not forecasts:
        print("[INFO] Falling back to Open-Meteo", file=sys.stderr)
        forecasts = fetch_from_openmeteo()
        source = "Open-Meteo"
    
    if not forecasts:
        print("[ERROR] All weather APIs failed", file=sys.stderr)
        sys.exit(1)
    
    output = {
        "location": f"{TAMBON} {AMPHOE} {PROVINCE}",
        "lat": LATITUDE,
        "lon": LONGITUDE,
        "source": source,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "forecast": forecasts,
    }
    
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Saved {len(forecasts)} days to {OUTPUT_PATH} (source: {source})")
    
    # ก็เขียน markdown ใน vault ด้วย
    write_markdown(output)


def write_markdown(data):
    """สร้าง .md ให้ Obsidian อ่าน"""
    today_str = datetime.now().strftime("%Y-%m-%d")
    md_path = f"obsidian-vault/09-daily-data/{today_str}-weather.md"
    
    lines = [
        "---",
        f"title: ฝน {data['location']} {today_str}",
        "category: weather",
        f"date: {today_str}",
        f"source: {data['source']}",
        "tags: [#ฝน, #พยากรณ์, #พิปูน]",
        "---",
        "",
        f"# 🌧️ พยากรณ์ฝน {data['location']}",
        f"**อัปเดต**: {data['updated_at']}",
        f"**แหล่งที่มา**: {data['source']}",
        "",
        "| วันที่ | สภาพ | ฝน% | ปริมาณ (มม.) | อุณหภูมิ | ความชื้น |",
        "|--------|------|-----|--------------|----------|---------|",
    ]
    
    for f in data["forecast"]:
        lines.append(
            f"| {f['date_label']} | {f['condition']} | {f['rain_chance']}% | "
            f"{f['rain_mm']} | {f['temp_min']}–{f['temp_max']}°C | {f['humidity']}% |"
        )
    
    lines += [
        "",
        "## 📊 ความสัมพันธ์",
        "- [[06-weather/ฝน-รายเดือน]]",
        "- [[01-diseases/]] — โรคที่เสี่ยงในช่วงฝน",
        "- [[07-risk-factors/ปัจจัยเสี่ยง-อากาศ]]",
    ]
    
    os.makedirs(os.path.dirname(md_path), exist_ok=True)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    print(f"[OK] Wrote markdown: {md_path}")


if __name__ == "__main__":
    main()

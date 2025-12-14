from __future__ import annotations

from datetime import date, timedelta, datetime
from typing import Dict, List, Optional, Tuple
import io
import csv

from services.data import Camp

# (camp_id, checkin_date, nights) -> {site_type: available_units}
AVAIL: Dict[Tuple[str, date, int], Dict[str, int]] = {}


def seed_availability(camps: List[Camp], days: int = 45):
    today = date.today()
    for camp in camps:
        for offset in range(days):
            d = today + timedelta(days=offset)
            for nights in [1, 2, 3, 4, 5]:
                base = (hash(camp.camp_id + d.isoformat()) % 6)
                per_type = {}
                for site in camp.sites:
                    weekend_factor = 1 if d.weekday() in [4, 5] else 0
                    qty = max(0, base - weekend_factor)
                    if "木屋" in site.name:
                        qty = max(0, qty - 1)
                    per_type[site.name] = qty
                AVAIL[(camp.camp_id, d, nights)] = per_type


def parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def filter_camps(camps: List[Camp], county: str, district: str) -> List[Camp]:
    out = [c for c in camps if c.county == county]
    if district:
        out = [c for c in out if c.district == district]
    return out


def estimate_price_per_night(camp: Camp, site_type: str) -> int:
    base = 1200
    if camp.altitude_m > 600:
        base += int((camp.altitude_m - 600) * 0.6)

    if "雨棚" in site_type:
        base += 300
    if "棧板" in site_type:
        base += 200
    if "小木屋" in site_type:
        base += 1200

    if "溫泉" in camp.tags:
        base += 200
    if "觀星" in camp.tags:
        base += 150

    return int(max(900, base))


def compute_availability(camp: Camp, checkin: date, nights: int, tents: int) -> List[Dict]:
    key = (camp.camp_id, checkin, nights)
    per_type_units = AVAIL.get(key, {})
    available = []

    for site in camp.sites:
        units = int(per_type_units.get(site.name, 0))
        if units <= 0:
            continue
        capacity_total = units * site.capacity_tents
        if capacity_total >= tents:
            available.append({
                "site_type": site.name,
                "available_units": units,
                "available_tents_capacity": capacity_total,
            })

    return available


def find_next_available_dates(camp: Camp, start: date, nights: int, tents: int, lookahead_days: int = 30, max_dates: int = 3) -> List[str]:
    dates = []
    for offset in range(lookahead_days):
        d = start + timedelta(days=offset)
        if compute_availability(camp, d, nights, tents):
            dates.append(d.isoformat())
            if len(dates) >= max_dates:
                break
    return dates


def build_card_result(camp: Camp, checkin: date, nights: int, tents: int) -> Optional[Dict]:
    available_sites = compute_availability(camp, checkin, nights, tents)
    if not available_sites:
        return None

    enriched = []
    for s in available_sites:
        price_night = estimate_price_per_night(camp, s["site_type"])
        enriched.append({
            **s,
            "price_per_night": price_night,
            "price_total": price_night * nights,
        })

    min_price_night = min(x["price_per_night"] for x in enriched)
    min_price_total = min(x["price_total"] for x in enriched)
    total_units_left = sum(x["available_units"] for x in enriched)
    hints = find_next_available_dates(camp, checkin, nights, tents)

    return {
        "camp_id": camp.camp_id,
        "camp_name": camp.name,
        "county": camp.county,
        "district": camp.district,
        "altitude_m": camp.altitude_m,
        "tags": camp.tags,
        "price_from_per_night": min_price_night,
        "price_from_total": min_price_total,
        "units_left_total": total_units_left,
        "available_date_hints": hints,
        "available_sites": enriched,
    }


def build_csv_bytes(camps: List[Camp], county: str, district: str, checkin: date, nights: int, tents: int):
    filtered = filter_camps(camps, county, district)

    rows = []
    for camp in filtered:
        sites = compute_availability(camp, checkin, nights, tents)
        if not sites:
            continue
        for s in sites:
            price = estimate_price_per_night(camp, s["site_type"])
            rows.append([
                county,
                district or "(不限)",
                checkin.isoformat(),
                nights,
                tents,
                camp.camp_id,
                camp.name,
                camp.altitude_m,
                s["site_type"],
                s["available_units"],
                s["available_tents_capacity"],
                price,
                ",".join(camp.tags),
            ])

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "county", "district", "checkin", "nights", "tents",
        "camp_id", "camp_name", "altitude_m",
        "site_type", "available_units", "tents_capacity_est",
        "price_per_night", "tags"
    ])
    writer.writerows(rows)

    data = io.BytesIO(output.getvalue().encode("utf-8"))
    data.seek(0)
    filename = f"reserve_{county}_{checkin.isoformat()}_{nights}n_{tents}t.csv"
    return data, filename
#!/usr/bin/env python3
"""Load the Ahrens equipment export, validate it, and emit:
  - data/items.json        (tagged tools/site equipment, for the static site)
  - data/heavy_register.json (trucks/trailers/heavy equipment, for Phase 4)
  - labels/tag_list.csv    (wave, equip_no, unit, description, url, Tagged?)

Wave rules and the heavy/trucks/trailers exclusion come from CLAUDE_1.md.
Old CSV has no type/group/tier columns — "Category" stands in for "type"
(it already contains exact values like "Saw", "Grinder", "Chainsaw", etc.),
and tier is derived here from Category.
"""
import csv
import json
import sys
from pathlib import Path

if len(sys.argv) != 3:
    print("usage: build_data.py <input.csv> <base_url>", file=sys.stderr)
    sys.exit(1)

INPUT_CSV = Path(sys.argv[1])
BASE_URL = sys.argv[2].rstrip("/")
OUT_DIR = Path(__file__).resolve().parent.parent

WAVE1_CATEGORIES = {"Saw", "Grinder", "Hand Breaker/Hammer", "Chainsaw", "Laser", "Nibbler", "GPS"}
HEAVY_CATEGORIES = {
    "Backhoe", "Dozer", "Forklift/Lift", "Hilift", "Skid Steer", "Trackhoe", "Tractor",
}
VEHICLE_CATEGORIES = {"Off Road Truck", "Passenger", "Service Truck", "Tandem"}
TRAILER_CATEGORIES = {"Trailer", "Rolloff"}
ATTACHMENT_CATEGORIES = {"Attachment", "Demo Robot Attachment"}
NOT_TAGGED_UNIT_CODES = {"W14", "W15", "W22"}

rows = []
with INPUT_CSV.open(newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append(r)

# --- Validate equip_no uniqueness ---
seen = {}
dupes = []
for r in rows:
    eq = (r.get("Equip #") or "").strip()
    if not eq:
        continue
    if eq in seen:
        dupes.append(eq)
    seen[eq] = seen.get(eq, 0) + 1

if dupes:
    print(f"ERROR: duplicate Equip # values found: {sorted(set(dupes))}", file=sys.stderr)
    sys.exit(1)

print(f"Loaded {len(rows)} rows. Equip # is unique across all rows.")

status_counts = {}
category_counts = {}
for r in rows:
    s = (r.get("Status") or "").strip() or "(blank)"
    status_counts[s] = status_counts.get(s, 0) + 1
    c = (r.get("Category") or "").strip() or "(blank)"
    category_counts[c] = category_counts.get(c, 0) + 1

print("Status breakdown:", status_counts)

dropped_sold = [r for r in rows if (r.get("Status") or "").strip().lower() == "sold"]
kept = [r for r in rows if (r.get("Status") or "").strip().lower() != "sold"]
print(f"Dropped {len(dropped_sold)} Sold units. {len(kept)} remain.")

tagged_items = []
heavy_register = []
skipped_no_category = []

for r in kept:
    eq = (r.get("Equip #") or "").strip()
    unit = (r.get("Unit") or "").strip()
    category = (r.get("Category") or "").strip()
    description = (r.get("Description") or "").strip()
    model_notes = (r.get("Model / Notes") or "").strip()
    status = (r.get("Status") or "").strip() or "Unknown"
    serial = (r.get("Serial / VIN") or "").strip()

    if not eq:
        continue

    if unit in NOT_TAGGED_UNIT_CODES or category in HEAVY_CATEGORIES or category in VEHICLE_CATEGORIES or category in TRAILER_CATEGORIES:
        heavy_register.append({
            "equip_no": eq, "unit": unit, "category": category,
            "description": description, "model_notes": model_notes,
            "status": status, "serial": serial,
        })
        continue

    if category in WAVE1_CATEGORIES:
        wave = 1
    elif category in ATTACHMENT_CATEGORIES:
        wave = 3
    else:
        wave = 2

    tagged_items.append({
        "equip_no": eq, "unit": unit, "category": category,
        "description": description, "model_notes": model_notes,
        "status": status, "serial": serial, "wave": wave,
        "url": f"{BASE_URL}/t/{eq}",
    })

print(f"Tagged tools/site equipment: {len(tagged_items)} (Wave 1: {sum(1 for i in tagged_items if i['wave']==1)}, "
      f"Wave 2: {sum(1 for i in tagged_items if i['wave']==2)}, Wave 3: {sum(1 for i in tagged_items if i['wave']==3)})")
print(f"Heavy equipment / trucks / trailers (Phase 4 register, not tagged): {len(heavy_register)}")

(OUT_DIR / "data").mkdir(exist_ok=True)
(OUT_DIR / "data" / "items.json").write_text(json.dumps(tagged_items, indent=2))
(OUT_DIR / "data" / "heavy_register.json").write_text(json.dumps(heavy_register, indent=2))

(OUT_DIR / "labels").mkdir(exist_ok=True)
with (OUT_DIR / "labels" / "tag_list.csv").open("w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["wave", "equip_no", "unit", "description", "url", "Tagged?"])
    for item in sorted(tagged_items, key=lambda i: (i["wave"], i["equip_no"])):
        w.writerow([item["wave"], item["equip_no"], item["unit"], item["description"], item["url"], ""])

print("Wrote data/items.json, data/heavy_register.json, labels/tag_list.csv")

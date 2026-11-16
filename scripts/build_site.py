#!/usr/bin/env python3
"""Generate the static /t/<equip_no> tool-card pages from data/items.json."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

STATUS_COLORS = {
    "Available": "#0FA1DA",
    "Out of Service": "#c0392b",
}

CARD_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{unit_or_eq} — Ahrens Tool Crib</title>
<style>
  :root {{ --sky:#0FA1DA; --navy:#0F4277; --gold:#F6BE4F; }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; padding: 20px; min-height: 100vh;
    background: var(--navy);
    font-family: -apple-system, system-ui, sans-serif;
    display: flex; align-items: flex-start; justify-content: center;
  }}
  .card {{
    background: #fff; border-radius: 14px; padding: 24px;
    max-width: 480px; width: 100%; margin-top: 24px;
    box-shadow: 0 2px 10px rgba(0,0,0,.25);
  }}
  .eyebrow {{ color: var(--sky); font-weight: 700; font-size: 14px; letter-spacing: .04em; text-transform: uppercase; }}
  h1 {{ font-size: 28px; margin: 4px 0 2px; color: var(--navy); line-height: 1.15; }}
  .unit {{ font-size: 18px; color: #555; margin: 0 0 18px; }}
  .status {{
    display: inline-block; padding: 6px 14px; border-radius: 999px;
    font-weight: 700; font-size: 15px; color: #fff; background: {status_color};
    margin-bottom: 18px;
  }}
  .row {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #eee; font-size: 16px; }}
  .row span:first-child {{ color: #777; }}
  .row span:last-child {{ font-weight: 600; color: var(--navy); text-align: right; }}
  .notice {{
    margin-top: 20px; padding: 14px; border-radius: 10px;
    background: #FEF6E3; border: 1px solid var(--gold); color: #6b5109; font-size: 14px;
  }}
</style>
</head>
<body>
  <div class="card">
    <div class="eyebrow">Ahrens Tool Crib · #{equip_no}</div>
    <h1>{description}</h1>
    <p class="unit">Unit {unit}{category_suffix}</p>
    <span class="status">{status}</span>
    <div class="row"><span>Serial</span><span>{serial}</span></div>
    <div class="row"><span>Notes</span><span>{model_notes}</span></div>
    <div class="notice">Phase 1 test page — tap in/out, who-has-it, and job tracking come in Phase 2. This page just confirms the tag scans to the right tool.</div>
  </div>
</body>
</html>
"""


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    items = json.loads((ROOT / "data" / "items.json").read_text())
    out_dir = ROOT / "docs" / "t"
    out_dir.mkdir(parents=True, exist_ok=True)

    for item in items:
        html = CARD_TEMPLATE.format(
            equip_no=esc(item["equip_no"]),
            unit_or_eq=esc(item["unit"] or item["equip_no"]),
            description=esc(item["description"] or "(no description)"),
            unit=esc(item["unit"] or "—"),
            category_suffix=f" · {esc(item['category'])}" if item["category"] else "",
            status=esc(item["status"]),
            status_color=STATUS_COLORS.get(item["status"], "#777"),
            serial=esc(item["serial"]) or "—",
            model_notes=esc(item["model_notes"]) or "—",
        )
        # Directory + index.html, not <id>.html, so the served path is
        # exactly /t/<equip_no> (matching the URL baked into every tag/QR),
        # not /t/<equip_no>.html.
        item_dir = out_dir / item["equip_no"]
        item_dir.mkdir(parents=True, exist_ok=True)
        (item_dir / "index.html").write_text(html)

    index_html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ahrens Tool Crib</title>
<style>body{{font-family:-apple-system,system-ui,sans-serif;background:#0F4277;color:#fff;
display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;padding:20px;text-align:center}}
.box{{max-width:420px}}h1{{color:#F6BE4F}}</style></head>
<body><div class="box"><h1>Ahrens Tool Crib</h1>
<p>Phase 1 test site — {len(items)} tools/equipment tagged. Scan a tag to open its card at /t/&lt;equip_no&gt;.</p>
</div></body></html>"""
    (ROOT / "docs" / "index.html").write_text(index_html)

    print(f"Generated {len(items)} tool-card pages in docs/t/, plus docs/index.html")


if __name__ == "__main__":
    main()

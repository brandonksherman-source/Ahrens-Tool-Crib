#!/usr/bin/env python3
"""Generate a printable Wave 1 label sheet: unit code + QR of the tag URL.

QR codes render client-side (qrcode.js via CDN) so this stays a plain
static file with no build step or paid service. Layout defaults to a
3x8 grid (~2.6in x 1in cells, close to Avery 5160) — tell me the real
sheet you have on hand and I'll match its exact dimensions.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ahrens Tool Crib — Wave 1 Labels</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
<style>
  :root {{ --navy:#0F4277; --sky:#0FA1DA; }}
  body {{ font-family: -apple-system, system-ui, sans-serif; margin: 20px; color: var(--navy); }}
  .toolbar {{ margin-bottom: 16px; }}
  .toolbar button {{
    background: var(--sky); color: #fff; border: none; padding: 10px 18px;
    border-radius: 8px; font-size: 15px; cursor: pointer;
  }}
  .count {{ color: #666; margin-left: 12px; font-size: 14px; }}
  .sheet {{
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.15in;
    max-width: 8.2in;
  }}
  .label {{
    border: 1px dashed #bbb; border-radius: 4px; padding: 8px;
    display: flex; align-items: center; gap: 8px;
    height: 1in; box-sizing: border-box; page-break-inside: avoid;
  }}
  .label .qr {{ flex: 0 0 auto; }}
  .label .text {{ min-width: 0; }}
  .label .unit {{ font-weight: 800; font-size: 18px; line-height: 1.1; }}
  .label .desc {{ font-size: 11px; color: #555; line-height: 1.2; margin-top: 2px;
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
  .label .eq {{ font-size: 10px; color: #999; }}
  @media print {{
    .toolbar {{ display: none; }}
    body {{ margin: 0.25in; }}
    .label {{ border: none; }}
  }}
</style>
</head>
<body>
  <div class="toolbar">
    <button onclick="window.print()">Print this sheet</button>
    <span class="count"></span>
  </div>
  <div class="sheet" id="sheet"></div>

<script>
  const ITEMS = {items_json};
  const sheet = document.getElementById('sheet');
  document.querySelector('.count').textContent = ITEMS.length + ' Wave 1 labels';

  ITEMS.forEach(item => {{
    const label = document.createElement('div');
    label.className = 'label';

    const qrBox = document.createElement('div');
    qrBox.className = 'qr';
    label.appendChild(qrBox);

    const text = document.createElement('div');
    text.className = 'text';
    text.innerHTML = `
      <div class="unit">${{item.unit || item.equip_no}}</div>
      <div class="desc">${{item.description}}</div>
      <div class="eq">#${{item.equip_no}}</div>
    `;
    label.appendChild(text);

    sheet.appendChild(label);
    new QRCode(qrBox, {{ text: item.url, width: 72, height: 72, correctLevel: QRCode.CorrectLevel.M }});
  }});
</script>
</body>
</html>
"""


def main():
    items = json.loads((ROOT / "data" / "items.json").read_text())
    wave1 = [i for i in items if i["wave"] == 1]
    wave1.sort(key=lambda i: i["unit"] or i["equip_no"])

    out = ROOT / "labels" / "wave1_labels.html"
    out.write_text(PAGE.format(items_json=json.dumps(wave1)))
    print(f"Wrote labels/wave1_labels.html with {len(wave1)} Wave 1 labels")


if __name__ == "__main__":
    main()

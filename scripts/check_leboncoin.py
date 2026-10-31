#!/usr/bin/env python3
"""Conservative Leboncoin listing status monitor. Never remove on search failures."""
import json, pathlib, re, time, urllib.request, urllib.error
P = pathlib.Path("stock.json")
data = json.loads(P.read_text(encoding="utf-8"))
changed = False
for car in data.get("vehicles", []):
    url = car.get("url", "")
    if not re.fullmatch(r"https://www\.leboncoin\.fr/ad/voitures/\d+", url):
        continue
    if not car.get("active", False):
        continue
    statuses = []
    for attempt in range(2):
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; RedcentStockMonitor/1.0)", "Accept": "text/html"})
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                statuses.append(resp.status)
        except urllib.error.HTTPError as exc:
            statuses.append(exc.code)
        except Exception as exc:
            print(f"Uncertain response for {url}: {exc}")
            break
        if attempt == 0:
            time.sleep(4)
    print(url, statuses)
    # Only explicit permanent Gone twice; never treat 403/404/429/5xx or timeout as removal.
    if statuses == [410, 410]:
        car["active"] = False
        car["unpublished_reason"] = "HTTP 410 confirmed twice at individual ad URL"
        changed = True
if changed:
    P.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Updated confirmed unpublished listings")
else:
    print("No confirmed changes; preserving stock")

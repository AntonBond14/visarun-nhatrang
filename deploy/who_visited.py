"""Кто ходил на наш хост. Фильтр по host обязателен: один лог Caddy отдаёт
несколько сайтов, и без фильтра чужие заходы приедут в нашу статистику."""

import json
import subprocess
import sys
from collections import Counter

HOST = sys.argv[1] if len(sys.argv) > 1 else "visarun-nhatrang.duckdns.org"
SINCE = sys.argv[2] if len(sys.argv) > 2 else "24h"

raw = subprocess.run(
    ["docker", "logs", "getmenu-caddy-1", "--since", SINCE],
    capture_output=True, text=True, errors="replace",
).stdout.splitlines()

agents = Counter()
paths = Counter()
statuses = Counter()
total_all_hosts = 0
ours = 0

for line in raw:
    line = line.strip()
    if not line.startswith("{"):
        continue
    try:
        rec = json.loads(line)
    except ValueError:
        continue
    req = rec.get("request") or {}
    if not req:
        continue
    total_all_hosts += 1
    if req.get("host") != HOST:
        continue
    ours += 1
    ua = (req.get("headers") or {}).get("User-Agent") or ["(нет)"]
    agents[ua[0][:120]] += 1
    paths[req.get("uri", "?")] += 1
    statuses[rec.get("status", "?")] += 1

print(f"хост: {HOST}   окно: {SINCE}")
print(f"строк лога всего по всем сайтам: {total_all_hosts}")
print(f"из них наших: {ours}")
print()
print("кто приходил (User-Agent -> запросов):")
for ua, n in agents.most_common(30):
    print(f"  {n:4d}  {ua}")
print()
print("что просили:")
for p, n in paths.most_common(15):
    print(f"  {n:4d}  {p}")
print()
print("коды ответа:", dict(statuses))

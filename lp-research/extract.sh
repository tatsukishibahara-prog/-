#!/usr/bin/env bash
# LPのタイトル・description・見出し(h1-h3)・ボタン/リンク文言を抜き出す
# usage: ./extract.sh <url> [<url>...]
set -euo pipefail

UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"

for url in "$@"; do
  echo "=== $url"
  html=$(curl -sSL -A "$UA" --max-time 30 "$url")
  python3 - "$html" <<'PY'
import re, sys, html as h
src = sys.argv[1]
def clean(s): return re.sub(r'\s+', ' ', h.unescape(re.sub(r'<[^>]+>', '', s))).strip()
t = re.search(r'<title[^>]*>(.*?)</title>', src, re.S | re.I)
d = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)', src, re.I)
print("title:", clean(t.group(1)) if t else "-")
print("description:", clean(d.group(1)) if d else "-")
print("-- headings")
for tag, body in re.findall(r'<(h[1-3])[^>]*>(.*?)</\1>', src, re.S | re.I):
    text = clean(body)
    if text: print(f"  {tag.lower()}: {text}")
print("-- CTA候補")
seen = set()
for body in re.findall(r'<(?:button|a)[^>]*(?:btn|button|cta)[^>]*>(.*?)</(?:button|a)>', src, re.S | re.I):
    text = clean(body)
    if text and len(text) < 40 and text not in seen:
        seen.add(text); print("  -", text)
PY
done

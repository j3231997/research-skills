"""Extract recent daily closing prices from a Google Finance quote page.

Usage:
    python3 gf_closes.py DAL:NYSE            # fetch and print daily closes
    python3 gf_closes.py DAL:NYSE 2026-10-09 # also show change vs prior close

Google Finance embeds chart data in the page as arrays like
[[2026,10,9,16,null,...],[82.17,...]]; the hour-16 entries are daily closes.
"""
import re
import sys
import urllib.request

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"


def fetch(symbol):
    url = f"https://www.google.com/finance/quote/{symbol}?hl=en"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def daily_closes(page):
    pattern = r"\[\[(\d{4}),(\d+),(\d+),16,null,[^\]]*\]\],\[([\d.]+),"
    closes = {}
    for m in re.finditer(pattern, page):
        y, mo, d, price = m.groups()
        closes.setdefault(f"{y}-{int(mo):02d}-{int(d):02d}", float(price))
    return dict(sorted(closes.items()))


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    closes = daily_closes(fetch(sys.argv[1]))
    if not closes:
        sys.exit("No daily closes found; page format may have changed.")
    for date, price in closes.items():
        print(date, price)
    if len(sys.argv) > 2:
        dates = list(closes)
        target = sys.argv[2]
        if target not in closes or dates.index(target) == 0:
            sys.exit(f"{target}: not found or no prior close in range.")
        prev = dates[dates.index(target) - 1]
        chg = closes[target] / closes[prev] - 1
        print(f"\n{prev} close {closes[prev]} -> {target} close {closes[target]}: {chg:+.2%}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Append one row per friend to points.csv:
timestamp (UTC ISO8601) , handle , score
"""

import asyncio, csv, datetime, sys, aiohttp
from bs4 import BeautifulSoup

FRIENDS = [
    "aron-cullberg",
    "s4andersson",
    "rasmus-melin",
    "viktor6",
    "jonalt",
    "jonathan-vestin",
    "martin-blom",
]

HEADERS = {"User-Agent": "kattis-data/1.0 (+https://github.com/aroncullberg)"}


def score_from_html(html: str) -> float:
    """Return the float score from a Kattis profile page (no login)."""
    soup = BeautifulSoup(html, "html.parser")
    label = soup.find("span", class_="info_label", string="Score")
    if not label:
        raise RuntimeError("Score label not found; markup changed?")
    return float(label.find_next("span", class_="important_text").text)


async def fetch(session, handle):
    url = f"https://open.kattis.com/users/{handle}"
    async with session.get(url, headers=HEADERS, timeout=30) as r:
        r.raise_for_status()
        return handle, score_from_html(await r.text())


async def main():
    async with aiohttp.ClientSession() as session:
        rows = await asyncio.gather(*[fetch(session, h) for h in FRIENDS])

    ts = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    with open("points.csv", "a", newline="") as f:
        w = csv.writer(f)
        for handle, score in rows:
            w.writerow([ts, handle, score])


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)

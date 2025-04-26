# Note, for some reason the API fails to get the first wordle of (CIGAR), so I manually added it when needed

import requests
from datetime import date, timedelta
import time
import sys

API_URL = "https://www.nytimes.com/svc/wordle/v2/{:%Y-%m-%d}.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; WordleFetcher/1.0)",
    "Accept": "application/json",
    "Referer": "https://www.nytimes.com/games/wordle/index.html",
}

def fetch_full_list(output_path, year=None):
    session = requests.Session()
    session.headers.update(HEADERS)
    entries = []

    # Determin start date, initialize variables, if needed manually add June 2021 headers
    if year is None:
        entries = ["== Current list of Wordles =="]
        # manual June 19 + header
        entries += [
            "=== June 2021 ===",
            "* Day 0, Jun 19 2021: CIGAR"
        ]
        current = date(2021, 6, 20)
        last_month = 6
    else:
        if year < 2021:
            print(f"⚠ No Wordles available before 2021!")
            return
        if year == 2021:
            # include Day 0 but drop the year from the header/line
            entries += [
                "=== June ===",
                "* Day 0, Jun 19: CIGAR"
            ]
            current = date(2021, 6, 20)
            last_month = 6
        else:
            # Start at Jan 1 of your year
            current = date(year, 1, 1)
            last_month = None

    one_day = timedelta(days=1)

    # ——— Main fetch loop ———
    while True:
        # If filtering for certain year, stop once we get to next year
        if year is not None and current.year > year:
            break

        url = API_URL.format(current)
        print(f"→ Fetching {current.isoformat()} ...", end=" ", flush=True)
        resp = session.get(url)

        if resp.status_code == 404:
            print("404 (no more puzzles) ✋")
            break
        if resp.status_code != 200:
            print(f"{resp.status_code} (retrying) ⏱️")
            time.sleep(1)
            current += one_day
            continue

        data = resp.json()
        day_num  = data.get("days_since_launch")
        sol = data.get("solution")
        if day_num is None or sol is None:
            print("malformed JSON → skipping")
            current += one_day
            continue

        # Month header
        if last_month is None or current.month != last_month:
            if year is None:
                hdr = f"=== {current.strftime('%B')} {current.year} ==="
                last_year = current.year
            else:
                hdr = f"=== {current.strftime('%B')} ==="
            entries.append(hdr)
            last_month = current.month

        # Entry line
        if year is None:
            date_str = current.strftime("%b ") + str(current.day) + current.strftime(" %Y")
        else:
            date_str = current.strftime("%b ") + str(current.day)
        entries.append(f"* Day {day_num}, {date_str}: {sol.upper()}")

        print(f"OK ({sol.upper()})")
        current += one_day

    # Write to file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(entries))
    print(f"\n✅ Wrote {len(entries)} entries to {output_path}")

if __name__ == "__main__":
    output_path="wordles.txt"
    choice = input("Print all Wordles? (Y/N): ").strip().upper()
    if choice == 'Y':
        fetch_full_list(output_path)
    elif choice == 'N':
        year = input("Enter the year (e.g. 2023): ").strip()
        try:
            year = int(year)
        except ValueError:
            print("❌ Invalid year; please enter a number.")
            sys.exit(1)
        fetch_full_list(output_path, year)
    else:
        print("❌ Invalid choice; please enter Y or N.")

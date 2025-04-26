import requests
from datetime import date, timedelta
import time

API_URL = "https://www.nytimes.com/svc/wordle/v2/{:%Y-%m-%d}.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; WordleFetcher/1.0)",
    "Accept": "application/json",
    "Referer": "https://www.nytimes.com/games/wordle/index.html",
}

def fetch_full_list(output_path="all_wordles.txt"):
    session = requests.Session()
    session.headers.update(HEADERS)

    start_date = date(2021, 6, 20)  # Day 1, skip Day 0
    one_day    = timedelta(days=1)
    current    = start_date
    entries    = []

    # Explicitly write Day 0 and first headings
    entries.append("== Current list of Wordles ==")
    entries.append("=== June 2021 ===")
    entries.append("* Day 0, Jun 19 2021: CIGAR")

    # Track when the month/year changes
    last_month, last_year = 6, 2021

    while True:
        url = API_URL.format(current)
        print(f"→ Fetching {current.isoformat()} ...", end=" ", flush=True)
        resp = session.get(url)

        if resp.status_code == 404:
            print("404 (no more puzzles)  ✋")
            break
        if resp.status_code != 200:
            print(f"{resp.status_code} (retrying) ⏱")
            time.sleep(1)
            current += one_day
            continue

        data = resp.json()
        day_num  = data.get("days_since_launch")
        solution = data.get("solution")
        if day_num is None or solution is None:
            print("malformed JSON → skipping")
            current += one_day
            continue

        # Insert a month header if this date is a new month
        if current.month != last_month or current.year != last_year:
            header = f"=== {current.strftime('%B')} {current.year} ==="
            entries.append(header)
            last_month, last_year = current.month, current.year

        # Format the daily entry
        formatted_date = current.strftime("%b ") + str(current.day) + current.strftime(" %Y")
        entries.append(f"* Day {day_num}, {formatted_date}: {solution.upper()}")
        print(f"OK ({solution.upper()})")

        current += one_day

    # Write to file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(entries))

    print(f"\n✔ Wrote {len(entries)} entries (with month headers) to {output_path}")

if __name__ == "__main__":
    fetch_full_list()

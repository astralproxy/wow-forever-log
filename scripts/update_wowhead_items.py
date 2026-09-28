import argparse
import csv
import io
import re
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen

SPREADSHEET_ID = "1PWAetMYOglFXz7ISOKisYgRGpZ4Pnfa1D4WL1Hv7D94"
CAMPING_CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"
    "/gviz/tq?tqx=out:csv&sheet=Camping"
)
WOWHEAD_URL = "https://www.wowhead.com/forever"
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "wowhead-items.csv"
USER_AGENT = "wow-forever-log item lookup updater"


def fetch_text(url):
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8-sig")


def normalize_item_name(name):
    name = re.sub(r"\s*\(\d+\)", " ", name)
    return " ".join(name.split())


def get_reagent_names(csv_text):
    reader = csv.reader(io.StringIO(csv_text))
    headers = next(reader, None)
    if not headers:
        raise ValueError("Camping CSV is empty")

    reagent_column = next(
        (index for index, header in enumerate(headers) if header.strip().casefold() == "reagents"),
        5 if len(headers) > 5 else None,
    )
    if reagent_column is None:
        raise ValueError("Could not find the Reagents column in the Camping CSV")

    names_by_key = {}
    for row in reader:
        if reagent_column >= len(row):
            continue
        for raw_name in re.split(r"\r?\n", row[reagent_column]):
            item_name = normalize_item_name(raw_name.strip())
            if item_name:
                names_by_key.setdefault(item_name.casefold(), item_name)

    return list(names_by_key.values())


def lookup_item(item_name):
    lookup_url = f"{WOWHEAD_URL}/item={quote(item_name, safe='')}?xml"
    root = ET.fromstring(fetch_text(lookup_url))
    item = root.find(".//item")
    if item is None:
        raise ValueError("Wowhead XML did not contain an item element")

    item_id = item.get("id", "")
    resolved_name = (item.findtext("name") or "").strip()
    canonical_url = (item.findtext("link") or "").strip()
    base = urlsplit(WOWHEAD_URL)
    canonical = urlsplit(canonical_url)
    expected_path = f"{base.path}/item={item_id}/"
    if not item_id.isdigit() or not resolved_name:
        raise ValueError("Wowhead XML did not contain a valid item ID and name")
    if canonical.netloc != base.netloc or not canonical.path.startswith(expected_path):
        raise ValueError("Wowhead XML returned an unexpected canonical item URL")

    return {"id": item_id, "name": resolved_name, "url": canonical_url}


def write_lookup_table(items, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=("id", "name", "url"))
        writer.writeheader()
        writer.writerows(items)


def main():
    parser = argparse.ArgumentParser(
        description="Build the local Wowhead item lookup CSV from Camping reagents."
    )
    parser.add_argument("--camping-csv-url", default=CAMPING_CSV_URL)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--delay", type=float, default=0.2, help="Seconds between Wowhead requests")
    args = parser.parse_args()

    if args.delay < 0:
        parser.error("--delay must not be negative")

    try:
        reagent_names = get_reagent_names(fetch_text(args.camping_csv_url))
    except Exception as error:
        print(f"Could not load Camping reagents: {error}", file=sys.stderr)
        return 1

    items = []
    failures = []
    for index, item_name in enumerate(reagent_names):
        try:
            item = lookup_item(item_name)
            items.append(item)
            print(f"Resolved {item_name}: {item['id']}")
        except Exception as error:
            failures.append(item_name)
            print(f"Could not resolve {item_name}: {error}", file=sys.stderr)
        if index + 1 < len(reagent_names) and args.delay:
            time.sleep(args.delay)

    try:
        write_lookup_table(items, args.output)
    except OSError as error:
        print(f"Could not write lookup CSV: {error}", file=sys.stderr)
        return 1

    print(f"Wrote {len(items)} items to {args.output}")
    if failures:
        print(f"Unresolved reagents ({len(failures)}): {', '.join(failures)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

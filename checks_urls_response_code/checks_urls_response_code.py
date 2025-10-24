#!/usr/bin/env python3
"""
check_urls_response_code.py
---------------------------

Purpose:
    Concurrently check HTTP response codes for a list of URLs from a CSV file
    and write the results (including response codes) to a timestamped CSV file.

Input CSV Format (headers required):
    URL,Langs,Status

Output CSV Format:
    URL,Langs,ResponseCode,Status

Default behavior:
    - Reads input CSV passed via -i flag
    - Checks each URL concurrently (fast, non-blocking)
    - Writes timestamped CSV results to the same directory as this script
    - If -o flag is given, writes results to that directory instead
    - Prints color + emoji output for quick scanning in the console

Examples:
    python check_urls_response_code.py -i urls.csv
    python check_urls_response_code.py -i urls.csv -o ./results/

Dependencies:
    pip install requests colorama
"""

import requests
import csv
import argparse
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import init, Fore, Style

# Initialize colorama (cross-platform terminal colors, incl. Windows)
init(autoreset=True)

# --- Configurable constants ---
MAX_WORKERS = 50  # Number of concurrent threads (tune for your network/host)
TIMEOUT = 10      # Per-request timeout (seconds)


def fetch_status(url: str):
    """
    Fetch the HTTP response code for a single URL.

    Strategy:
      1) Try HEAD (faster, no body).
      2) If status >= 400 or HEAD blocked, retry with GET.
    Returns:
      - int HTTP status code on success
      - "ERROR" on exception (timeout, DNS failure, etc.)
    """
    try:
        r = requests.head(url, allow_redirects=True, timeout=TIMEOUT)
        if r.status_code >= 400:
            r = requests.get(url, allow_redirects=True, timeout=TIMEOUT)
        return r.status_code
    except requests.RequestException:
        return "ERROR"


def color_for_status(code) -> str:
    """
    Map status code to a colored string for console readability.
    """
    if isinstance(code, int):
        if 200 <= code < 300:
            return Fore.GREEN + str(code) + Style.RESET_ALL  # Success (green)
        elif 300 <= code < 400:
            return Fore.YELLOW + str(code) + Style.RESET_ALL  # Redirect (yellow)
        elif 400 <= code < 600:
            return Fore.RED + str(code) + Style.RESET_ALL  # Client/Server error (red)
    return Fore.LIGHTBLACK_EX + "ERROR" + Style.RESET_ALL  # Unknown/failed (gray)


def emoji_for_status(code) -> str:
    """
    Map status code to an emoji for ultra-fast visual scanning.
      🟩 200–299   🟨 300–399   🟥 400–599   ⚫ ERROR/unknown
    """
    if isinstance(code, int):
        if 200 <= code < 300:
            return "🟩"
        if 300 <= code < 400:
            return "🟨"
        if 400 <= code < 600:
            return "🟥"
    return "⚫"


def check_urls(input_file: str, output_dir: str):
    """
    Main flow:
      - Read input CSV (robust header handling)
      - Concurrently fetch status codes
      - Write results CSV with timestamped filename
    """
    # Determine output directory (default: this script’s folder)
    script_dir = Path(__file__).resolve().parent
    output_path = Path(output_dir).expanduser().resolve() if output_dir else script_dir
    output_path.mkdir(parents=True, exist_ok=True)

    # Build timestamped output filename from input base name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = Path(input_file).stem
    output_file = output_path / f"{base_name}_results_{timestamp}.csv"

    # Read CSV with BOM-safe encoding and normalized headers
    with open(input_file, mode="r", newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)

        # Normalize header names (trim + lowercase) to handle Excel quirks
        def norm(s: str): return (s or "").strip().lower()
        header_map = {norm(h): h for h in (reader.fieldnames or [])}

        # Safe getter that tolerates header variations
        def getcol(row, key_norm: str, default=""):
            orig = header_map.get(key_norm)
            return (row.get(orig, default).strip() if orig else default)

        rows = []
        for row in reader:
            url = getcol(row, "url")
            if not url:
                continue  # skip rows missing URL
            langs = getcol(row, "langs")
            status = getcol(row, "status")
            rows.append({"URL": url, "Langs": langs, "Status": status})

    print(f"🔍 Checking {len(rows)} URLs using up to {MAX_WORKERS} threads...\n")

    results = []

    # Fire off all URL checks concurrently
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_map = {executor.submit(fetch_status, r["URL"]): r for r in rows}

        # As each completes, print a color+emoji line and collect the result
        for fut in as_completed(future_map):
            row = future_map[fut]
            try:
                code = fut.result()
            except Exception:
                code = "ERROR"

            print(f"{emoji_for_status(code)} {row['URL']} -> {color_for_status(code)}")

            results.append({
                "URL": row["URL"],
                "Langs": row["Langs"],
                "ResponseCode": code,
                "Status": row["Status"],
            })

    # Write output CSV once at the end (fast + atomic)
    with open(output_file, mode="w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=["URL", "Langs", "ResponseCode", "Status"])
        writer.writeheader()
        writer.writerows(results)

    print(f"\n✅ Results written to: {Fore.CYAN}{output_file}{Style.RESET_ALL}")


if __name__ == "__main__":
    # CLI: -i for input CSV, -o for optional output directory
    parser = argparse.ArgumentParser(
        description="Check HTTP response codes for a list of URLs in parallel (color + emoji output)."
    )
    parser.add_argument(
        "-i", "--input", required=True,
        help="Path to input CSV file with headers: URL,Langs,Status"
    )
    parser.add_argument(
        "-o", "--output", default="",
        help="Directory to save output CSV (default: script's directory)"
    )
    args = parser.parse_args()

    check_urls(args.input, args.output)

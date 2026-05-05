import csv
import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv


API_URL: str = "https://app.scrapingbee.com/api/v1/google"
SEARCH_QUERY: str = "pizza new-york"
DATA_FILE: Path = Path(__file__).with_name("data.csv")


def get_api_key() -> str:
    load_dotenv()
    api_key = os.getenv("SCRAPINGBEE_API_KEY")

    if not api_key:
        raise ValueError("SCRAPINGBEE_API_KEY not found in .env file")

    return api_key
    
    
def fetch_google_results(api_key: str, query: str) -> dict[str, Any]:
    response = requests.get(
        url=API_URL,
        params={
            "api_key": api_key,
            "search": query,
        },
        timeout=10,
    )
    response.raise_for_status()

    return response.json()
    

def read_position_history(csv_path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with csv_path.open(newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        if not reader.fieldnames:
            raise ValueError("CSV file must contain a header row with domains")

        return reader.fieldnames, list(reader)
        

def normalize_domain(domain: str) -> str:
    return domain.removeprefix("www.")
    
    
def find_domain_positions(
    data: dict[str, Any],
    domains: list[str],
) -> dict[str, int]:
    domain_positions = {domain: 0 for domain in domains}
    monitored_domains = set(domains)

    for result in data.get("organic_results", []):
        raw_domain = result.get("domain")
        position = result.get("position")

        if not raw_domain or not isinstance(position, int):
            continue

        current_domain = normalize_domain(raw_domain)

        if current_domain in monitored_domains and domain_positions[current_domain] == 0:
            domain_positions[current_domain] = position

    return domain_positions
    

def format_position(position: int | str | None) -> str:
    if position in (None, "", 0, "0"):
        return "not found"

    return str(position)


def get_position_change(previous: str | None, current: int) -> str:
    if current == 0 and previous in (None, "", "0"):
        return "still not found"

    if not previous or previous == "0":
        return "newly found"

    if current == 0:
        return "dropped out of current results"

    previous_position = int(previous)

    if current < previous_position:
        return f"up by {previous_position - current} position(s)"

    if current > previous_position:
        return f"down by {current - previous_position} position(s)"

    return "same position"


def print_domain_report(
    domains: list[str],
    current_positions: dict[str, int],
    history: list[dict[str, str]],
) -> None:
    print("\n=====")
    print("Domain position report")

    latest_history_row = history[-1] if history else {}

    for domain in domains:
        current_position = current_positions[domain]
        previous_position = latest_history_row.get(domain)

        historical_positions = [
            row.get(domain, "N/A")
            for row in history
        ]

        print("\n---")
        print(f"Domain: {domain}")
        print(f"Previous position: {format_position(previous_position)}")
        print(f"Current position: {format_position(current_position)}")
        print(f"Change: {get_position_change(previous_position, current_position)}")

        if historical_positions:
            print(f"History: {', '.join(historical_positions)}")
        else:
            print("History: no historical records yet")
            
            
def ensure_file_ends_with_newline(csv_path: Path) -> None:
    if not csv_path.exists() or csv_path.stat().st_size == 0:
        return

    with csv_path.open("rb+") as file:
        file.seek(-1, os.SEEK_END)
        last_character = file.read(1)

        if last_character != b"\n":
            file.write(b"\n")


def append_domain_positions(
    csv_path: Path,
    domains: list[str],
    positions: dict[str, int],
) -> None:
    ensure_file_ends_with_newline(csv_path)

    with csv_path.open("a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=domains,
            lineterminator="\n",
        )
        writer.writerow(positions)
        

def main() -> None:
    api_key = get_api_key()

    domains, history = read_position_history(DATA_FILE)
    data = fetch_google_results(api_key, SEARCH_QUERY)

    current_positions = find_domain_positions(data, domains)

    print_domain_report(domains, current_positions, history)
    append_domain_positions(DATA_FILE, domains, current_positions)


if __name__ == "__main__":
    main()
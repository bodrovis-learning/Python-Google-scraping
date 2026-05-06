import os
from typing import Any

import requests
from dotenv import load_dotenv


API_URL: str = "https://app.scrapingbee.com/api/v1/google"
SEARCH_QUERY: str = "pizza new-york"


def get_api_key() -> str:
    load_dotenv()
    api_key = os.getenv("SCRAPINGBEE_API_KEY")

    if not api_key:
        raise ValueError("SCRAPINGBEE_API_KEY not found in .env file")

    return api_key
    

def fetch_google_maps_results(api_key: str, query: str) -> dict[str, Any]:
    response = requests.get(
        url=API_URL,
        params={
            "api_key": api_key,
            "search": query,
            "search_type": "maps",
        },
        timeout=10,
    )
    response.raise_for_status()

    return response.json()
    

def format_value(value: Any) -> str:
    if value in (None, "", []):
        return "N/A"

    if isinstance(value, list):
        return ", ".join(str(item) for item in value)

    return str(value)
    

def print_map_results(data: dict[str, Any]) -> None:
    print("\nHere are the map results:")

    map_results = data.get("map_results") or data.get("maps_results") or []

    if not map_results:
        print("No map results found.")
        return

    for result in map_results:
        position = format_value(result.get("position"))
        title = format_value(result.get("title"))
        address = format_value(result.get("address"))
        opening_hours = format_value(result.get("opening_hours"))
        link = format_value(result.get("link"))
        price = format_value(result.get("price"))
        rating = format_value(result.get("rating"))
        reviews = format_value(result.get("reviews"))

        print(f"\n{position}. {title}")
        print(f"Address: {address}")
        print(f"Opening hours: {opening_hours}")
        print(f"Link: {link}")
        print(f"Price: {price}")
        print(f"Rating: {rating}, based on {reviews} reviews")
        

def main() -> None:
    api_key = get_api_key()
    data = fetch_google_maps_results(api_key, SEARCH_QUERY)

    print_map_results(data)


if __name__ == "__main__":
    main()
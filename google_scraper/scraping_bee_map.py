import requests
import json

response = requests.get(
    url="https://app.scrapingbee.com/api/v1/store/google",
    params={
        "api_key": "",
        "search": "pizza new-york",
        "search_type": "maps",
    },
)

data = json.loads(response.content)

print("\nHere are the map results:")

for result in data["maps_results"]:
    print(f"{result['position']}. {result['title']}")
    print(f"Address: {result['address']}")
    print(f"Opening hours: {result['opening_hours']}")
    print(f"Link: {result['link']}")
    print(f"Price: {result['price']}")
    print(f"Rating: {result['rating']}, based on {result['reviews']} reviews")
    print("\n\n")

import requests
import json

response = requests.get(
    url="https://app.scrapingbee.com/api/v1/store/google",
    params={
        "api_key": "",
        "search": "pizza new-york",
        # "nb_results": "20",
    },
)

# print('Response HTTP Status Code: ', response.status_code)
# print("Response HTTP Response Body: ", response.content)

data = json.loads(response.content)

print("=== Organic search results ===")

for result in data["organic_results"]:
    print(f"{result['position']}. {result['title']}")
    print(result["url"])
    print(result["description"])
    print("\n\n")

print("\n\n=== Local search results ===")

for result in data["local_results"]:
    print(f"{result['position']}. {result['title']}")
    print(f"Rating: {result['review']}, based on {result['review_count']} reviews")
    print("\n\n")

print("\n\n=== Top ads ===")

for result in data["top_ads"]:
    print(f"{result['position']}. {result['title']}")
    print(result["url"])
    print(result["description"])
    print("\n\n")

print("\n\n=== Related queries ===")

for result in data["related_queries"]:
    print(f"{result['position']}. {result['title']}")
    print("\n")

print("\n\n=== Relevant questions ===")

for result in data["questions"]:
    print(f"Question:\n{result['text']}")
    print(f"\n{result['answer']}")
    print("\n\n")

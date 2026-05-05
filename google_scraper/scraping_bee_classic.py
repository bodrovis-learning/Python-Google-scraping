import os
from typing import Any

import requests
from dotenv import load_dotenv


API_URL: str = "https://app.scrapingbee.com/api/v1/google"


def fetch_google_results(api_key: str, query: str) -> requests.Response:
    response = requests.get(
        url=API_URL,
        params={
            "api_key": api_key,
            "search": query,
        },
        timeout=10,
    )
    response.raise_for_status()
    return response


def get_api_key() -> str:
    load_dotenv()
    api_key = os.getenv("SCRAPINGBEE_API_KEY")

    if not api_key:
        raise ValueError("SCRAPINGBEE_API_KEY not found in .env file")

    return api_key


def print_organic_results(data: dict[str, Any]) -> None:
    print("\n=== Organic search results ===")

    for result in data.get("organic_results", []):
        position = result.get("position", "N/A")
        title = result.get("title", "No title")
        url = result.get("url", "No URL")
        description = result.get("description", "No description")

        print(f"\n{position}. {title}")
        print(url)
        print(description)


def print_local_results(data: dict[str, Any]) -> None:
    print("\n\n=== Local search results ===")

    for result in data.get("local_results", []):
        position = result.get("position", "N/A")
        title = result.get("title", "No title")
        review = result.get("review")
        review_count = result.get("review_count")

        print(f"\n{position}. {title}")

        if review is not None and review_count is not None:
            print(f"Rating: {review} (based on {review_count} reviews)")
        elif review is not None:
            print(f"Rating: {review}")
        else:
            print("Rating: N/A")


def print_related_queries(data: dict[str, Any]) -> None:
    print("\n\n=== Related queries ===")

    queries = data.get("related_queries", [])

    if not queries:
        print("No related queries found.")
        return

    for result in queries:
        position = result.get("position")
        title = result.get("title")

        if position is not None:
            print(f"\n{position}. {title}")
        else:
            print(f"\n- {title}")


def print_questions(data: dict[str, Any]) -> None:
    print("\n\n=== Relevant questions ===")

    for result in data.get("questions", []):
        position = result.get("position", "N/A")
        question = result.get("text", "No question")
        answer = result.get("answer")

        print(f"\n{position}. {question}")

        if answer:
            print(f"Answer: {answer}")
        else:
            print("Answer: Not shown in the response")


if __name__ == "__main__":
    api_key = get_api_key()
    query = "pizza new-york"

    response = fetch_google_results(api_key, query)
    data = response.json()

    print("Response HTTP Status Code:", response.status_code)

    print_organic_results(data)
    print_local_results(data)
    print_related_queries(data)
    print_questions(data)
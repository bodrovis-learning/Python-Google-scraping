import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlparse

from bs4 import BeautifulSoup
from bs4.element import Tag
from dotenv import load_dotenv
from requests import Response
from scrapingbee import ScrapingBeeClient


TARGET_URL: str = "https://www.google.com/search?q=web+scraping&hl=en&gl=us"
HTML_FILE: Path = Path("google_search_rendered.html")
ERROR_FILE: Path = Path("scrapingbee_error.html")
SCREENSHOT_FILE: Path = Path("google_search_screenshot.png")


@dataclass(frozen=True)
class SearchResult:
    position: int
    title: str
    link: str


def get_api_key() -> str:
    load_dotenv()
    api_key = os.getenv("SCRAPINGBEE_API_KEY")

    if not api_key:
        raise ValueError("SCRAPINGBEE_API_KEY not found in .env file")

    return api_key


def create_client(api_key: str) -> ScrapingBeeClient:
    return ScrapingBeeClient(api_key=api_key)


def save_response_debug(response: Response, output_path: Path) -> None:
    output_path.write_bytes(response.content)

    print("\nScrapingBee request failed.")
    print(f"Status code: {response.status_code}")
    print(f"Saved response body to {output_path}")
    print("Open that file to see what ScrapingBee/Google returned.")


def fetch_rendered_google_html(
    client: ScrapingBeeClient,
    url: str,
) -> str:
    response = client.get(
        url,
        params={
            "custom_google": "true",
            "render_js": "true",
            "wait_browser": "load",
            "block_resources": "false",
            "premium_proxy": "true",
        },
        retries=3,
    )

    if not response.ok:
        save_response_debug(response, ERROR_FILE)
        response.raise_for_status()

    return response.text


def save_html(html: str, output_path: Path) -> None:
    output_path.write_text(html, encoding="utf-8")
    print(f"Saved rendered HTML to {output_path}")


def save_full_page_screenshot(
    client: ScrapingBeeClient,
    url: str,
    output_path: Path,
) -> None:
    response = client.get(
        url,
        params={
            "custom_google": "true",
            "render_js": "true",
            "wait_browser": "networkidle2",
            "screenshot": "true",
            "screenshot_full_page": "true",
            "block_resources": "false",
            "premium_proxy": "true",
        },
        retries=3,
    )

    if not response.ok:
        save_response_debug(response, ERROR_FILE)
        response.raise_for_status()

    output_path.write_bytes(response.content)
    print(f"Saved screenshot to {output_path}")


def clean_google_link(raw_link: str) -> str:
    if raw_link.startswith("/url?"):
        parsed_url = urlparse(raw_link)
        query_params = parse_qs(parsed_url.query)

        if "q" in query_params:
            return query_params["q"][0]

    return urljoin("https://www.google.com", raw_link)


def is_google_internal_link(link: str) -> bool:
    parsed_url = urlparse(link)

    if not parsed_url.netloc:
        return True

    return "google." in parsed_url.netloc


def parse_search_results(html: str) -> list[SearchResult]:
    soup = BeautifulSoup(html, "html.parser")
    results: list[SearchResult] = []
    seen_links: set[str] = set()

    for link_tag in soup.find_all("a", href=True):
        if not isinstance(link_tag, Tag):
            continue

        heading = link_tag.find("h3")

        if not isinstance(heading, Tag):
            continue

        raw_link = link_tag.get("href")

        if not isinstance(raw_link, str):
            continue

        title = heading.get_text(strip=True)
        link = clean_google_link(raw_link)

        if not title or not link.startswith("http"):
            continue

        if is_google_internal_link(link):
            continue

        if link in seen_links:
            continue

        seen_links.add(link)

        results.append(
            SearchResult(
                position=len(results) + 1,
                title=title,
                link=link,
            )
        )

    return results


def print_search_results(results: list[SearchResult]) -> None:
    if not results:
        print("No search results found in the rendered HTML.")
        return

    print("\nSearch results:")

    for result in results:
        print(f"\n{result.position}. {result.title}")
        print(result.link)


def main() -> None:
    api_key = get_api_key()
    client = create_client(api_key)

    html = fetch_rendered_google_html(client, TARGET_URL)
    save_html(html, HTML_FILE)

    results = parse_search_results(html)
    print_search_results(results)

    save_full_page_screenshot(client, TARGET_URL, SCREENSHOT_FILE)


if __name__ == "__main__":
    main()
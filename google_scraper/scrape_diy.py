from dataclasses import dataclass
from urllib.parse import parse_qs, urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

GOOGLE_SEARCH_URL: str = "https://www.google.com/search"
SEARCH_QUERY: str = "web scraping"

CONSENT_COOKIE: str = "YES+cb.20220419-08-p0.cs+FX+111"

USER_AGENT: str = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) "
    "Gecko/20100101 Firefox/118.0"
)


@dataclass(frozen=True)
class SearchResult:
    position: int
    title: str
    link: str
    

def fetch_google_html(query: str) -> str:
    response = requests.get(
        GOOGLE_SEARCH_URL,
        params={
            "q": query,
            "hl": "en",
            "gl": "us",
        },
        headers={
            "User-Agent": USER_AGENT,
        },
        cookies={
            "CONSENT": CONSENT_COOKIE,
        },
        timeout=10,
    )

    response.raise_for_status()
    return response.text
    

def create_soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")
    

def find_result_headings(soup: BeautifulSoup) -> list[Tag]:
    headings = soup.select("#search h3")

    return [
        heading
        for heading in headings
        if isinstance(heading, Tag)
    ]
    

def clean_google_link(raw_link: str) -> str:
    if raw_link.startswith("/url?"):
        parsed_url = urlparse(raw_link)
        query_params = parse_qs(parsed_url.query)

        if "q" in query_params:
            return query_params["q"][0]

    return urljoin("https://www.google.com", raw_link)
    
    
def parse_search_results(soup: BeautifulSoup) -> list[SearchResult]:
    results: list[SearchResult] = []
    seen_links: set[str] = set()

    for heading in find_result_headings(soup):
        link_tag = heading.find_parent("a", href=True)

        if not isinstance(link_tag, Tag):
            continue

        raw_link = link_tag.get("href")

        if not isinstance(raw_link, str):
            continue

        title = heading.get_text(strip=True)
        link = clean_google_link(raw_link)

        if not title or not link.startswith("http"):
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
        print("No search results found.")
        return

    print("\nSearch results:")

    for result in results:
        print(f"\n{result.position}. {result.title}")
        print(result.link)
        
        
def main() -> None:
    html = fetch_google_html(SEARCH_QUERY)
    soup = create_soup(html)
    results = parse_search_results(soup)

    print_search_results(results)


if __name__ == "__main__":
    main()
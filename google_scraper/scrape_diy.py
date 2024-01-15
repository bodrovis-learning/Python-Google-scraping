import requests
from bs4 import BeautifulSoup
from scrapingbee import ScrapingBeeClient

text = "web scraping"
url = "https://google.com/search?q=" + text

cookies = {"CONSENT": "YES+cb.20220419-08-p0.cs+FX+111"}

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0"
}

response = requests.get(url, headers=headers, cookies=cookies)

soup = BeautifulSoup(response.content, "html.parser")

heading_object = soup.select("#search h3")

for i, result in enumerate(heading_object):
    if "href" in result.parent.attrs:
        print(i + 1)
        print(result.string)
        print(result.parent.attrs["href"])
        print("------")


# OR

# client = ScrapingBeeClient(
#     api_key=""
# )

# response = client.get(
#     "https://www.google.com/search?q=Best+Laptops+in+Europe&tbm=shop",
#     params={
#         "custom_google": "true",
#         # 'premium_proxy': 'true',
#         # 'country_code':'lv',
#         "block_resources": "false",
#         "wait": "1500",  # Waiting for the content to load (1.5 seconds)
#         "screenshot": True,
#         # Specify that we need the full height
#         "screenshot_full_page": True,
#         "forward_headers": True,
#     },
#     cookies=cookies,
#     headers=headers,
# )

# soup = BeautifulSoup(response.content, "html.parser")
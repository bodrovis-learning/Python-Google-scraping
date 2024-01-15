import requests
import json
import os
import csv

response = requests.get(
    url="https://app.scrapingbee.com/api/v1/store/google",
    params={
        "api_key": "",
        "search": "pizza new-york",
    },
)

data = json.loads(response.content)

domains = ["tripadvisor.com", "bbc.com", "foodnetwork.com"]

domain_positions = dict([(domain, 0) for domain in domains])

for result in data["organic_results"]:
    current_domain = result["domain"].replace("www.", "")

    if current_domain in domains and domain_positions[current_domain] == 0:
        domain_positions[current_domain] = result["position"]


root = os.path.dirname(os.path.abspath(__file__))

print("\n=====")
print(f"Let's compare positions for the requested domains!")

with open(os.path.join(root, "data.csv"), newline="") as csvfile:
    reader = csv.DictReader(csvfile)

    for domain in domains:
        csvfile.seek(0)

        print("\n---")
        if domain_positions[domain] == 0:
            print(f"Unfortunately I was not able to find {domain} in the results...")
        else:
            print(f"{domain} has position {domain_positions[domain]}")

        print("Here are the historical records for this domain:")

        for row in reader:
            print(row[domain])


with open(os.path.join(root, "data.csv"), "a", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=domains)
    writer.writerow(domain_positions)

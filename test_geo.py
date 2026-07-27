import requests
import json

url = "https://d2396ha8oiavw0.cloudfront.net/sul-main/immoSearch"

payload = {
    "offset": 0,
    "cat": "parken"
}

headers = {
    "Content-Type": "application/json",
    "Origin": "https://stadtundland.de",
    "Referer": "https://stadtundland.de/"
}

response = requests.post(
    url,
    json=payload,
    headers=headers,
    timeout=30
)

print(json.dumps(response.json(), indent=2, ensure_ascii=False))
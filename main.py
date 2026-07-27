import json
import os
import requests

from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from geo import is_near

API_URL = "https://d2396ha8oiavw0.cloudfront.net/sul-main/immoSearch"

HEADERS = {
    "Content-Type": "application/json",
    "Origin": "https://stadtundland.de",
    "Referer": "https://stadtundland.de/",
}

KNOWN_FILE = "known_offers.json"


def load_known():
    if os.path.exists(KNOWN_FILE):
        with open(KNOWN_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_known(ids):
    with open(KNOWN_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(list(ids)), f, indent=2)


def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    response = requests.post(
        url,
        json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
        },
        timeout=30,
    )

    if response.status_code != 200:
        print("Telegram-Fehler:")
        print(response.text)


def get_offers():
    all_offers = []
    offset = 0

    while True:
        response = requests.post(
            API_URL,
            json={
                "offset": offset,
                "cat": "parken",
            },
            headers=HEADERS,
            timeout=30,
        )

        response.raise_for_status()

        result = response.json()

        offers = result["data"]

        if not offers:
            break

        print(f"Offset {offset}: {len(offers)} Angebote geladen")

        all_offers.extend(offers)

        if len(all_offers) >= result["count"]:
            break

        offset += len(offers)

    return all_offers


def build_address(offer):
    address = offer["address"]

    return (
        f'{address["street"]} '
        f'{address["house_number"]}, '
        f'{address["postal_code"]} '
        f'{address["city"]}'
    )


known = load_known()

offers = get_offers()

print(f"Insgesamt {len(offers)} Angebote gefunden.")

for offer in offers:

    immo_number = offer["details"]["immoNumber"]

    if immo_number in known:
        continue

    adresse = build_address(offer)

    if not is_near(adresse):
        print(f"⏭ Übersprungen (zu weit): {adresse}")
        continue

    headline = offer["headline"]
    preis = offer["costs"]["coldRent"]

    text = (
        "🅿️ Neuer STADT-UND-LAND Stellplatz\n\n"
        f"{headline}\n\n"
        f"📍 {adresse}\n"
        f"💶 {preis} €/Monat\n"
        f"🆔 {immo_number}"
    )

    print(text)

    send_telegram(text)

    known.add(immo_number)

save_known(known)

print("✅ Fertig.")
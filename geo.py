import json
import os

from geopy.distance import geodesic
from geopy.geocoders import Nominatim

CACHE_FILE = "coordinates.json"

geolocator = Nominatim(user_agent="stadtundland_bot")


def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)


cache = load_cache()


def get_coordinates(address):
    if address in cache:
        return tuple(cache[address])

    location = geolocator.geocode(address)

    if location is None:
        return None

    coords = (location.latitude, location.longitude)

    cache[address] = coords
    save_cache(cache)

    return coords


TARGET = get_coordinates(
    "Johanna-Tesch-Straße, Berlin"
)


def is_near(address, km=2):
    coords = get_coordinates(address)

    if coords is None or TARGET is None:
        return False

    distance = geodesic(TARGET, coords).km

    return distance <= km
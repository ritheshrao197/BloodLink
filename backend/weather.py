"""Is it raining at a district right now? Used only for the Rainmaker achievement.

Uses Open-Meteo (free, no API key). Only the district name is sent, never anything about the user. Any failure
returns None ("unknown") so a slow or unreachable weather service can never break a donation.
Disable with WEATHER_CHECK=0.
"""

import logging
import os

import requests

log = logging.getLogger("bloodlink.weather")
ENABLED = os.getenv("WEATHER_CHECK", "1") == "1"
TIMEOUT = 2.0
RAIN_CODES = set(range(51, 68)) | set(range(80, 83)) | set(range(95, 100))  # drizzle, rain, showers, thunderstorm

# Districts whose name is not the name of their main town
TOWN = {
    "Bengaluru Urban": "Bengaluru", "Kodagu": "Madikeri", "Chikkamagaluru": "Chikmagalur", "Bengaluru Rural": "Doddaballapura", "Dakshina Kannada": "Mangaluru",
    "Uttara Kannada": "Karwar", "Mumbai City": "Mumbai", "Mumbai Suburban": "Mumbai", "Ernakulam": "Kochi",
    "North Goa": "Panaji", "South Goa": "Margao", "Nilgiris": "Ooty", "Kanniyakumari": "Nagercoil",
    "Central Delhi": "New Delhi", "East Delhi": "New Delhi", "North Delhi": "New Delhi",
    "North East Delhi": "New Delhi", "North West Delhi": "New Delhi", "Shahdara": "New Delhi",
    "South Delhi": "New Delhi", "South East Delhi": "New Delhi", "South West Delhi": "New Delhi",
    "West Delhi": "New Delhi", "Chhatrapati Sambhajinagar": "Aurangabad", "Ahilyanagar": "Ahmednagar",
    "Dharashiv": "Osmanabad",
}
_coords: dict[str, tuple[float, float] | None] = {}


def _locate(district: str) -> tuple[float, float] | None:
    if district not in _coords:
        name = TOWN.get(district, district)
        r = requests.get("https://geocoding-api.open-meteo.com/v1/search",
                         params={"name": name, "count": 1, "countryCode": "IN"}, timeout=TIMEOUT)
        hits = r.json().get("results") or []
        _coords[district] = (hits[0]["latitude"], hits[0]["longitude"]) if hits else None
    return _coords[district]


def current(district: str | None) -> str | None:
    """'rain', 'dry', or None when unknown."""
    if not ENABLED or not district:
        return None
    try:
        where = _locate(district)
        if not where:
            return None
        r = requests.get("https://api.open-meteo.com/v1/forecast",
                         params={"latitude": where[0], "longitude": where[1], "current": "precipitation,weather_code"},
                         timeout=TIMEOUT)
        cur = r.json().get("current") or {}
        rainy = (cur.get("precipitation") or 0) > 0 or cur.get("weather_code") in RAIN_CODES
        return "rain" if rainy else "dry"
    except (requests.RequestException, ValueError, KeyError) as exc:
        log.info("weather lookup for %s failed: %s", district, exc)
        return None

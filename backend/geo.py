"""Distances and approximate coordinates.

Privacy: donor locations are opt-in and rounded to 2 decimals (~1 km) before storage. They are never returned to other
users; requesters only see a rounded distance.
"""

import math

# Approximate district centres (main town) for the districts the demo uses; others fall back to Open-Meteo geocoding.
DISTRICT_CENTRES = {
    "Bengaluru Urban": (12.97, 77.59), "Dakshina Kannada": (12.87, 74.88), "Mysuru": (12.30, 76.64), "Udupi": (13.34, 74.75),
    "Belagavi": (15.85, 74.50), "Dharwad": (15.46, 75.01), "Kalaburagi": (17.33, 76.83), "Shivamogga": (13.93, 75.57),
    "Bengaluru Rural": (13.29, 77.54), "Hassan": (13.00, 76.10), "Tumakuru": (13.34, 77.10), "Kodagu": (12.42, 75.74),
    "Mumbai City": (18.94, 72.83), "Mumbai Suburban": (19.12, 72.85), "Pune": (18.52, 73.86), "Nagpur": (21.15, 79.09),
    "Thane": (19.22, 72.98), "Chennai": (13.08, 80.27), "Coimbatore": (11.02, 76.96), "Madurai": (9.93, 78.12),
    "Vellore": (12.92, 79.13), "Ernakulam": (9.98, 76.28), "Thiruvananthapuram": (8.52, 76.94), "Kozhikode": (11.26, 75.78),
    "Thrissur": (10.53, 76.21), "Kasaragod": (12.50, 74.99), "New Delhi": (28.61, 77.21), "South Delhi": (28.53, 77.22),
    "Central Delhi": (28.65, 77.23), "South East Delhi": (28.56, 77.27), "North Goa": (15.49, 73.83), "South Goa": (15.27, 73.96),
}

RINGS_KM = (5, 15, 40)  # alert circles; after the last circle, the rest of the district/state
MIN_FIRST_WAVE = 8  # the first wave widens until it reaches at least this many donors (or circles run out)
ESCALATE_MINUTES = {"Critical": 5, "High": 10, "Normal": 20}


def round_coord(value: float) -> float:
    return round(float(value), 2)


def valid(lat, lng) -> bool:
    return lat is not None and lng is not None and -90 <= lat <= 90 and -180 <= lng <= 180


def km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Great-circle distance (haversine)."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 6371.0 * 2 * math.asin(math.sqrt(a))


def district_centre(district: str | None) -> tuple[float, float] | None:
    if not district:
        return None
    if district in DISTRICT_CENTRES:
        return DISTRICT_CENTRES[district]
    try:
        import weather  # reuses its cached Open-Meteo geocoder

        return weather._locate(district) if weather.ENABLED else None
    except Exception:  # noqa: BLE001
        return None


FEED_SCOPES = ("25", "50", "state", "all")  # how far the live feed reaches from the viewer's home point


def home_point(user) -> dict | None:
    """Where 'nearby' is measured from: the location the person shared (rounded), else their district's centre."""
    if valid(user.lat, user.lng):
        return {"lat": user.lat, "lng": user.lng, "source": "gps"}
    centre = district_centre(user.city)
    return {"lat": centre[0], "lng": centre[1], "source": "district"} if centre else None


def ring_for(distance_km: float | None, same_district: bool, same_state: bool) -> int | None:
    """Which alert circle a donor belongs to (0 = nearest). None = too far to alert at all."""
    if distance_km is not None:
        for i, limit in enumerate(RINGS_KM):
            if distance_km <= limit:
                return i
        return len(RINGS_KM) if (same_state and distance_km <= 150) else None
    # donor without a location: place them by district/state
    if same_district:
        return 1
    if same_state:
        return len(RINGS_KM)
    return None


def shown_km(distance_km: float | None) -> float | None:
    """Distance as shown to people: never more precise than half a kilometre."""
    if distance_km is None:
        return None
    return max(0.5, round(distance_km * 2) / 2)

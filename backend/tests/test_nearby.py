"""Nearby feed and donor search. Mysuru (12.30, 76.64) is ~120 km from Bengaluru and ~160 km from Udupi."""
from factory import login, make_request, make_user

MYSURU = {"lat": 12.30, "lng": 76.64}


def _req(db, hospital, city, state="Karnataka", lat=None, lng=None, **kw):
    return make_request(db, hospital=hospital, city=city, state=state, lat=lat, lng=lng, **kw)


def _feed(client, **params):
    return client.get("/api/requests", params={"status": "Active", **params}).json()


def _setup(db):
    _req(db, "Near", "Mysuru", lat=12.32, lng=76.65)            # ~2.5 km
    _req(db, "Edge", "Mysuru", lat=12.48, lng=76.70)            # ~21 km
    _req(db, "Mid", "Mandya", lat=12.52, lng=76.90)             # ~37 km
    _req(db, "Far", "Bengaluru Urban", lat=12.97, lng=77.59)    # ~128 km
    _req(db, "Kerala", "Ernakulam", state="Kerala", lat=9.98, lng=76.28)
    _req(db, "NoPoint", "Mysuru")                                # same district, no coordinates


def test_feed_within_25_km_is_nearest_first_with_distance(client, db):
    _setup(db)
    rows = _feed(client, **MYSURU, scope="25", state="Karnataka", district="Mysuru")
    assert [r["hospital"] for r in rows] == ["Near", "Edge", "NoPoint"]
    assert rows[0]["distance_km"] == 2.5 and rows[-1]["distance_km"] is None


def test_feed_scopes_widen(client, db):
    _setup(db)
    base = {**MYSURU, "state": "Karnataka", "district": "Mysuru"}
    assert [r["hospital"] for r in _feed(client, **base, scope="50")] == ["Near", "Edge", "Mid", "NoPoint"]
    assert {r["hospital"] for r in _feed(client, **base, scope="state")} == {"Near", "Edge", "Mid", "Far", "NoPoint"}
    everything = _feed(client, **base, scope="all")
    assert len(everything) == 6 and everything[0]["hospital"] == "Near"


def test_feed_without_a_point_keeps_the_old_listing(client, db):
    _setup(db)
    rows = _feed(client)
    assert len(rows) == 6 and all(r["distance_km"] is None for r in rows)


def test_bad_scope_is_rejected(client, db):
    assert client.get("/api/requests", params={**MYSURU, "scope": "7"}).status_code == 422


def test_district_point_lookup(client):
    res = client.get("/api/geo/point", params={"state": "Karnataka", "district": "Mysuru"})
    assert res.status_code == 200 and res.json() == {"lat": 12.30, "lng": 76.64}
    assert client.get("/api/geo/point", params={"district": "Atlantis"}).status_code == 404


def test_home_point_prefers_shared_location_then_district(client, db):
    gps = make_user(db, name="With GPS", lat=12.31, lng=76.62)
    plain = make_user(db, name="District only")
    me1 = client.get(f"/api/users/{gps.id}", headers=login(db, gps)).json()["home_point"]
    me2 = client.get(f"/api/users/{plain.id}", headers=login(db, plain)).json()["home_point"]
    assert me1 == {"lat": 12.31, "lng": 76.62, "source": "gps"}
    assert me2 == {"lat": 12.30, "lng": 76.64, "source": "district"}


def test_new_sos_gets_its_district_centre(client, db):
    res = client.post("/api/sos", json={"requester_name": "R", "blood_group": "O+", "hospital": "JSS Hospital",
                                        "city": "Mysuru", "state": "Karnataka", "units_needed": 1, "urgency": "High"})
    r = res.json()["request"]
    assert (r["lat"], r["lng"]) == (12.30, 76.64)


def test_donor_search_is_nearest_first_with_rounded_distance(client, db):
    make_user(db, name="Udupi donor", city="Udupi")                          # district centre, far
    make_user(db, name="Close donor", lat=12.33, lng=76.66)                  # ~4 km
    make_user(db, name="Town donor")                                         # Mysuru centre, 0 km
    rows = client.get("/api/donors", params={**MYSURU, "blood_group": "O+"}).json()
    assert [d["name"] for d in rows] == ["Town donor", "Close donor", "Udupi donor"]
    assert rows[1]["distance_km"] == 4.0
    assert "lat" not in rows[1] and "lng" not in rows[1]  # never the exact point

"""Blood bank stock: banks keep their sheet, the public sees fresh nearby stock, SOS shows it, stale banks are reminded."""
from datetime import timedelta

from factory import login, make_user
from models import BloodStock, utcnow

FULL = {"A+": 0, "A-": 0, "B+": 4, "B-": 1, "AB+": 0, "AB-": 0, "O+": 2, "O-": 3}


def _bank(db, name="Mysuru Blood Bank", city="Mysuru", **kw):
    return make_user(db, name=name, role="blood_bank", city=city, phone="+91 821 000 0000", **kw)


def _save(client, db, bank, units=FULL):
    return client.put("/api/stock/mine", headers=login(db, bank), json={"units": units})


def _age(db, bank, hours):
    for s in db.query(BloodStock).filter_by(bank_id=bank.id):
        s.updated_at = utcnow() - timedelta(hours=hours)
    db.commit()


# ---------------------------------------------------------------- the bank's own sheet
def test_bank_saves_and_reads_its_stock(client, db):
    bank = _bank(db)
    assert _save(client, db, bank, {"B+": 4, "O-": 3}).status_code == 200
    mine = client.get("/api/stock/mine", headers=login(db, bank)).json()
    assert mine["units"]["B+"] == 4 and mine["units"]["O-"] == 3 and mine["units"]["A+"] == 0
    assert len(mine["units"]) == 8 and mine["updated_at"]
    assert _save(client, db, bank, {"B+": 1}).status_code == 200  # a save replaces the whole sheet
    mine = client.get("/api/stock/mine", headers=login(db, bank)).json()
    assert mine["units"]["B+"] == 1 and mine["units"]["O-"] == 0


def test_only_verified_blood_banks_can_edit(client, db):
    assert client.put("/api/stock/mine", json={"units": FULL}).status_code == 401
    for u in (make_user(db, name="Donor"), make_user(db, name="JSS Hospital", role="hospital"),
              _bank(db, name="New Bank", is_verified=False)):
        assert _save(client, db, u).status_code == 403


def test_bad_numbers_and_groups_are_rejected(client, db):
    bank = _bank(db)
    assert _save(client, db, bank, {"B+": -1}).status_code == 422
    assert _save(client, db, bank, {"B+": 100000}).status_code == 422
    assert _save(client, db, bank, {"Z+": 1}).status_code == 422


# ---------------------------------------------------------------- public search
def test_public_search_shows_exact_and_compatible_units_nearest_first(client, db):
    near = _bank(db, name="Near Bank", lat=12.31, lng=76.65)
    far = _bank(db, name="Far Bank", lat=12.60, lng=76.65)  # ~33 km away, still within 50 km
    _save(client, db, near)
    _save(client, db, far, {"O-": 2})
    rows = client.get("/api/stock", params={"blood_group": "B+", "lat": 12.30, "lng": 76.64}).json()
    assert [r["bank"]["name"] for r in rows] == ["Near Bank", "Far Bank"]
    assert rows[0]["units"] == 4  # B+ itself
    assert rows[0]["compatible"] == {"B-": 1, "O+": 2, "O-": 3}  # other groups a B+ patient can receive
    assert rows[1]["units"] == 0 and rows[1]["compatible"] == {"O-": 2}
    assert rows[0]["distance_km"] is not None and rows[0]["bank"]["phone"] and rows[0]["updated_at"]


def test_search_leaves_out_stale_unverified_empty_and_far_banks(client, db):
    stale = _bank(db, name="Stale Bank")
    _save(client, db, stale)
    _age(db, stale, 49)
    unverified = _bank(db, name="Unverified Bank")
    _save(client, db, unverified)
    unverified.is_verified = False
    db.commit()
    _save(client, db, _bank(db, name="Empty Bank"), {"A+": 5})  # nothing a B+ patient can receive
    _save(client, db, _bank(db, name="Chennai Bank", city="Chennai", state="Tamil Nadu"))
    _save(client, db, _bank(db, name="Good Bank"))
    rows = client.get("/api/stock", params={"blood_group": "B+", "district": "Mysuru", "state": "Karnataka"}).json()
    assert [r["bank"]["name"] for r in rows] == ["Good Bank"]


def test_search_needs_a_group_and_a_place(client, db):
    assert client.get("/api/stock", params={"district": "Mysuru"}).status_code == 422
    assert client.get("/api/stock", params={"blood_group": "B+"}).status_code == 422


# ---------------------------------------------------------------- SOS
def test_sos_lists_nearby_stock_and_still_alerts_donors(client, db):
    _save(client, db, _bank(db))
    make_user(db, blood_group="O+")  # a compatible donor in Mysuru
    res = client.post("/api/sos", json={"requester_name": "R", "blood_group": "O+", "hospital": "JSS Hospital",
                                        "city": "Mysuru", "state": "Karnataka", "units_needed": 1, "urgency": "High"}).json()
    assert [s["bank"]["name"] for s in res["stock"]] == ["Mysuru Blood Bank"]
    assert res["stock"][0]["units"] == 2 and res["stock"][0]["compatible"] == {"O-": 3}
    assert res["matched_donors"] == 1  # donors are alerted exactly as before


# ---------------------------------------------------------------- freshness reminders
def test_stale_banks_are_reminded_once_a_day(client, db, monkeypatch):
    import notifier
    import reminders

    told = []
    monkeypatch.setattr(notifier, "tell", lambda user, key, url="/", buttons=None, **kw: told.append((user.name, key, url)))
    fresh, stale, gone = _bank(db, name="Fresh"), _bank(db, name="Stale"), _bank(db, name="Gone")
    _bank(db, name="Never")  # never entered stock: not nagged
    for b, hours in ((fresh, 2), (stale, 30), (gone, 8 * 24)):
        _save(client, db, b)
        _age(db, b, hours)
    assert reminders.run_stock()["stock"] == 1
    assert told == [("Stale", "stock_stale", "/staff")]
    assert reminders.run_stock()["stock"] == 0  # not again today

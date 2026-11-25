from datetime import date

from factory import SCREENING, login, make_request, make_user, pledge
from models import User

BASICS = {"sex": "female", "date_of_birth": "1996-04-12", "weight_kg": 58}


def register(client, **kw):
    body = {"name": "Kavya", "blood_group": "O+", "city": "Mysuru", "state": "Karnataka", **BASICS, "conditions": [], **kw}
    return client.post("/api/register", json=body)


def test_donor_registration_requires_basics_and_conditions(client):
    for missing in ("sex", "date_of_birth", "weight_kg", "conditions"):
        body = {k: v for k, v in {**BASICS, "conditions": []}.items() if k != missing}
        res = client.post("/api/register", json={"name": "K", "blood_group": "O+", "city": "Mysuru", **body})
        assert res.status_code == 422, missing


def test_hospital_registration_skips_screening(client):
    res = client.post("/api/register", json={"name": "JSS Hospital", "blood_group": "O+", "city": "Mysuru", "role": "hospital"})
    assert res.status_code == 200, res.text


def test_unknown_condition_is_rejected(client):
    assert register(client, conditions=["flu"]).status_code == 422


def test_clean_screening_registers_eligible_donor(client, db):
    res = register(client)
    assert res.status_code == 200, res.text
    user = res.json()["user"]
    assert user["eligibility"]["eligible"] is True and user["permanently_ineligible"] is False
    u = db.get(User, user["id"])
    assert u.screened_at is not None and u.is_available is True
    assert u.date_of_birth == date(1996, 4, 12) and u.weight_kg == 58


def test_permanent_condition_registers_but_flags_without_storing_it(client, db):
    res = register(client, conditions=["thalassaemia", "hiv"])
    assert res.status_code == 200, res.text
    user = res.json()["user"]
    assert user["permanently_ineligible"] is True and user["is_available"] is False
    assert [r["code"] for r in user["eligibility"]["reasons"]] == ["permanent"]
    assert "thalass" not in res.text.lower()  # the condition itself is never echoed back
    u = db.get(User, user["id"])
    assert u.permanently_ineligible is True
    for col in User.__table__.columns:  # nothing on the row names the condition
        assert "thalass" not in str(getattr(u, col.name)).lower()


def test_flagged_donor_cannot_pledge_and_is_never_alerted(client, db):
    import eligibility
    from models import utcnow

    donor = make_user(db, permanently_ineligible=True)
    res = pledge(client, login(db, donor), make_request(db).id, donor.id)
    assert res.status_code == 409
    assert [r["code"] for r in res.json()["detail"]["eligibility"]["reasons"]] == ["permanent"]
    assert eligibility.can_be_alerted(donor, utcnow()) is False


def test_unscreened_donor_is_still_alerted_but_must_answer_before_pledging(client, db):
    import eligibility
    from models import utcnow

    donor = make_user(db, screened_at=None)
    assert eligibility.can_be_alerted(donor, utcnow()) is True
    h = login(db, donor)
    req = make_request(db)
    res = pledge(client, h, req.id, donor.id)
    assert res.status_code == 409
    assert "screening" in [r["code"] for r in res.json()["detail"]["eligibility"]["reasons"]]
    ok = client.post(f"/api/donate/{req.id}", headers=h,
                     json={"user_id": donor.id, "confirmed": True, "screening": {**SCREENING, "conditions": []}})
    assert ok.status_code == 200, ok.text
    db.expire_all()
    assert db.get(User, donor.id).screened_at is not None


def test_condition_reported_at_pledge_time_flags_donor(client, db):
    donor = make_user(db, screened_at=None)
    req = make_request(db)
    res = client.post(f"/api/donate/{req.id}", headers=login(db, donor),
                      json={"user_id": donor.id, "confirmed": True, "screening": {**SCREENING, "conditions": ["heart"]}})
    assert res.status_code == 409
    db.expire_all()
    assert db.get(User, donor.id).permanently_ineligible is True


def test_rescreening_from_profile_can_clear_a_mistake(client, db):
    donor = make_user(db, permanently_ineligible=True, is_available=False)
    h = login(db, donor)
    res = client.post(f"/api/users/{donor.id}/screening", headers=h, json={"conditions": []})
    assert res.status_code == 200, res.text
    assert res.json()["permanently_ineligible"] is False
    res = client.post(f"/api/users/{donor.id}/screening", headers=h, json={"conditions": ["cancer"]})
    assert res.json()["permanently_ineligible"] is True and res.json()["is_available"] is False
    other = make_user(db, name="Someone else")
    assert client.post(f"/api/users/{donor.id}/screening", headers=login(db, other), json={"conditions": []}).status_code == 403


def test_questions_endpoint_lists_permanent_conditions(client):
    body = client.get("/api/eligibility/questions").json()
    codes = [c["code"] for c in body["permanent"]]
    assert {"thalassaemia", "sickle_cell", "bleeding", "hiv", "hepatitis"} <= set(codes)
    assert body["min_hb_g_dl"] == 12.5


def test_flagged_donors_are_hidden_from_donor_search(client, db):
    make_user(db, name="Can Donate")
    make_user(db, name="Cannot Donate", permanently_ineligible=True)
    names = [d["name"] for d in client.get("/api/donors").json()]
    assert "Can Donate" in names and "Cannot Donate" not in names


def test_seeded_donors_are_screened(db):
    import seed_data

    seed_data.seed(db)
    assert db.query(User).filter(User.role == "donor", User.screened_at.is_(None)).count() == 0

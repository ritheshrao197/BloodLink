# Donation verification: design

Date: 2026-11-25 · Feedback item #3 (with part of #5)

## Goal

Points and the next eligible donation date must follow a **real, staff-confirmed donation**, not a donor's tap on
"I Can Donate". Today `POST /api/donate/{id}` awards points, sets `last_donation_at`, counts a unit and may mark the
request Fulfilled in one step, so a donor who never reaches the hospital still gets rewarded.

## Decisions (agreed)

1. Hospital or blood bank **staff confirm** each donation (no donor-entered codes).
2. A new **`blood_bank`** role is added now.
3. A blood bank covers **its district** (`User.city`): it may confirm pledges for any request in that district.
4. A pledge does **not** count toward units. Unconfirmed pledges **expire after 24 h** as a no-show; **3 no-shows**
   block pledging for **30 days**.

## States

```
pledged ──staff "Donated"──▶ confirmed   (points + last_donation_at set here)
   ├────staff "Didn't come"──▶ no_show
   └────24 h unconfirmed────▶ expired     (counts as a no-show)
```

`confirmed`, `no_show` and `expired` are final.

## Data model

`donations`:
- `status` (`pledged | confirmed | no_show | expired`; default `pledged`)
- `confirmed_at`, `confirmed_by` (staff user id)
- `hb_g_dl` (float, optional haemoglobin reading)
- `points_awarded` stays 0 until confirmation.

`users`:
- `role`: `donor | hospital | blood_bank`. A blood bank's coverage is its `city` (district).
- `no_show_count` (int, default 0), `pledge_blocked_until` (datetime, nullable)

`requests`: `units_fulfilled` counts confirmed donations only. `units_pledged` (open pledges) is computed in
`request_out`, not stored.

Migration: `migrate()` adds the columns. Existing donation rows are set to `confirmed` so history and points don't
change.

## Who may confirm

- an admin
- the `hospital` account whose name matches `request.hospital` (same rule as `_require_admin_or_hospital`)
- any `blood_bank` account whose `city` equals `request.city`
- the bot with its trusted token, acting for a staff member identified by Telegram id who passes the rules above

Staff may never confirm their own donation.

## API

| Endpoint | Behaviour |
|---|---|
| `POST /api/donate/{id}` (unchanged URL) | Existing checks (Active request, compatible group, health check, one response per request), plus: donor not blocked, no other open pledge, donation interval passed. Creates a `pledged` Donation. No points, no `last_donation_at`, no units. Notifies the requester ("donor on the way") and the covering staff on Telegram. Returns `status: "pledged"` and `expected_points` with its breakdown. |
| `GET /api/staff/pledges` | Open pledges for requests the caller covers (admins see all): donation id, donor name, group, phone, hospital, city, pledged time. |
| `POST /api/staff/pledges/{donation_id}/confirm` (body: optional `hb_g_dl`) | Awards points (base 100, quick bonus if the pledge was within 5 min of the request, streak bonus), sets `last_donation_at` to now, increases `total_donations` and `units_fulfilled`, marks the request Fulfilled when covered, pays the first-donation referral reward, runs achievement evaluation, and notifies the donor ("+X BLP, next eligible on <date>"). |
| `POST /api/staff/pledges/{donation_id}/no-show` | Sets `no_show` and increments `no_show_count`. On the 3rd, sets `pledge_blocked_until = now + 30 days`. Notifies the donor. |

Errors: 403 if the caller doesn't cover the request, 409 if the donation isn't `pledged`, 404 if the donation doesn't exist.

Expiry: the existing hourly background loop marks pledges older than 24 h as `expired` (counted as a no-show,
same penalty) and notifies the donor.

## Web app

- Donate modal: a "Pledged ✓" result with the hospital and "about +X BLP once staff confirm". No points-awarded wording.
- Request card: "N of M units confirmed · K on the way".
- Profile: "My pledges" with each status. The next eligible date reflects confirmed donations only.
- New `/staff` page (hospital, blood_bank, admin): a polled queue with **Donated ✓** (optional Hb input) and
  **Didn't come ✗**. A nav link for those roles only.
- Admin: the `blood_bank` role is shown and can be assigned; pledged/confirmed/no-show counts.
- New strings in `en.js`. Other locales fall back to English.

## Telegram bot

- Donor pledge reply: "Pledged, please go to <hospital>; points after staff confirm". The points breakdown is removed.
- Staff get a pledge message with **✓ Donated** and **✗ Didn't come** buttons, which call the staff API via the bot token.
- Donor messages for confirmed, no-show and expired, with keys in en/kn/hi.

## Demo data

- Seeded donations are `confirmed`.
- About 6 `blood_bank` accounts (one per state's main district) and a few open pledges.
- Bump `SEED_VERSION`.

## Testing

`backend/tests/test_verification.py` (pytest, in-memory SQLite, FastAPI TestClient):
- a pledge gives no points and leaves `last_donation_at` unchanged
- confirming awards points, sets `last_donation_at` and counts the unit
- a pledge inside the 90/120-day interval is refused, and so is a second open pledge
- a no-show increments the count, and the 3rd blocks pledging
- expiry after 24 h counts as a no-show
- permissions: a wrong-district blood bank or another hospital gets 403
- a donation can't be confirmed twice (409)

Plus a manual end-to-end check in the web app.

## Out of scope

Achievements stay. They are evaluated at confirmation, so pledges alone never unlock them.

Haemoglobin notifications (#6, the reading is only stored here), the blood bank ↔ hospital
messaging beyond these notifications (#5), and translating the new strings into languages other than en/kn/hi.

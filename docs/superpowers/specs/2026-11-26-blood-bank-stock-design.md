# Blood bank stock — design (approved 2026-11-26)

**Why:** families should see at once which nearby blood banks hold the group they need. Donor alerts are unchanged, so a
stale number can never delay help.

## Decisions (user)
- SOS: show nearby stock **and** still alert donors exactly as today.
- Detail: units per blood group (8 numbers), no components.
- Visibility: public, no sign-in.
- Freshness: show "updated X ago", hide stock older than 48 h, remind the bank after 24 h.

## Design
- **Who edits:** verified `blood_bank` accounts only (admins too). Hospitals with an in-house bank get the blood bank role. *(my call)*
- **Data:** `blood_stock` (bank_id, blood_group, units, updated_at), unique per bank+group. A save replaces all 8 (missing = 0).
- **API** (`backend/stock.py`):
  - `GET/PUT /api/stock/mine`: the bank's own sheet.
  - `GET /api/stock?blood_group=&lat=&lng=&district=&state=`: public search. Lists verified banks with fresh stock of
    that group or a compatible one, within 50 km of the point or in the same district, nearest first. Exact-group units
    and the compatible breakdown are shown separately.
  - SOS response gains `stock`: up to 5 of the same, around the request's point and district.
- **Web:**
  - Staff page: a "My stock" card for blood banks.
  - New public `/stock` page "Blood availability" (group + district or Near me), linked from the menu.
  - SOS-sent screen: an "Available at blood banks" card.
- **Bot:** the SOS confirmation lists nearby stock.
- **Freshness:** banks are hidden once stock is more than 48 h old. A reminder (Telegram + push via `notifier.tell`) is
  sent once a day while stock is 24 h–7 days old; after that the bank is treated as having stopped. Banks that never
  entered stock are not reminded. *(the 7-day cap is my call)*
- **Languages:** web text in all 10 languages; server and bot messages in en/kn/hi like the rest.

## Not included
Components, auto-decrement on donations, reservations/booking.

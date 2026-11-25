# Eligibility screening at registration: design

Date: 2026-11-25 · Feedback item #2

## Goal
Check permanent (genetic and chronic) conditions while a donor registers, require the basics (sex, date of birth,
weight), and explain every eligibility rule up front instead of only at donation time.

## Decisions (agreed)
1. A donor who reports a permanent condition is still registered but marked **cannot donate**: never alerted, cannot
   pledge, can use everything else. A kind message explains why.
2. Privacy: only a flag is stored (`permanently_ineligible`), never the specific condition.
3. The Telegram bot asks the same questions.
4. Existing donors keep receiving alerts and answer the check once, the first time they pledge (or from their profile).

## Permanent conditions (NBTC-based)
thalassaemia (major/intermedia; trait is fine), sickle_cell, bleeding (haemophilia or other bleeding disorder), hiv,
hepatitis (B or C), heart (heart attack, angina, heart surgery), cancer, epilepsy, kidney_liver (chronic),
insulin_diabetes.

## Data
`users.permanently_ineligible` (bool, default false), `users.screened_at` (datetime, null = not answered).
Hospital and blood bank accounts are never screened.

## Rules
- `eligibility.status()` adds `permanent` (flagged) and `screening` (donor not yet screened) reasons; both block
  pledging. `screening` is answered by sending `conditions` with the pledge screening.
- `can_be_alerted()` skips flagged donors (not unscreened ones).
- `POST /api/register` requires `sex`, `date_of_birth`, `weight_kg` and `conditions` (list of codes; empty = none) for
  donors. A non-empty list sets the flag and makes the donor unavailable.
- `POST /api/users/{id}/screening {conditions}` answers or re-answers the check (self or bot).
- `GET /api/eligibility/questions` returns the permanent condition codes and the general rules.

## UI
- Web registration: required basics, a "Who can donate" explainer, the checklist with an explicit "None of these
  apply to me" tick.
- Donate dialog and profile: the checklist for unscreened donors; a kind notice (and "redo") for flagged donors.
- Bot: after the phone step, sex → date of birth (typed) → weight band → conditions (✅ none / ⚠️ one applies). The
  pledge flow asks the conditions first for unscreened donors.
- Strings in all 10 web languages; bot strings in en/kn/hi.

## Demo data
Seeded donors are screened at registration time; bump `SEED_VERSION`.

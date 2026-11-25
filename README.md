# 🩸 BLOODLINK v2.0: Intelligent Blood Donor Network

A hybrid **React web app + Telegram bot** that matches blood requests with compatible donors using
ABO/Rh rules, alerts donors instantly on Telegram, and keeps them engaged with points, badges, vouchers and referrals.
See [architechure.md](architechure.md) for the full blueprint.

```
frontend/  React 18 + Vite 5 + Tailwind 3 + lucide-react   → http://localhost:5173
backend/   FastAPI + SQLAlchemy + SQLite                    → http://localhost:8000/api  (docs: /docs)
bot/       python-telegram-bot 22 (polling)
```

## Quick start (Windows / PowerShell)

```powershell
# 1. Python deps (one venv for backend + bot)
python -m venv .venv
.venv\Scripts\pip install -r backend\requirements.txt -r bot\requirements.txt

# 2. Frontend deps
cd frontend; npm install; cd ..

# 3. (optional) Telegram: create a bot with @BotFather, then
copy .env.example .env      # and paste TELEGRAM_BOT_TOKEN
```

Run each in its own terminal:

```powershell
cd backend;  ..\.venv\Scripts\python -m uvicorn main:app --reload --port 8000
cd frontend; npm run dev
cd bot;      ..\.venv\Scripts\python bot.py          # only if TELEGRAM_BOT_TOKEN is set
```

Open http://localhost:5173. The database is created and seeded with demo donors and requests on first start.
The demo data simulates 18 months of network activity: about 700 donors and 35 hospitals in 6 states, about 770 SOS requests,
1,100 donations, referrals and voucher redemptions. Points, badges and stats all follow from that history.
`seed_data.py --refresh` replaces the demo data and keeps Telegram-linked accounts; `--reset` wipes everything.
Bumping `SEED_VERSION` in [backend/seed_data.py](backend/seed_data.py) makes a deployment refresh its demo data once on its next start.

**Donation verification:** "I Can Donate" creates a *pledge*. Hospital staff (the account named on the request) or a blood
bank in the request's district confirm it, and only then are points awarded, the unit counted and the next eligible
date set. Pledges nobody confirms within 24 hours expire as no-shows; every 3rd no-show pauses pledging for 30 days.
See [backend/verification.py](backend/verification.py).

Backend tests: `cd backend; ..\.venv\Scripts\pip install -r requirements-dev.txt; ..\.venv\Scripts\python -m pytest tests`

On macOS/Linux use `.venv/bin/python` instead of `.venv\Scripts\python`.

## Deploy for free (Render + Neon)

In production one service runs everything: [start.sh](start.sh) starts the bot, and the API also serves the built web app
(`frontend/dist`), so the site and `/api` share one URL.

1. **Database:** create a free Postgres at [neon.tech](https://neon.tech) and copy its connection string
   (`postgresql://…`). Render's free disk is wiped on every restart, so SQLite would lose data.
2. **App:** on [render.com](https://render.com) choose **New → Blueprint** and pick this repo. [render.yaml](render.yaml) sets everything up.
   Fill in `TELEGRAM_BOT_TOKEN`, `DATABASE_URL` (from Neon) and `BLOODLINK_WEB_URL` (`https://<name>.onrender.com`, which
   you can set after the first deploy).
3. **Keep it awake:** free Render services sleep after 15 minutes without web traffic, and then the bot stops answering. Add a
   free monitor at [cron-job.org](https://cron-job.org) or [UptimeRobot](https://uptimerobot.com) that opens
   `https://<name>.onrender.com/api/health` every 10 minutes. The free 750 hours a month cover one service running all the time.
4. **Stop the bot on your PC.** Telegram allows only one copy of a bot to poll at a time.

Set `AUTO_SEED=0` if you don't want demo data in the live database.

## Features

| Area | What's there |
|---|---|
| **Live feed** (`/`) | Active SOS requests, polled every 4 s, colour-coded by urgency, filter by group or "I can help", one-click donate |
| **SOS** (`/sos`) | Blood group, hospital, city, units, urgency. Shows matched donors and how many were alerted on Telegram |
| **Donor search** (`/donors`) | By exact group or "can donate to" (ABO/Rh matrix), city and availability |
| **Register** (`/register?ref=CODE`) | +50 BLP, plus a +50 welcome bonus with a referral code. Shows the referral code and a Link Telegram button. Donors give sex, date of birth and weight and answer a permanent-conditions check (thalassaemia, sickle cell, haemophilia, HIV, hepatitis B/C, heart disease and more); someone who reports one is registered but never alerted, and only that outcome is stored |
| **Dashboard** (`/profile`) | Points, badge progress, availability toggle, referral links and stats, points, donation and voucher history |
| **Leaderboard** (`/leaderboard`) | Live top 10 with a podium, badges, blood groups and the 🗣️ Influencer badge (5+ referrals) |
| **Rewards** (`/rewards`) | Coffee 100 · Movie 250 · Shopping 500 · Merch 1000 BLP. Issues a fake voucher code, also sent to Telegram |
| **Confirm donations** (`/staff`) | Hospital and blood bank accounts confirm each pledged donor (with an optional haemoglobin reading) or mark them as not come. Points and the next donation date follow only confirmed donations |
| **Admin** (`/admin`) | Demand vs. supply by group, city demand heatmap, average response time, confirmed donations and no-shows, verify/cancel/fulfil requests, verify users and assign roles, voucher log |

**Telegram bot:** fully button-driven, in **English, ಕನ್ನಡ or हिन्दी** (asked on `/start`, changeable with `/language`).
`/menu` shows buttons for everything. Registration is name (one tap to use your Telegram name) → blood group → state → district →
Telegram's "share phone" button. SOS is blood group → state → district (or one tap for your saved location) → hospital → units →
urgency → share phone. Typing is only needed for a place or hospital that isn't listed. Locations live in
[backend/locations.py](backend/locations.py): every district of Karnataka, Kerala, Tamil Nadu, Maharashtra, Delhi and Goa, plus
a starter list of hospitals. SOS alerts reach each donor in their own language. SOS alerts carry a **🩸 I Can Donate** button: one tap pledges
to donate and tells the requester a donor is on the way. Hospital and blood bank staff get the pledge on Telegram with
**✅ Donated** / **❌ Didn't come** buttons; points are awarded only when they confirm. Deep links: `t.me/<bot>?start=USER_12345` (referral) and `?start=link_USER_12345`
(link a web account).

### Donor safety and engagement

- **Eligibility check.** Before donating, on the web or Telegram, donors answer a 20-second self-check based on India's NBTC guidelines:
  - age 18–65 and weight at least 45 kg;
  - at least 90 days since the last donation for men, 120 for women;
  - recent fever or infection, antibiotics, alcohol, tattoo or piercing, surgery, pregnancy or breastfeeding.

  The server re-checks before accepting a donation. SOS alerts skip donors who can't donate yet. A "yes" pauses alerts until
  that date, and the donor can undo it from their profile. Rules are in [backend/eligibility.py](backend/eligibility.py). It's
  a preliminary check: hospital staff always decide.
- **Donation reminders** on Telegram: 5 days before a donor can give again, on the day (with an "I'm available" button), and a
  gentle nudge a week later. They run hourly in the backend ([backend/reminders.py](backend/reminders.py)) and are sent once per
  donation cycle. Run them on demand with `POST /api/admin/reminders/run`, or turn them off with `REMINDERS=0`.
- **Royal shareable cards:** 1080×1080 images drawn in the browser, in five designs: Blood Royalty, Achievement Crown, Diamond
  Elite, Emerald Guardian and Midnight Hero. Each has the donor's QR invite code. Offered after a donation, on each unlocked
  achievement and on the profile. They share natively on phones (image straight to WhatsApp or Instagram), or via
  WhatsApp/Telegram/X/LinkedIn/Facebook links, or as a download.

### Showcase accounts

Four long-time donors whose real histories earn (almost) every achievement. While `DEMO_LOGIN=1` the sign-in panel offers
each one as a chip, showing their live achievement count:

| Code | Donor | Blood | Achievements | Missing |
|---|---|---|---|---|
| `USER_77777` | **Sinchana** | AB- | 52/54 | Iron Will, Hot Streak Platinum |
| `USER_77701` | **Sanjana** | O- | 51/54 | Iron Will, Hot Streak Platinum, The Unicorn (not AB-) |
| `USER_77702` | **Varsha** | AB- | 51/54 | Iron Will, Hot Streak Platinum, Bloodline Ambassador (40 referrals) |
| `USER_77703` | **Vrusha** | B+ | 50/54 | Iron Will, Hot Streak Platinum, The Unicorn, Bloodline Royalty (42 donations) |

All four have:
- donations at least 120 days apart (the safe interval for women), across five states;
- 5-minute and 2 AM responses, donations on New Year's Day, at a festival and in the rain, and 3 camp donations;
- verified status and Admin's Favorite;
- membership of The Bloodline Squad and a shared location;
- eligibility to donate today.

With a 120-day interval you can't donate in eight quarters in a row, so Iron Will is out of reach. Each of the four still has one perfect year (January, May, August, December) for Unstoppable.

### Demo data that stays alive

- **Self-healing:** at startup the server seeds an empty database. It refreshes the demo data when `SEED_VERSION` changes, or
  whenever demo data is missing (fewer than 50 demo donors). The refresh runs in **one transaction**, so the site is never seen
  empty, and a failure leaves the old data in place. Only rows flagged `is_demo` are replaced; real accounts (Telegram,
  web-registered, admin) and real SOS requests are kept.
- **Demo activity** (on while `DEMO_LOGIN=1`; `DEMO_PULSE=0` turns it off):
  - a new realistic SOS appears every 15–35 minutes;
  - demo donors pledge at realistic speeds (Critical fastest);
  - stale requests close after about a day.

  Simulated requests never message anyone on Telegram and never escalate.
- **Live activity strip** on the home page: the latest pledges, shown as first name and surname initial only.

### Nearest donors first

- **Opt-in location:** donors share their location once (the profile's "Nearby alerts" card, or Telegram's 📍 button). It's
  rounded to about 1 km and never shown to anyone. Requesters only ever see distances rounded to half a kilometre.
- **SOS location:** an SOS carries the hospital's location ("I'm at the hospital: use my location"), or falls back to the
  district centre.
- **Alerts go out in widening circles:**
  - The first wave covers 5 km, growing to 15 km, 40 km, or the rest of the state until at least 8 donors are reached.
  - If the request is still open, the next circle is alerted after 5 minutes (Critical), 10 (High) or 20 (Normal).
  - Nobody is alerted twice, and widening stops once the request is fulfilled.
  - Escalation state lives in the database (`sos_alerts`, `alert_ring`, `next_ring_at`), so a restart doesn't lose it.
- **Distances shown:** Telegram alerts say "📍 About 3 km from you", and the live feed shows distances with a "Nearest first"
  sort.
- Code: [backend/geo.py](backend/geo.py) and `alert_plan` / `escalate_once` in [backend/main.py](backend/main.py).

### Sign-in and security

- **Log in with Telegram.** The site gets a one-time link (`t.me/<bot>?start=login_<nonce>`), you tap Start, the bot
  confirms who you are (Telegram vouches for the id), and the browser receives a session token. There are no passwords to leak.
- **Sessions:** random 256-bit tokens, stored only as SHA-256, valid for 30 days, and revoked on sign-out. Registering on the
  web signs you in straight away. Link Telegram afterwards (a one-time `link_<nonce>`) to sign in on other devices.
- **Every action is checked on the server.** You can only donate, redeem, RSVP, change settings or read private data as
  yourself. The bot is a trusted service (header `X-Bot-Secret`, derived from the bot token) and acts only for the Telegram user
  who is messaging it.
- **Admin portal:** sign in with `ADMIN_PASSWORD`, or with a Telegram account listed in `ADMIN_TELEGRAM_IDS`. A hospital account
  can verify, fulfil or cancel requests at its own hospital.
- **Demo mode:** with `DEMO_LOGIN=1`, *seeded demo accounts* can be opened by their code so judges can explore. Real accounts
  never can, because referral codes are public invite codes. Set `DEMO_LOGIN=0` for real-world use.
- Code: [backend/auth.py](backend/auth.py).

### Teams and donation camps

- **Teams** (`/teams`): colleges, companies, communities and friend groups. Create a team, share its invite code, and climb the
  team leaderboard. A team scores only donations its members make *after* joining. Team pages show members ranked by
  contribution and the gap to the team above.
- **Camps** (`/camps`): anyone signed in can post a blood drive.
  - Donors RSVP. If they won't be eligible by the camp day, they're told up front.
  - Telegram reminders go out 3 days before, the day before and on the day.
  - The organiser marks attendance, which records the donation (+100 BLP), restarts the donor's safe-interval clock, and
    unlocks 🎪 First Camp / 🏕️ Camp Champion.
- **Telegram:** `/camps` (upcoming camps in your state, one-tap RSVP) and `/teams`.
- **Code:** [backend/community.py](backend/community.py).

### Languages

The web app is available in English, ಕನ್ನಡ, हिन्दी, മലയാളം, தமிழ், తెలుగు, বাংলা, অসমীয়া, कोंकणी (Konkani) and ತುಳು (Tulu).
The header language picker remembers the choice and saves it to the account, so Telegram messages follow it.
Dictionaries are in [frontend/src/i18n/](frontend/src/i18n/). `npm run i18n:check` (also run by `npm run build`) checks that
every file has exactly the keys and `{placeholders}` of `en.js`, with nothing empty, and no letters from another script
(for example Malayalam letters inside Tamil). Each language loads its own Noto font.
The Telegram bot itself speaks English, ಕನ್ನಡ and हिन्दी; for the other languages it falls back to English.

### Achievements

GitHub-style collectible badges, separate from spendable BLP (each one pays a one-off BLP bonus when unlocked). There are 36
achievements across Donation, Speed, Referral, Streak, Location, Fun and Verification, plus 4 tiered badges that level up
Bronze → Silver → Gold → Platinum: 🦈 Blood Shark (donations), ⚡ Quickdraw (responses under 5 minutes), 🤝 Recruiter
(referrals) and 🔥 Hot Streak. They are computed from real history in [backend/achievements.py](backend/achievements.py), so each
records when it was earned. Rarity percentages are live ("3% of donors").

- **Web:** `/achievements` shows the collection with progress bars and NEW tags. The profile and leaderboard show each user's
  rarest icons, and the donate dialog celebrates new unlocks.
- **Telegram:** `/achievements` (or 🏅 in the menu) shows the collection. Unlocks arrive as messages in the user's language.
- **Admin:** ⭐ Favorite in the Users tab awards "Admin's Favorite".
- **Safety:** streaks count consecutive 3-month windows, never months, because whole-blood donors need 90+ days between
  donations (120 for women). Rainmaker checks the weather through [Open-Meteo](https://open-meteo.com), which is free and
  needs no key, in the background after a donation; only the district name is sent. Set `WEATHER_CHECK=0` to turn it off.

### Points (BLP)

Register +50 · referral welcome bonus +50 · donation +100 · response under 5 min +20 · donating again after 3+ months +50 ·
friend registers +50 to the referrer · friend's first donation +200 and a $5 voucher to the referrer.
Badges: 🥉 Bronze 0+, 🥈 Silver 101+, 🥇 Gold 501+, 💎 Platinum 1000+.

## Hackathon simplifications

- **No login.** The web app remembers the user in `localStorage`; "Sign in" means entering your referral code. The admin portal is open.
- **Vouchers are fake codes.** Location matching is by city name. Donation verification is a confirmation checkbox.
- **Compatibility is preliminary.** Medical eligibility is confirmed by the hospital. No AI/ML is used.

## API

Base URL `http://localhost:8000/api`. Interactive docs are at http://localhost:8000/docs.

`POST /register` · `POST /sos` · `GET /requests?status=Active|Fulfilled|Cancelled|all` · `GET /requests/{id}` ·
`POST /donate/{request_id}` `{user_id | donor_telegram_id, confirmed}` · `GET /leaderboard` · `GET /rewards` ·
`POST /redeem/{reward_id}` `{user_id | telegram_id}` · `GET /compatible/{group}` · `GET /donors` ·
`GET /users/{id}` · `GET /users/by-code/{code}` · `GET /users/by-telegram/{tid}` · `GET /users/{id}/activity` ·
`POST /users/link-telegram` · `PATCH /users/{id}/availability` · `GET /config` ·
`GET /admin/stats|users|vouchers` · `POST /admin/users/{id}/verify` · `POST /admin/requests/{id}/verify|status`

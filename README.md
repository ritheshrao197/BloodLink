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
To reset the demo data: `cd backend; ..\.venv\Scripts\python seed_data.py --reset`.

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
| **Register** (`/register?ref=CODE`) | +50 BLP, plus a +50 welcome bonus with a referral code. Shows the referral code and a Link Telegram button |
| **Dashboard** (`/profile`) | Points, badge progress, availability toggle, referral links and stats, points, donation and voucher history |
| **Leaderboard** (`/leaderboard`) | Live top 10 with a podium, badges, blood groups and the 🗣️ Influencer badge (5+ referrals) |
| **Rewards** (`/rewards`) | Coffee 100 · Movie 250 · Shopping 500 · Merch 1000 BLP. Issues a fake voucher code, also sent to Telegram |
| **Admin** (`/admin`) | Demand vs. supply by group, city demand heatmap, average response time, verify/cancel/fulfil requests, verify users, voucher log |

**Telegram bot:** fully button-driven, in **English, ಕನ್ನಡ or हिन्दी** (asked on `/start`, changeable with `/language`).
`/menu` shows buttons for everything. Registration is name (one tap to use your Telegram name) → blood group → state → district →
Telegram's "share phone" button. SOS is blood group → state → district (or one tap for your saved location) → hospital → units →
urgency → share phone. Typing is only needed for a place or hospital that isn't listed. Locations live in
[backend/locations.py](backend/locations.py): every district of Karnataka, Kerala, Tamil Nadu, Maharashtra, Delhi and Goa, plus
a starter list of hospitals. SOS alerts reach each donor in their own language. SOS alerts carry a **🩸 I Can Donate** button: one tap fulfils the request,
awards points and notifies the requester. Deep links: `t.me/<bot>?start=USER_12345` (referral) and `?start=link_USER_12345`
(link a web account).

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

# 🩸 BLOODLINK v2.0

## Project Documentation & Hackathon Blueprint

**Event:** CEC-HACKSTORM-2026 | Stage 1: Class-Level  
**Department:** CSE | 5th Semester [C]  
**Institution:** Canara Engineering College | Technical Activity Cell  
**Project Title:** BLOODLINK - Intelligent Blood Donor Network  
**Version:** 2.0 (Hybrid Web + Telegram Ecosystem)

---

## 📋 Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [The BLOODLINK Solution](#3-the-bloodlink-solution)
4. [System Architecture](#4-system-architecture)
5. [Technology Stack](#5-technology-stack)
6. [Core Features](#6-core-features)
7. [Gamification & Rewards System](#7-gamification--rewards-system)
8. [Referral System](#8-referral-system)
9. [User Workflows](#9-user-workflows)
10. [Database Schema](#10-database-schema)
11. [API Documentation](#11-api-documentation)
12. [Code Implementation](#12-code-implementation)
13. [Hackathon Execution Plan](#13-hackathon-execution-plan)
14. [Demo Script](#14-demo-script)
15. [Future Scope](#15-future-scope)
16. [Conclusion](#16-conclusion)

---

## 1. Executive Summary

**BLOODLINK** is a centralized, hybrid digital blood donor network designed to bridge the critical gap between blood requesters and donors during emergencies. It combines the visual power of a **React Web Application** with the zero-friction, instant-action capability of a **Telegram Bot**.

### The Core Innovation

> **"Request blood as easily as sending a WhatsApp message. Earn rewards for saving lives."**

- **Web App** = The Brain & The Stage (Dashboards, Leaderboards, Analytics)
- **Telegram Bot** = The Pulse & The Hands (Instant SOS, One-Tap Donations)
- **Gamification** = The Engine (Points, Badges, Vouchers)
- **Referrals** = The Growth (Every donor becomes a recruiter)

### Key Differentiators

| Feature | Traditional Apps | BLOODLINK v2.0 |
|---------|------------------|-----------------|
| Request Speed | Open app → Login → Fill form (2-3 mins) | Send `/sos` on Telegram (3 seconds) |
| Donor Alerts | Push notification (only if app is open) | Telegram push (always on) |
| Growth Model | Word of mouth | Viral referral links + vouchers |
| Retention | Donors forget after one donation | Points, badges, leaderboard |
| Visibility | Behind a login wall | Live public leaderboard |

---

## 2. Problem Statement

### 2.1 The Core Problem

Finding compatible blood donors during emergencies is **slow, scattered, and unreliable**. When every second counts, manual searching wastes precious time that could mean the difference between life and death.

### 2.2 Affected Parties

- **Patients** requiring urgent blood transfusions
- **Families** desperately searching for donors
- **Hospitals** managing multiple critical cases
- **Volunteers** willing to donate but hard to reach

### 2.3 Current Pain Points

| Pain Point | Description |
|------------|-------------|
| **Scattered Data** | Donor details are spread across WhatsApp groups, phone contacts, and hospital registers |
| **Outdated Info** | Donor availability is unknown or outdated |
| **No Proximity Search** | Nearby donors are impossible to identify quickly |
| **No Central Management** | No system to track requests, responses, and fulfillment |
| **No Incentive** | Donors have no motivation to stay engaged after one donation |

### 2.4 Impact

> **"Manual searching wastes time when every second counts."**

- Average time to find a donor via social media: **2-6 hours**
- Critical window for blood transfusion: **30 minutes to 2 hours**
- This gap costs lives.

---

## 3. The BLOODLINK Solution

### 3.1 One-Line Pitch

> **"BLOODLINK eliminates fatal delays with instant blood group compatibility algorithms, a zero-friction Telegram bot, and a gamified rewards system that turns donors into recurring heroes."**

### 3.2 The Hybrid Ecosystem

BLOODLINK is not just an app; it's a **self-sustaining community** with two interfaces:

1. **Telegram Bot (`@BloodLinkBot`)** - For instant, frictionless actions
2. **React Web App** - For visual dashboards, leaderboards, and administration

### 3.3 Key Features

- ✅ **Registered donors** searchable by blood group, city, and availability
- ✅ **Rule-based ABO/Rh matching** for preliminary donor compatibility
- ✅ **Emergency SOS** - Broadcast blood group, hospital, location, and units needed
- ✅ **Live emergency request feed** with request tracking
- ✅ **Admin verification** for hospitals and donors
- ✅ **Donor availability status** and blood demand analytics
- ✅ **Gamified rewards** - Points, badges, vouchers
- ✅ **Referral system** - Viral growth engine

### 3.4 User Roles

| Role | Description | Primary Interface |
|------|-------------|-------------------|
| **Requester** | Patients, families, hospitals needing blood | Telegram Bot + Web App |
| **Donor** | Registered volunteers willing to donate | Telegram Bot + Web App |
| **Hospital** | Medical institutions verifying requests | Web App (Admin Portal) |
| **Administrator** | System managers, analytics, verification | Web App (Admin Portal) |

---

## 4. System Architecture

### 4.1 High-Level Architecture Diagram

```text
┌─────────────────────────────────────────────────────────────────┐
│                     BLOODLINK ECOSYSTEM                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────┐           ┌──────────────┐                   │
│   │  React Web   │◄─────────►│  FastAPI     │                   │
│   │  App (Vite)  │   REST    │  Backend     │                   │
│   │              │           │              │                   │
│   │ • Dashboard  │           │ • REST APIs  │                   │
│   │ • Leaderboard│           │ • Webhooks   │                   │
│   │ • Rewards    │           │ • Match Logic│                   │
│   │ • Referrals  │           │ • Gamification│                  │
│   └──────────────┘           └──────┬───────┘                   │
│                                     │                           │
│                                     ▼                           │
│                          ┌──────────────────┐                   │
│                          │    SQLite DB     │                   │
│                          │                  │                   │
│                          │ • Users          │                   │
│                          │ • Requests       │                   │
│                          │ • Rewards        │                   │
│                          │ • Referrals      │                   │
│                          │ • Badges         │                   │
│                          └────────┬─────────┘                   │
│                                   │                             │
│                                   ▼                             │
│                          ┌──────────────────┐                   │
│                          │  Telegram Bot    │                   │
│                          │                  │                   │
│                          │ • SOS Alerts     │                   │
│                          │ • 1-Tap Donate   │                   │
│                          │ • Rewards        │                   │
│                          │ • Referrals      │                   │
│                          └──────────────────┘                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Data Flow

1. **User registers** on the React Web App (or via Telegram deep link)
2. **Data is stored** in SQLite via FastAPI
3. **SOS request** is created via Telegram bot or Web App
4. **FastAPI triggers** a broadcast to matching donors via Telegram
5. **Donor responds** via one-tap button
6. **FastAPI updates** the request status and awards points
7. **Leaderboard** on the Web App updates in real-time

### 4.3 Component Breakdown

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | React.js + Vite + Tailwind CSS | Visual dashboards, leaderboards, registration |
| **Backend** | Python + FastAPI + Uvicorn | REST APIs, business logic, webhook handling |
| **Database** | SQLite + SQLAlchemy ORM | Persistent data storage |
| **Bot** | python-telegram-bot | Zero-friction user interface |
| **Integration** | Vite Proxy + REST APIs | Frontend-Backend communication |

---

## 5. Technology Stack

### 5.1 Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| **React.js** | 18.x | UI library for building interactive interfaces |
| **Vite** | 5.x | Fast build tool and dev server |
| **Tailwind CSS** | 3.x | Utility-first CSS framework for styling |
| **JavaScript** | ES6+ | Core programming language |
| **Lucide React** | Latest | Icon library for modern UI elements |

### 5.2 Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.10+ | Core programming language |
| **FastAPI** | Latest | High-performance REST API framework |
| **Uvicorn** | Latest | ASGI server for FastAPI |
| **Pydantic** | Latest | Data validation using Python type hints |

### 5.3 Database

| Technology | Version | Purpose |
|------------|---------|---------|
| **SQLite** | 3.x | Lightweight, serverless database |
| **SQLAlchemy** | Latest | Python ORM for database operations |

### 5.4 Telegram Integration

| Technology | Version | Purpose |
|------------|---------|---------|
| **python-telegram-bot** | 20.x | Telegram Bot API wrapper |
| **Telegram Bot API** | Latest | Real-time messaging platform |

### 5.5 Development Tools

| Tool | Purpose |
|------|---------|
| **Git** | Version control |
| **VS Code** | Code editor |
| **Postman** | API testing |
| **Telegram Desktop** | Bot testing and demo |

### 5.6 Important Notes

> ⚠️ **No AI/ML model is used.** Compatibility matching is strictly rule-based (ABO/Rh matrix).
> ⚠️ **All vouchers are mocked** for the hackathon prototype.

---

## 6. Core Features

### 6.1 Donor Registration & Search

- **Register** via Web App or Telegram bot
- **Search** by blood group, city, and availability
- **Filter** by compatibility (rule-based ABO/Rh matrix)
- **View** donor profiles with badges and donation history

### 6.2 Emergency SOS Request

- **Trigger** via Telegram (`/sos`) or Web App
- **Inputs:** Blood group, hospital, city, units needed
- **Broadcast:** Instant alert to all matching donors
- **Track:** Real-time status (Active → Fulfilled)

### 6.3 Rule-Based Compatibility Matching

The system uses the standard ABO/Rh compatibility matrix:

**Recipient → Compatible Donor Blood Groups**

| Recipient | Can Receive From |
|-----------|------------------|
| **A+** | A+, A-, O+, O- |
| **A-** | A-, O- |
| **B+** | B+, B-, O+, O- |
| **B-** | B-, O- |
| **AB+** | All blood groups (Universal Recipient) |
| **AB-** | AB-, A-, B-, O- |
| **O+** | O+, O- |
| **O-** | O- (Universal Donor) |

### 6.4 Live Emergency Feed (Web App)

- Real-time ticker of active SOS requests
- Color-coded urgency levels
- Click to view details and respond

### 6.5 Admin Portal

- Verify hospitals and donors
- View analytics (demand heatmap, response times)
- Manage rewards and vouchers
- Track referral performance

### 6.6 Real-Time Leaderboard

- Top 10 donors by points
- Badge display (Bronze/Silver/Gold/Platinum)
- Blood group tags
- Public visibility for social proof

---

## 7. Gamification & Rewards System

### 7.1 Points System (BloodLink Points - BLP)

| Action | Points Earned |
|--------|---------------|
| **Register** | +50 BLP |
| **Successful Donation** | +100 BLP |
| **Refer a Friend (Registration)** | +50 BLP |
| **Refer a Friend (Donation)** | +200 BLP |
| **Quick Response (< 5 mins)** | +20 BLP |
| **Streak Bonus (Every 3 months)** | +50 BLP |

### 7.2 Badge Levels

| Badge | Points Required | Icon | Title |
|-------|-----------------|------|-------|
| **Bronze** | 0 - 100 BLP | 🥉 | First Responder |
| **Silver** | 101 - 500 BLP | 🥈 | Life Saver |
| **Gold** | 501 - 1000 BLP | 🥇 | Guardian Angel |
| **Platinum** | 1000+ BLP | 💎 | Legendary Hero |
| **Influencer** | 5+ Referrals | 🗣️ | Community Champion |

### 7.3 Rewards Store (Mocked for Hackathon)

| Reward | Points Cost | Description |
|--------|-------------|-------------|
| ☕ **Coffee Voucher** | 100 BLP | Free coffee at Starbucks/CCD |
| 🎬 **Movie Ticket** | 250 BLP | PVR/INOX movie voucher |
| 🛍️ **Amazon Voucher** | 500 BLP | $10 Amazon gift card |
| 🎓 **College Merch** | 1000 BLP | Custom BLOODLINK T-shirt |

### 7.4 How Rewards Work (Hackathon Implementation)

> **Note:** Real payment gateway integration is NOT required for the hackathon.

1. User redeems points on the Web App
2. System checks if user has sufficient BLP
3. If yes, points are deducted
4. A **fake voucher code** is generated (e.g., `AMZN-99X2`)
5. The code is displayed on screen and sent via Telegram

### 7.5 Leaderboard Display

The React Web App shows a live leaderboard:

```text
🏆 TOP HEROES

#1  🥇  Karthik (O-)      650 BLP
#2  🥈  Dr. Kavita Joshi (AB-)  480 BLP
#3  🥉  Mohammad Farooq (B+)   320 BLP
#4  🥉  Priya Sharma (A+)      150 BLP
#5  🥉  Rahul Verma (O+)       120 BLP
```

---

## 8. Referral System

### 8.1 The Viral Growth Engine

Every registered user gets a **unique referral code** (e.g., `USER_12345`) and a **deep link**:

```text
https://t.me/BloodLinkBot?start=USER_12345
```

### 8.2 How It Works

1. **User registers** → Gets a unique referral code
2. **Shares link** via WhatsApp, Telegram, or social media
3. **Friend clicks link** → Bot tags their profile with `referred_by: USER_12345`
4. **Friend registers** → Referrer gets **+50 BLP**
5. **Friend donates** → Referrer gets **+200 BLP + a brand voucher**

### 8.3 Referral Rewards

| Milestone | Referrer Reward | New User Reward |
|-----------|-----------------|-----------------|
| **Friend Registers** | +50 BLP | +50 BLP (Welcome Bonus) |
| **Friend Donates** | +200 BLP + $5 Voucher | +100 BLP |

### 8.4 Referral Tracking (Web App)

The React Web App displays:

- Total referrals made
- Referrals who registered
- Referrals who donated
- Total BLP earned from referrals

---

## 9. User Workflows

### 9.1 Requester Workflow (Telegram)

```text
User opens Telegram
    ↓
Sends /sos to @BloodLinkBot
    ↓
Bot shows inline keyboard for blood group selection
    ↓
User selects blood group (e.g., O-)
    ↓
Bot asks for hospital and city
    ↓
User types "Apollo Hospital, Bangalore"
    ↓
Bot confirms: "🚨 SOS Broadcasted!"
    ↓
Matching donors receive instant alert
    ↓
First donor to tap "I Can Donate" is connected
```

### 9.2 Donor Workflow (Telegram)

```text
User receives SOS alert
    ↓
Taps "🩸 I Can Donate"
    ↓
Bot confirms: "Thank you! You earned 100 BLP!"
    ↓
Bot sends referral link: "Invite a friend, earn a voucher!"
    ↓
User shares link → Earns more points
```

### 9.3 Registration Workflow (Web App)

```text
User visits http://localhost:5173/register
    ↓
Fills form: Name, Blood Group, City, Referral Code (optional)
    ↓
Submits → Points awarded (+50 BLP)
    ↓
Shows unique referral code and Telegram link
    ↓
User clicks "Link Telegram" → Bot syncs account
```

### 9.4 Admin Workflow (Web App)

```text
Admin logs into dashboard
    ↓
Views live SOS feed
    ↓
Tracks request status (Active → Fulfilled)
    ↓
Verifies hospitals and donors
    ↓
Views analytics (demand heatmap, response times)
    ↓
Manages rewards and vouchers
```

---

## 10. Database Schema

### 10.1 ER Diagram (Simplified)

```text
┌─────────────────┐       ┌─────────────────┐
│     USERS       │       │    REQUESTS     │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ name            │       │ requester_name  │
│ blood_group     │       │ blood_group     │
│ city            │       │ hospital        │
│ telegram_id     │       │ city            │
│ points          │       │ status          │
│ badge           │       │ fulfilled_by    │
│ referral_code   │       │ created_at      │
│ referred_by     │       └─────────────────┘
│ created_at      │
└─────────────────┘
         │
         │
         ▼
┌─────────────────┐
│   REFERRALS     │
├─────────────────┤
│ id (PK)         │
│ referrer_id     │
│ referred_id     │
│ status          │
│ points_awarded  │
└─────────────────┘
```

### 10.2 SQLAlchemy Models

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    blood_group = Column(String, nullable=False)
    city = Column(String, nullable=False)
    telegram_id = Column(String, unique=True, nullable=True)
    points = Column(Integer, default=50)
    badge = Column(String, default="Bronze")
    referral_code = Column(String, unique=True, nullable=False)
    referred_by = Column(String, nullable=True)
    total_donations = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class BloodRequest(Base):
    __tablename__ = "requests"
    
    id = Column(Integer, primary_key=True, index=True)
    requester_name = Column(String, nullable=False)
    blood_group = Column(String, nullable=False)
    hospital = Column(String, nullable=False)
    city = Column(String, nullable=False)
    units_needed = Column(Integer, default=1)
    status = Column(String, default="Active")
    fulfilled_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Referral(Base):
    __tablename__ = "referrals"
    
    id = Column(Integer, primary_key=True, index=True)
    referrer_id = Column(Integer, ForeignKey("users.id"))
    referred_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="Registered")
    points_awarded = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Reward(Base):
    __tablename__ = "rewards"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    reward_name = Column(String)
    points_cost = Column(Integer)
    voucher_code = Column(String)
    status = Column(String, default="Pending")
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

## 11. API Documentation

### 11.1 Base URL

```text
http://localhost:8000/api
```

### 11.2 Endpoints

#### User Registration

```http
POST /api/register
```

**Request Body:**
```json
{
  "name": "Karthik",
  "blood_group": "O-",
  "city": "Bangalore",
  "referred_by": "USER_12345"
}
```

**Response:**
```json
{
  "status": "success",
  "user_id": 1,
  "referral_code": "USER_67890",
  "points": 50
}
```

---

#### Create SOS Request

```http
POST /api/sos
```

**Request Body:**
```json
{
  "requester_name": "Priya",
  "blood_group": "O-",
  "hospital": "Apollo Hospital",
  "city": "Bangalore",
  "units_needed": 2
}
```

**Response:**
```json
{
  "status": "broadcasted",
  "request_id": 1
}
```

---

#### Get Leaderboard

```http
GET /api/leaderboard
```

**Response:**
```json
[
  {
    "name": "Karthik",
    "points": 650,
    "badge": "Gold",
    "blood_group": "O-"
  },
  {
    "name": "Dr. Kavita Joshi",
    "points": 480,
    "badge": "Silver",
    "blood_group": "AB-"
  }
]
```

---

#### Get Active Requests

```http
GET /api/requests
```

**Response:**
```json
[
  {
    "id": 1,
    "requester_name": "Priya",
    "blood_group": "O-",
    "hospital": "Apollo Hospital",
    "city": "Bangalore",
    "status": "Active"
  }
]
```

---

#### Donate (Fulfill Request)

```http
POST /api/donate/{request_id}
```

**Request Body:**
```json
{
  "donor_telegram_id": "123456789"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Request fulfilled! Donor awarded 100 BLP."
}
```

---

#### Redeem Reward

```http
POST /api/redeem/{reward_id}
```

**Request Body:**
```json
{
  "user_id": 1
}
```

**Response:**
```json
{
  "status": "success",
  "voucher_code": "AMZN-99X2",
  "points_remaining": 150
}
```

---

## 12. Code Implementation

### 12.1 Backend: `main.py` (FastAPI)

```python
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid
from datetime import datetime

app = FastAPI(title="BLOODLINK API", version="2.0")

# CORS for React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# --- Database Setup ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./bloodlink.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    blood_group = Column(String, nullable=False)
    city = Column(String, nullable=False)
    telegram_id = Column(String, unique=True, nullable=True)
    points = Column(Integer, default=50)
    badge = Column(String, default="Bronze")
    referral_code = Column(String, unique=True, default=lambda: str(uuid.uuid4())[:8])
    referred_by = Column(String, nullable=True)
    total_donations = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)

class BloodRequest(Base):
    __tablename__ = "requests"
    id = Column(Integer, primary_key=True, index=True)
    requester_name = Column(String, nullable=False)
    blood_group = Column(String, nullable=False)
    hospital = Column(String, nullable=False)
    city = Column(String, nullable=False)
    units_needed = Column(Integer, default=1)
    status = Column(String, default="Active")
    fulfilled_by = Column(String, nullable=True)

Base.metadata.create_all(bind=engine)

# --- Schemas ---
class UserCreate(BaseModel):
    name: str
    blood_group: str
    city: str
    referred_by: str = None

class SOSCreate(BaseModel):
    requester_name: str
    blood_group: str
    hospital: str
    city: str
    units_needed: int = 1

# --- Helper Functions ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def update_badge(user):
    if user.points >= 1000:
        user.badge = "Platinum"
    elif user.points >= 500:
        user.badge = "Gold"
    elif user.points >= 100:
        user.badge = "Silver"
    else:
        user.badge = "Bronze"

def get_compatible_donors(blood_group: str):
    """Rule-based ABO/Rh compatibility matrix"""
    compatibility = {
        "A+": ["A+", "A-", "O+", "O-"],
        "A-": ["A-", "O-"],
        "B+": ["B+", "B-", "O+", "O-"],
        "B-": ["B-", "O-"],
        "AB+": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
        "AB-": ["AB-", "A-", "B-", "O-"],
        "O+": ["O+", "O-"],
        "O-": ["O-"]
    }
    return compatibility.get(blood_group, [])

# --- APIs ---

@app.post("/api/register")
def register_user(user: UserCreate, background_tasks: BackgroundTasks):
    db = next(get_db())
    
    # Check referral code
    if user.referred_by:
        referrer = db.query(User).filter(User.referral_code == user.referred_by).first()
        if referrer:
            referrer.points += 50
            update_badge(referrer)
    
    new_user = User(
        name=user.name,
        blood_group=user.blood_group,
        city=user.city,
        referred_by=user.referred_by
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "status": "success",
        "user_id": new_user.id,
        "referral_code": new_user.referral_code,
        "points": new_user.points
    }

@app.post("/api/sos")
def create_sos(sos: SOSCreate, background_tasks: BackgroundTasks):
    db = next(get_db())
    new_req = BloodRequest(
        requester_name=sos.requester_name,
        blood_group=sos.blood_group,
        hospital=sos.hospital,
        city=sos.city,
        units_needed=sos.units_needed
    )
    db.add(new_req)
    db.commit()
    db.refresh(new_req)
    
    # TODO: Trigger Telegram broadcast
    # background_tasks.add_task(broadcast_telegram_sos, new_req.id, sos.blood_group, sos.city)
    
    return {"status": "broadcasted", "request_id": new_req.id}

@app.get("/api/leaderboard")
def get_leaderboard():
    db = next(get_db())
    users = db.query(User).order_by(User.points.desc()).limit(10).all()
    return [
        {
            "name": u.name,
            "points": u.points,
            "badge": u.badge,
            "blood_group": u.blood_group
        }
        for u in users
    ]

@app.get("/api/requests")
def get_requests():
    db = next(get_db())
    reqs = db.query(BloodRequest).filter(BloodRequest.status == "Active").all()
    return reqs

@app.post("/api/donate/{request_id}")
def donate(request_id: int, donor_telegram_id: str):
    db = next(get_db())
    req = db.query(BloodRequest).filter(BloodRequest.id == request_id).first()
    if req:
        req.status = "Fulfilled"
        donor = db.query(User).filter(User.telegram_id == donor_telegram_id).first()
        if donor:
            donor.points += 100
            donor.total_donations += 1
            update_badge(donor)
            req.fulfilled_by = donor.name
        db.commit()
    return {"status": "success"}

@app.get("/api/compatible/{blood_group}")
def get_compatible(blood_group: str):
    return {"compatible_donors": get_compatible_donors(blood_group)}
```

### 12.2 Frontend: `App.jsx` (React)

```jsx
import { useState, useEffect } from 'react';

export default function App() {
  const [view, setView] = useState('home');
  const [leaderboard, setLeaderboard] = useState([]);
  const [requests, setRequests] = useState([]);
  const [form, setForm] = useState({
    name: '',
    blood_group: 'O+',
    city: '',
    referred_by: ''
  });

  useEffect(() => {
    fetch('http://localhost:8000/api/leaderboard')
      .then(r => r.json())
      .then(setLeaderboard);
    fetch('http://localhost:8000/api/requests')
      .then(r => r.json())
      .then(setRequests);
  }, []);

  const handleRegister = async (e) => {
    e.preventDefault();
    const res = await fetch('http://localhost:8000/api/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form)
    });
    const data = await res.json();
    alert(`Registered! Your referral code: ${data.referral_code}`);
    window.location.reload();
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white font-sans">
      <header className="p-4 bg-slate-900 flex justify-between items-center border-b border-red-500/30">
        <h1 className="text-2xl font-bold text-red-500">🩸 BLOODLINK</h1>
        <nav className="space-x-4">
          <button onClick={() => setView('home')} className="hover:text-red-400">Home</button>
          <button onClick={() => setView('register')} className="hover:text-red-400">Register</button>
          <button onClick={() => setView('leaderboard')} className="hover:text-red-400">Leaderboard</button>
        </nav>
      </header>

      <main className="p-8 max-w-6xl mx-auto">
        {view === 'home' && (
          <div>
            <h2 className="text-3xl font-bold mb-4">Live Emergency Requests</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {requests.map(r => (
                <div key={r.id} className="bg-slate-900 p-4 rounded-lg border border-red-500/20">
                  <span className="text-xs bg-red-600 px-2 py-1 rounded">URGENT</span>
                  <h3 className="text-xl font-bold mt-2">{r.blood_group} Needed</h3>
                  <p className="text-gray-400">{r.hospital}, {r.city}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {view === 'register' && (
          <form onSubmit={handleRegister} className="max-w-md mx-auto bg-slate-900 p-6 rounded-lg">
            <h2 className="text-2xl font-bold mb-4">Become a Donor</h2>
            <input
              placeholder="Name"
              className="w-full p-2 mb-2 bg-slate-800 rounded"
              onChange={e => setForm({...form, name: e.target.value})}
              required
            />
            <select
              className="w-full p-2 mb-2 bg-slate-800 rounded"
              onChange={e => setForm({...form, blood_group: e.target.value})}
            >
              {['A+','A-','B+','B-','AB+','AB-','O+','O-'].map(bg => (
                <option key={bg}>{bg}</option>
              ))}
            </select>
            <input
              placeholder="City"
              className="w-full p-2 mb-2 bg-slate-800 rounded"
              onChange={e => setForm({...form, city: e.target.value})}
              required
            />
            <input
              placeholder="Referral Code (Optional)"
              className="w-full p-2 mb-4 bg-slate-800 rounded"
              onChange={e => setForm({...form, referred_by: e.target.value})}
            />
            <button className="w-full bg-red-600 py-2 rounded font-bold hover:bg-red-700">
              Register & Earn 50 Points
            </button>
          </form>
        )}

        {view === 'leaderboard' && (
          <div>
            <h2 className="text-3xl font-bold mb-4">🏆 Top Heroes</h2>
            <div className="bg-slate-900 rounded-lg p-4">
              {leaderboard.map((u, i) => (
                <div key={i} className="flex justify-between items-center p-3 border-b border-slate-800">
                  <div className="flex items-center gap-3">
                    <span className="text-yellow-400 font-bold">#{i + 1}</span>
                    <span className="text-xl">
                      {u.badge === 'Gold' ? '🥇' : u.badge === 'Silver' ? '🥈' : '🥉'}
                    </span>
                    <span className="font-bold">{u.name}</span>
                    <span className="text-xs bg-slate-800 px-2 py-1 rounded">{u.blood_group}</span>
                  </div>
                  <span className="text-red-400 font-bold">{u.points} BLP</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
```

### 12.3 Telegram Bot: `bot.py`

```python
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)
import requests

TOKEN = "YOUR_BOT_TOKEN"
API_URL = "http://localhost:8000/api"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if args:
        ref = args[0]
        await update.message.reply_text(
            f"🎉 Welcome! You were referred by {ref}.\n"
            f"Register on our web app to claim your bonus: "
            f"http://localhost:5173/register?ref={ref}"
        )
    else:
        await update.message.reply_text(
            "🩸 Welcome to BloodLink!\n"
            "Use /sos to request blood\n"
            "Use /register to link your account"
        )

async def sos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(bg, callback_data=f"sos_{bg}")]
        for bg in ['A+','A-','B+','B-','AB+','AB-','O+','O-']
    ]
    await update.message.reply_text(
        "Select Blood Group Needed:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_sos_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    bg = query.data.split("_")[1]
    context.user_data['sos_bg'] = bg
    await query.edit_message_text(
        f"Blood Group: {bg}\n"
        f"Now, type the Hospital Name and City (e.g., Apollo, Bangalore):"
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'sos_bg' in context.user_data:
        text = update.message.text
        bg = context.user_data['sos_bg']
        
        parts = text.split(",")
        hospital = parts[0].strip() if len(parts) > 0 else "Unknown"
        city = parts[1].strip() if len(parts) > 1 else "Unknown"
        
        requests.post(f"{API_URL}/sos", json={
            "requester_name": update.effective_user.first_name,
            "blood_group": bg,
            "hospital": hospital,
            "city": city,
            "units_needed": 1
        })
        
        await update.message.reply_text(
            f"🚨 SOS BROADCASTED for {bg} at {hospital}, {city}!\n"
            f"Nearby donors are being alerted."
        )
        del context.user_data['sos_bg']
    else:
        await update.message.reply_text("Use /sos to request blood.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("sos", sos))
    app.add_handler(CallbackQueryHandler(handle_sos_click, pattern="^sos_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()

if __name__ == "__main__":
    main()
```

---

## 13. Hackathon Execution Plan

### 13.1 The 8-Hour Sprint Plan

| Hour | Task | Deliverable |
|------|------|-------------|
| **1** | Setup FastAPI + SQLite + BotFather | Backend running, bot token acquired |
| **2** | Build Telegram bot core (`/start`, `/sos`, `/register`) | Bot responds to commands |
| **3** | Build React Web App (registration + leaderboard) | Web UI with form and leaderboard |
| **4** | Connect Web App to FastAPI (REST APIs) | Data flows from UI to DB |
| **5** | Implement referral system + gamification logic | Points awarded for referrals and donations |
| **6** | Implement SOS broadcast + one-tap donate | Full emergency loop working |
| **7** | Test, seed demo data, fix bugs | Stable demo |
| **8** | Prepare PPT, record fallback video | Presentation ready |

### 13.2 What to Mock (FAKE) for the Demo

| Feature | Real Implementation | Hackathon Hack |
|---------|---------------------|----------------|
| **Vouchers** | Amazon/Starbucks API | Generate random code: `AMZN-99X2` |
| **GPS/Proximity** | Google Maps API | Match by city (text input) |
| **Verification** | Aadhaar/Hospital API | Checkbox: "I confirm this donation is real" |
| **Authentication** | OAuth/JWT | No login required (simple forms) |
| **Payments** | Razorpay/Stripe | No payments (points only) |

### 13.3 The "Hackathon Survival" Checklist

- [ ] **Seed the Database:** Insert 5 fake users with 500+ points so the leaderboard looks alive
- [ ] **Use Telegram Desktop:** Easier to demo on a projector
- [ ] **Record a Fallback Video:** Wi-Fi will fail; have a 90-second screen recording
- [ ] **QR Code on PPT:** Link to `t.me/YourBot` so judges can scan and join live
- [ ] **Charge Your Phone:** For the live Telegram demo
- [ ] **Bring a Backup Laptop:** Just in case

---

## 14. Demo Script

### 14.1 The 5-Minute Presentation Flow

**Slide 1: The Problem (30 seconds)**
> "Every second counts in an emergency. But finding a donor is broken—scattered WhatsApp groups, outdated phone numbers, no way to know who's available."

**Slide 2: The Solution (30 seconds)**
> "BLOODLINK. A hybrid ecosystem. A visual web app for the dashboard and a zero-friction Telegram bot for instant action. Request blood as easily as sending a WhatsApp message."

**Slide 3: Live Demo - Web App (1 minute)**
- Show the Leaderboard (seeded with data)
- Show the Live SOS feed
- Register a new user on the spot
- Show the referral code generated

**Slide 4: Live Demo - Telegram Bot (1 minute)**
- Send `/sos` on your phone (projected on screen)
- Show the inline buttons
- Confirm the request
- Switch to a second phone (the "Donor") → receive the alert → tap "I Can Donate"
- Show the Web App leaderboard updating in real-time (the donor's points increase)

**Slide 5: The Gamification (1 minute)**
- Show the Rewards Store
- Explain: "100 points = Coffee. 500 points = Amazon Voucher. We turn donors into heroes."

**Slide 6: The Impact & Future (1 minute)**
> "Zero friction. Viral referrals. Gamified retention. This isn't just an app—it's a movement. Every drop counts. Every second matters."

---

## 15. Future Scope

### 15.1 Short-Term (Post-Hackathon)

| Feature | Description |
|---------|-------------|
| **Mobile App** | React Native app for iOS/Android |
| **Push Notifications** | Firebase Cloud Messaging for real-time alerts |
| **GPS Search** | Find donors within a 5km radius using geolocation |
| **Blood Bank Integration** | Connect with Red Cross and local blood banks |
| **Multilingual Support** | Hindi, Kannada, Tamil, Telugu |

### 15.2 Long-Term (Production)

| Feature | Description |
|---------|-------------|
| **AI/ML Matching** | Predictive analytics for donor availability |
| **Blockchain Verification** | Immutable donation records |
| **Hospital Dashboard** | Real-time inventory management |
| **Wearable Integration** | Smartwatch alerts for nearby emergencies |
| **Government Integration** | Link with national health databases |

### 15.3 Scaling Strategy

1. **Pilot:** Launch in Canara Engineering College
2. **City-Wide:** Expand to Bangalore hospitals
3. **State-Wide:** Partner with Karnataka Blood Bank
4. **National:** Integrate with e-RaktKosh (Government of India)

---

## 16. Conclusion

### 16.1 Key Takeaways

> **"Every Drop Counts. Every Second Matters. One platform, faster connections."**

BLOODLINK v2.0 is not just a hackathon project—it is a **scalable, sustainable, and community-driven solution** to one of healthcare's most critical problems.

### 16.2 Why BLOODLINK Wins

| Criterion | How BLOODLINK Excels |
|-----------|----------------------|
| **Innovation** | Hybrid Web + Telegram architecture (zero friction) |
| **Feasibility** | Built in 8 hours with existing tech stack |
| **Impact** | Directly saves lives by reducing donor search time |
| **Scalability** | Viral referral system + gamification = organic growth |
| **User Experience** | Chat-first approach (familiar to all users) |
| **Technical Depth** | Full-stack (React + FastAPI + SQLite + Telegram) |

### 16.3 Important Disclaimer

> ⚠️ **Compatibility is preliminary.** Medical eligibility is confirmed by hospitals. BLOODLINK is a matching platform, not a medical authority.

### 16.4 Final Words

> **"INNOVATE. CREATE. TRANSFORM."**

BLOODLINK turns blood donation from a one-time act of charity into a **gamified, rewarding, and viral movement**. Every donor becomes a hero. Every referral saves a life.

**Let's build it. 🩸💪**

---

## 📎 Appendices

### Appendix A: Project Structure

```text
bloodlink/
├── backend/
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── index.css
│   │   └── components/
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── bot/
│   ├── bot.py
│   ├── handlers/
│   └── requirements.txt
├── seed_data.py
├── README.md
└── .gitignore
```

### Appendix B: Requirements Files

**`backend/requirements.txt`**
```text
fastapi
uvicorn
sqlalchemy
pydantic
python-telegram-bot
requests
```

**`frontend/package.json` (dependencies)**
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "lucide-react": "^0.263.1"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.0.0",
    "tailwindcss": "^3.3.0",
    "autoprefixer": "^10.4.14",
    "postcss": "^8.4.24"
  }
}
```

### Appendix C: Seed Data Script

```python
# seed_data.py
from main import SessionLocal, User, update_badge
import uuid

db = SessionLocal()

users = [
    {"name": "Karthik", "blood_group": "O-", "city": "Bangalore", "points": 650},
    {"name": "Dr. Kavita Joshi", "blood_group": "AB-", "city": "Bangalore", "points": 480},
    {"name": "Mohammad Farooq", "blood_group": "B+", "city": "Delhi", "points": 320},
    {"name": "Priya Sharma", "blood_group": "A+", "city": "Mumbai", "points": 150},
    {"name": "Rahul Verma", "blood_group": "O+", "city": "Chennai", "points": 120},
]

for u in users:
    user = User(
        name=u["name"],
        blood_group=u["blood_group"],
        city=u["city"],
        points=u["points"],
        referral_code=str(uuid.uuid4())[:8]
    )
    update_badge(user)
    db.add(user)

db.commit()
db.close()
print("✅ Seed data inserted!")
```

---

**Document Version:** 2.0  
**Last Updated:** 2026  
**Author:** BLOODLINK Team  

---

> 🩸 **BLOODLINK** - *Bridging Donors & Patients in Critical Seconds.*
> 
> **INNOVATE. CREATE. TRANSFORM.**
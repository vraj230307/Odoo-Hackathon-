# ✈ Traveloop — Personalized Travel Planning Made Easy

> Built for Odoo Hackathon 2026 | Team of 4

Traveloop is a full-stack travel planning platform that lets users create multi-city itineraries, track budgets, discover destinations, manage packing lists, and share trips — all in one place.

---

## 🚀 Live Demo
Run locally at `http://127.0.0.1:5000`

---

## 👥 Team & Modules

| Member | Module |
|--------|--------|
| Member 1 | Auth + Dashboard + Profile |
| Member 2 | Trips + Itinerary |
| Member 3 | City Search + Budget |
| Member 4 | Notes + Packing + Admin |

---

## ✨ Features

- 🔐 Email/password authentication with session management
- 🗺️ Multi-city trip planning with dates and destinations
- 🏙️ Search 35+ cities with filters by region and country
- 🎯 Activity search with category and price filters
- 💰 Budget tracking with expense breakdown
- 📝 Trip notes and journal
- 🎒 Packing checklist with categories
- 📊 Admin analytics dashboard
- 🌐 Public itinerary sharing
- 📱 Fully responsive UI

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, Flask, Flask-CORS |
| Database | SQLite + SQLAlchemy |
| Auth | Werkzeug password hashing |

---

## ⚙️ Setup & Run

```bash
# 1. Clone the repo
git clone https://github.com/vraj230307/Odoo-Hackathon-.git
cd Odoo-Hackathon-

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# 3. Install dependencies
pip install -r backend/requirements.txt

# 4. Setup database
cd backend
python setup_db.py
python -c "
import sqlite3
conn = sqlite3.connect('database.db')
with open('../database/schema.sql', 'r', encoding='utf-8') as f:
    conn.executescript(f.read())
conn.close()
print('Done!')
"

# 5. Run the app
python app.py
```

Open `http://127.0.0.1:5000` in your browser.

---

## 📁 Project Structure

```
traveloop/
├── backend/
│   ├── routes/          # All API blueprints
│   ├── helpers/         # Utility functions
│   ├── app.py           # Flask entry point
│   ├── models.py        # SQLAlchemy models
│   ├── config.py        # App configuration
│   └── setup_db.py      # Database seeder
├── frontend/
│   ├── pages/           # HTML pages
│   ├── css/             # Stylesheets
│   ├── js/              # JavaScript files
│   └── assets/          # Images and icons
└── database/
    └── schema.sql       # Cities & activities schema
```

---

## 🎨 Design System

| Token | Value |
|-------|-------|
| Primary | `#4F46E5` |
| Secondary | `#06B6D4` |
| Background | `#F8FAFC` |
| Surface | `#FFFFFF` |

---

## 📡 API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/register` | Create account |
| POST | `/api/login` | Login |
| POST | `/api/logout` | Logout |

### Trips
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/trips` | Get all trips |
| POST | `/api/trip` | Create trip |
| DELETE | `/api/trip/:id` | Delete trip |

### Search
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/cities` | Search cities |
| GET | `/api/activities` | Search activities |

### Budget
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/expenses` | Get expenses |
| POST | `/api/expenses` | Add expense |
# Traveloop — Odoo Hackathon

Personalized travel planning platform.

## Team Modules
| Member | Module | Branch |
|--------|--------|--------|
| Member 1 | Auth + Dashboard + Profile | `module-auth` |
| Member 2 | Trips + Itinerary | `module-trips` |
| Member 3 | Search + Budget | `module-budget` |
| Member 4 | Notes + Checklist + Admin | `module-productivity` |

## Setup (everyone runs this)
```bash
git clone https://github.com/vraj230307/Odoo-Hackathon-.git
cd Odoo-Hackathon-
python -m venv venv
venv\Scripts\activate
pip install -r backend/requirements.txt
cp .env.example backend/.env
# fill in your Supabase keys in backend/.env
cd backend
python app.py
```

## Colors
- Primary: `#4F46E5`
- Secondary: `#06B6D4`
- Background: `#F8FAFC`

## API Response Format (everyone must follow this)
```json
{ "success": true, "message": "...", "data": [] }
```

## Git Rules
- Never push directly to `main`
- Each member works on their own branch
- Pull before you push every time
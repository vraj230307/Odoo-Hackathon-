# ============================================================
# Seed Script — Populate database with dummy test data
# ============================================================

from app import create_app
from models import db, User, Trip, PackingItem, TripNote, SavedDestination
from werkzeug.security import generate_password_hash


def seed():
    """Drop + recreate tables and insert sample data."""
    app = create_app()

    with app.app_context():
        db.drop_all()
        db.create_all()

        # --- Users ---
        u1 = User(username='johndoe', email='john@example.com',
                   password=generate_password_hash('password123', method='pbkdf2:sha256'))
        u2 = User(username='janedoe', email='jane@example.com',
                   password=generate_password_hash('password123', method='pbkdf2:sha256'))
        u3 = User(username='alice',   email='alice@example.com',
                   password=generate_password_hash('password123', method='pbkdf2:sha256'))
        db.session.add_all([u1, u2, u3])
        db.session.commit()

        # --- Trips ---
        t1 = Trip(user_id=u1.id, destination='Paris, France')
        t2 = Trip(user_id=u1.id, destination='Tokyo, Japan')
        t3 = Trip(user_id=u2.id, destination='New York, USA')
        t4 = Trip(user_id=u3.id, destination='Paris, France')
        db.session.add_all([t1, t2, t3, t4])
        db.session.commit()

        # --- Packing Items ---
        items = [
            PackingItem(user_id=u1.id, trip_id=t1.id, item_name='Passport',  category='Documents'),
            PackingItem(user_id=u1.id, trip_id=t1.id, item_name='Sunscreen', category='Toiletries'),
            PackingItem(user_id=u1.id, trip_id=t1.id, item_name='Camera',    category='Electronics'),
            PackingItem(user_id=u1.id, trip_id=t2.id, item_name='Adapter',   category='Electronics'),
            PackingItem(user_id=u2.id, trip_id=t3.id, item_name='Jacket',    category='Clothing'),
        ]
        db.session.add_all(items)

        # --- Saved Destinations ---
        dests = [
            SavedDestination(user_id=u1.id, city_name='Paris, France'),
            SavedDestination(user_id=u1.id, city_name='Rome, Italy'),
            SavedDestination(user_id=u2.id, city_name='Tokyo, Japan'),
            SavedDestination(user_id=u2.id, city_name='Paris, France'),
            SavedDestination(user_id=u3.id, city_name='Paris, France'),
            SavedDestination(user_id=u3.id, city_name='Barcelona, Spain'),
        ]
        db.session.add_all(dests)

        # --- Trip Notes ---
        notes = [
            TripNote(trip_id=t1.id, note_title='Eiffel Tower Tips',
                     note_content='Book tickets online to skip the queue.'),
            TripNote(trip_id=t1.id, note_title='Cafe Recommendations',
                     note_content='Le Comptoir near Notre Dame is great.'),
            TripNote(trip_id=t2.id, note_title='Sushi Spots',
                     note_content='Tsukiji outer market has the best sushi.'),
            TripNote(trip_id=t3.id, note_title='Broadway Shows',
                     note_content='Get rush tickets for Hamilton!'),
        ]
        db.session.add_all(notes)

        db.session.commit()
        print('Database seeded successfully!')


if __name__ == '__main__':
    seed()

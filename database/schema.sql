-- =====================================================
-- Traveloop Database Schema
-- Member 3 — Search + Budget Module
-- =====================================================

DROP TABLE IF EXISTS expenses;
DROP TABLE IF EXISTS activities;
DROP TABLE IF EXISTS cities;

-- =====================================================
-- CITIES TABLE
-- =====================================================

CREATE TABLE cities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,
    country TEXT NOT NULL,
    region TEXT NOT NULL,

    emoji TEXT DEFAULT '🏙️',

    avg_cost_per_day REAL DEFAULT 5000,

    rating REAL DEFAULT 4.5,

    featured INTEGER DEFAULT 0,

    description TEXT,

    image_url TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- ACTIVITIES TABLE
-- =====================================================

CREATE TABLE activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    city_id INTEGER NOT NULL,

    name TEXT NOT NULL,

    category TEXT NOT NULL,

    cost REAL DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(city_id)
    REFERENCES cities(id)
    ON DELETE CASCADE
);

-- =====================================================
-- EXPENSES TABLE
-- =====================================================

CREATE TABLE expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    trip_id TEXT NOT NULL,

    category TEXT NOT NULL,

    description TEXT NOT NULL,

    amount REAL NOT NULL,

    expense_date DATE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- INDEXES
-- =====================================================

CREATE INDEX idx_city_name ON cities(name);
CREATE INDEX idx_city_country ON cities(country);
CREATE INDEX idx_city_region ON cities(region);

CREATE INDEX idx_activity_city ON activities(city_id);
CREATE INDEX idx_activity_category ON activities(category);

CREATE INDEX idx_expense_trip ON expenses(trip_id);

-- =====================================================
-- CITIES DATA
-- =====================================================

INSERT INTO cities
(name, country, region, image_url)
VALUES

('Varanasi', 'India', 'Asia', 'https://loremflickr.com/800/600/Varanasi%2Ctravel/all'),
('Haridwar', 'India', 'Asia', 'https://loremflickr.com/800/600/Haridwar%2Ctravel/all'),
('Rishikesh', 'India', 'Asia', 'https://loremflickr.com/800/600/Rishikesh%2Ctravel/all'),
('Dwarka', 'India', 'Asia', 'https://loremflickr.com/800/600/Dwarka%2Ctravel/all'),
('Somnath', 'India', 'Asia', 'https://loremflickr.com/800/600/Somnath%2Ctravel/all'),
('Tirupati', 'India', 'Asia', 'https://loremflickr.com/800/600/Tirupati%2Ctravel/all'),
('Goa', 'India', 'Asia', 'https://loremflickr.com/800/600/Goa%2Ctravel/all'),
('Pondicherry', 'India', 'Asia', 'https://loremflickr.com/800/600/Pondicherry%2Ctravel/all'),
('Kovalam', 'India', 'Asia', 'https://loremflickr.com/800/600/Kovalam%2Ctravel/all'),
('Andaman and Nicobar Islands', 'India', 'Asia', 'https://loremflickr.com/800/600/AndamanandNicobarIslands%2Ctravel/all'),
('Manali', 'India', 'Asia', 'https://loremflickr.com/800/600/Manali%2Ctravel/all'),
('Shimla', 'India', 'Asia', 'https://loremflickr.com/800/600/Shimla%2Ctravel/all'),
('Leh', 'India', 'Asia', 'https://loremflickr.com/800/600/Leh%2Ctravel/all'),
('Darjeeling', 'India', 'Asia', 'https://loremflickr.com/800/600/Darjeeling%2Ctravel/all'),
('Nainital', 'India', 'Asia', 'https://loremflickr.com/800/600/Nainital%2Ctravel/all'),
('Jaipur', 'India', 'Asia', 'https://loremflickr.com/800/600/Jaipur%2Ctravel/all'),
('Udaipur', 'India', 'Asia', 'https://loremflickr.com/800/600/Udaipur%2Ctravel/all'),
('Jaisalmer', 'India', 'Asia', 'https://loremflickr.com/800/600/Jaisalmer%2Ctravel/all'),
('Jim Corbett', 'India', 'Asia', 'https://loremflickr.com/800/600/JimCorbett%2Ctravel/all'),
('Kaziranga', 'India', 'Asia', 'https://loremflickr.com/800/600/Kaziranga%2Ctravel/all'),
('Bir Billing', 'India', 'Asia', 'https://loremflickr.com/800/600/BirBilling%2Ctravel/all'),
('Auli', 'India', 'Asia', 'https://loremflickr.com/800/600/Auli%2Ctravel/all'),
('Bali', 'Indonesia', 'Asia', 'https://loremflickr.com/800/600/Bali%2Ctravel/all'),
('Maldives', 'Maldives', 'Asia', 'https://loremflickr.com/800/600/Maldives%2Ctravel/all'),
('Phuket', 'Thailand', 'Asia', 'https://loremflickr.com/800/600/Phuket%2Ctravel/all'),
('Dubai', 'UAE', 'Middle East', 'https://loremflickr.com/800/600/Dubai%2Ctravel/all'),
('Singapore', 'Singapore', 'Asia', 'https://loremflickr.com/800/600/Singapore%2Ctravel/all'),
('Tokyo', 'Japan', 'Asia', 'https://loremflickr.com/800/600/Tokyo%2Ctravel/all'),
('Paris', 'France', 'Europe', 'https://loremflickr.com/800/600/Paris%2Ctravel/all'),
('Swiss Alps', 'Switzerland', 'Europe', 'https://loremflickr.com/800/600/SwissAlps%2Ctravel/all'),
('Rome', 'Italy', 'Europe', 'https://loremflickr.com/800/600/Rome%2Ctravel/all'),
('Las Vegas', 'USA', 'North America', 'https://loremflickr.com/800/600/LasVegas%2Ctravel/all'),
('New York City', 'USA', 'North America', 'https://loremflickr.com/800/600/NewYorkCity%2Ctravel/all'),
('Santorini', 'Greece', 'Europe', 'https://loremflickr.com/800/600/Santorini%2Ctravel/all'),
('Reykjavik', 'Iceland', 'Europe', 'https://loremflickr.com/800/600/Reykjavik%2Ctravel/all');

-- =====================================================
-- ACTIVITIES DATA
-- =====================================================

INSERT INTO activities
(city_id, name, category, cost)
VALUES

(1, 'Ganga Aarti', 'Sightseeing', 38.0),
(1, 'Boat Ride', 'Activity', 16.0),
(1, 'Temple Darshan', 'Sightseeing', 7.0),

(3, 'River Rafting', 'Activity', 33.0),
(3, 'Bungee Jumping', 'Activity', 65.0),

(7, 'Parasailing', 'Activity', 107.0),
(7, 'Scuba Diving', 'Activity', 34.0),
(7, 'Beach Party', 'Nature', 101.0),

(11, 'Skiing', 'Activity', 35.0),
(11, 'Snowboarding', 'Activity', 107.0),

(16, 'Fort Exploration', 'Sightseeing', 18.0),
(16, 'Hot Air Balloon Ride', 'Activity', 90.0),

(17, 'Boat Ride', 'Activity', 90.0),

(18, 'Camel Safari', 'Nature', 77.0),

(19, 'Jungle Safari', 'Nature', 77.0),

(21, 'Paragliding', 'Activity', 136.0),

(22, 'Skiing', 'Activity', 49.0),

(23, 'Surfing', 'Activity', 26.0),
(23, 'ATV Ride', 'Activity', 108.0),

(24, 'Water Villa Stay', 'Activity', 39.0),

(25, 'Island Hopping', 'Activity', 121.0),

(26, 'Desert Safari', 'Nature', 138.0),
(26, 'Skydiving', 'Activity', 55.0),

(27, 'Theme Park Visit', 'Entertainment', 60.0),

(28, 'Anime Shopping', 'Shopping', 145.0),
(28, 'Sushi Tour', 'Food', 10.0),

(29, 'River Cruise', 'Activity', 38.0),

(30, 'Skiing', 'Activity', 71.0),

(31, 'Historical Tour', 'Sightseeing', 146.0),

(32, 'Casino', 'Entertainment', 150.0),

(33, 'Broadway Show', 'Entertainment', 64.0),

(34, 'Sunset Cruise', 'Nature', 105.0),

(35, 'Northern Lights Tour', 'Nature', 40.0);

-- =====================================================
-- SAMPLE EXPENSE DATA
-- =====================================================

INSERT INTO expenses
(trip_id, category, description, amount, expense_date)
VALUES

('TRIP001', '🍜 Food', 'Dinner at restaurant', 1200, '2026-05-01'),
('TRIP001', '🏨 Accommodation', 'Hotel booking', 5000, '2026-05-01'),
('TRIP001', '🚌 Transport', 'Taxi fare', 700, '2026-05-02'),
('TRIP001', '🎭 Activities', 'Museum ticket', 900, '2026-05-02');

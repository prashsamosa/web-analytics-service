# I generated this code with the help of AI.
"""
Sample data generator for the analytics service.
Generates realistic events for testing the API endpoints.
"""

import sys
import os
import json
import random
from datetime import datetime, timedelta
from faker import Faker
import sqlite3
import uuid

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

fake = Faker()


NUM_EVENTS = 3000
NUM_USERS = 50
DATABASE_PATH = "analytics.db"

START_DATE = datetime(2025, 5, 1)
END_DATE = datetime(2025, 5, 29)

SAMPLE_URLS = [
    "https://example.com/",
    "https://example.com/about",
    "https://example.com/products",
    "https://example.com/services",
    "https://example.com/contact",
    "https://example.com/blog",
    "https://example.com/pricing",
    "https://example.com/login",
    "https://example.com/signup",
    "https://example.com/dashboard",
    "https://shop.example.com/",
    "https://shop.example.com/category/electronics",
    "https://shop.example.com/category/clothing",
    "https://blog.example.com/post/1",
    "https://blog.example.com/post/2",
]

SAMPLE_PAGE_TITLES = [
    "Home - Example.com",
    "About Us - Example.com",
    "Our Products - Example.com",
    "Services - Example.com",
    "Contact Us - Example.com",
    "Blog - Example.com",
    "Pricing - Example.com",
    "Login - Example.com",
    "Sign Up - Example.com",
    "Dashboard - Example.com",
    "Shop - Example.com",
    "Electronics - Shop",
    "Clothing - Shop",
    "Latest Tech Trends - Blog",
    "How to Choose Products - Blog",
]

SAMPLE_ELEMENT_IDS = [
    "header-nav",
    "main-cta-button",
    "footer-link",
    "product-card",
    "add-to-cart",
    "learn-more",
    "contact-button",
    "menu-toggle",
    "search-button",
    "newsletter-signup",
    "social-media-link",
    "video-play-button",
    "download-link",
    "share-button",
    "close-modal",
]

SAMPLE_CLICK_TEXTS = [
    "Learn More",
    "Get Started",
    "Contact Us",
    "Add to Cart",
    "Sign Up",
    "Login",
    "Download Now",
    "View Details",
    "Subscribe",
    "Share",
    "Close",
    "Next",
    "Previous",
    "Submit",
    "Cancel",
]

def generate_user_ids(num_users):
    """Generate realistic user IDs"""
    user_ids = []
    for i in range(num_users):

        if random.random() < 0.3:
            user_ids.append(f"user_{fake.uuid4()[:8]}")
        else:
            user_ids.append(f"session_{fake.uuid4()[:12]}")
    return user_ids

def generate_view_event(user_id):
    """Generate a view event"""
    url = random.choice(SAMPLE_URLS)
    title = random.choice(SAMPLE_PAGE_TITLES)

    payload = {"url": url}
    if random.random() < 0.8:
        payload["title"] = title

    return {
        "user_id": user_id,
        "event_type": "view",
        "payload": json.dumps(payload)
    }

def generate_click_event(user_id):
    """Generate a click event"""
    payload = {}

    if random.random() < 0.7:
        payload["element_id"] = random.choice(SAMPLE_ELEMENT_IDS)

    if random.random() < 0.6:
        payload["text"] = random.choice(SAMPLE_CLICK_TEXTS)

    if random.random() < 0.4:
        payload["xpath"] = f"//div[@id='{random.choice(SAMPLE_ELEMENT_IDS)}']"

    return {
        "user_id": user_id,
        "event_type": "click",
        "payload": json.dumps(payload)
    }

def generate_location_event(user_id):
    """Generate a location event"""

    city_coords = [
        (40.7128, -74.0060),  # New York
        (51.5074, -0.1278),   # London
        (35.6762, 139.6503),  # Tokyo
        (48.8566, 2.3522),    # Paris
        (37.7749, -122.4194), # San Francisco
        (55.7558, 37.6176),   # Moscow
        (28.6139, 77.2090),   # Delhi
        (-33.8688, 151.2093), # Sydney
        (39.9042, 116.4074),  # Beijing
        (25.2048, 55.2708),   # Dubai
    ]

    base_lat, base_lng = random.choice(city_coords)


    lat_offset = random.uniform(-0.1, 0.1)
    lng_offset = random.uniform(-0.1, 0.1)

    latitude = round(base_lat + lat_offset, 6)
    longitude = round(base_lng + lng_offset, 6)

    payload = {
        "latitude": latitude,
        "longitude": longitude
    }

    if random.random() < 0.7:  # 70% chance to include accuracy
        payload["accuracy"] = round(random.uniform(5.0, 100.0), 1)

    return {
        "user_id": user_id,
        "event_type": "location",
        "payload": json.dumps(payload)
    }

def generate_random_timestamp():
    """Generate a random timestamp between START_DATE and END_DATE"""
    time_delta = END_DATE - START_DATE
    random_days = random.uniform(0, time_delta.total_seconds())
    return START_DATE + timedelta(seconds=random_days)

def generate_events(num_events, user_ids):
    """Generate all events"""
    events = []


    event_types = ['view'] * 60 + ['click'] * 30 + ['location'] * 10

    for i in range(num_events):
        user_id = random.choice(user_ids)
        event_type = random.choice(event_types)
        timestamp = generate_random_timestamp()

        if event_type == 'view':
            event_data = generate_view_event(user_id)
        elif event_type == 'click':
            event_data = generate_click_event(user_id)
        else:  # location
            event_data = generate_location_event(user_id)

        event = {
            "event_id": str(uuid.uuid4()),
            "user_id": event_data["user_id"],
            "event_type": event_data["event_type"],
            "timestamp": timestamp.isoformat(),
            "payload": event_data["payload"]
        }

        events.append(event)

        if (i + 1) % 500 == 0:
            print(f"Generated {i + 1}/{num_events} events...")

    return events

def create_database_schema():
    """Create the database schema if it doesn't exist"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()


    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            event_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            event_type TEXT NOT NULL CHECK (event_type IN ('view', 'click', 'location')),
            timestamp TIMESTAMP NOT NULL,
            payload TEXT NOT NULL
        )
    ''')


    cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_user_id ON events(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_event_type ON events(event_type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_composite ON events(event_type, timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_user_time ON events(user_id, timestamp)')

    conn.commit()
    conn.close()
    print("Database schema created successfully!")

def insert_events_to_database(events):
    """Insert events into the SQLite database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()


    cursor.execute('DELETE FROM events')
    print("Cleared existing events from database")


    for event in events:
        cursor.execute('''
            INSERT INTO events (event_id, user_id, event_type, timestamp, payload)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            event['event_id'],
            event['user_id'],
            event['event_type'],
            event['timestamp'],
            event['payload']
        ))

    conn.commit()
    conn.close()
    print(f"Inserted {len(events)} events into database!")

def verify_data():
    """Verify the generated data"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()


    cursor.execute('SELECT COUNT(*) FROM events')
    total_count = cursor.fetchone()[0]
    print(f"\nTotal events in database: {total_count}")


    cursor.execute('''
        SELECT event_type, COUNT(*)
        FROM events
        GROUP BY event_type
        ORDER BY event_type
    ''')

    print("\nEvents by type:")
    for event_type, count in cursor.fetchall():
        print(f"  {event_type}: {count}")


    cursor.execute('SELECT MIN(timestamp), MAX(timestamp) FROM events')
    min_date, max_date = cursor.fetchone()
    print(f"\nDate range: {min_date} to {max_date}")


    cursor.execute('SELECT COUNT(DISTINCT user_id) FROM events')
    unique_users = cursor.fetchone()[0]
    print(f"Unique users: {unique_users}")


    cursor.execute('SELECT * FROM events LIMIT 3')
    print("\nSample events:")
    for row in cursor.fetchall():
        event_id, user_id, event_type, timestamp, payload = row
        print(f"  {event_type} | {user_id} | {timestamp} | {payload[:50]}...")

    conn.close()

def main():
    """Main function to generate sample data"""
    print("Starting Analytics Data Generation")
    print(f"Generating {NUM_EVENTS} events for {NUM_USERS} users...")
    print(f"Date range: {START_DATE.date()} to {END_DATE.date()}")
    print(f"Database: {DATABASE_PATH}")
    print("-" * 50)

    try:

        print("1. Creating database schema...")
        create_database_schema()


        print("2. Generating user IDs...")
        user_ids = generate_user_ids(NUM_USERS)


        print("3. Generating events...")
        events = generate_events(NUM_EVENTS, user_ids)


        print("4. Inserting events into database...")
        insert_events_to_database(events)


        print("5. Verifying generated data...")
        verify_data()

        print("\n Data generation completed successfully!")
        print("\n Next steps:")
        print("  1. Start the FastAPI server: uvicorn app.main:app --reload")
        print("  2. Visit http://localhost:8000/docs to explore the API")
        print("  3. Test the endpoints with the generated data")

    except Exception as e:
        print(f"\n❌ Error during data generation: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

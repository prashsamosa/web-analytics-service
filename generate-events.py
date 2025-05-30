import json
import random
from datetime import datetime, timezone, timedelta
from faker import Faker
from sqlalchemy.orm import sessionmaker
from database import engine, Event, create_tables

fake = Faker()

# Create session
SessionLocal = sessionmaker(bind=engine)

def generate_view_payload():
    """Generate realistic view event payload"""
    urls = [
        "/home", "/about", "/products", "/contact", "/blog", "/services",
        "/pricing", "/features", "/documentation", "/support", "/login",
        "/dashboard", "/profile", "/settings", "/help", "/faq"
    ]

    titles = [
        "Home - Analytics Service", "About Us", "Our Products", "Contact Us",
        "Blog - Latest Updates", "Our Services", "Pricing Plans", "Key Features",
        "Documentation", "Support Center", "Login", "Dashboard", "User Profile",
        "Settings", "Help Center", "Frequently Asked Questions"
    ]

    url = random.choice(urls)
    title = random.choice(titles)

    return {
        "url": f"https://example.com{url}",
        "title": title
    }

def generate_click_payload():
    """Generate realistic click event payload"""
    element_ids = [
        "submit-btn", "nav-home", "nav-about", "cta-button", "download-btn",
        "signup-btn", "login-btn", "menu-toggle", "search-btn", "filter-btn",
        "sort-btn", "back-btn", "next-btn", "prev-btn", "close-btn"
    ]

    texts = [
        "Submit", "Home", "About", "Get Started", "Download Now",
        "Sign Up", "Log In", "Menu", "Search", "Filter",
        "Sort", "Back", "Next", "Previous", "Close"
    ]

    xpaths = [
        "//button[@id='submit-btn']", "//a[@class='nav-link']", "//div[@class='cta-button']",
        "//button[@class='btn-primary']", "//a[@href='/download']", "//form//button",
        "//nav//a", "//header//button", "//main//button", "//footer//a"
    ]

    payload = {}

    if random.random() > 0.3:  # 70% chance to have element_id
        payload["element_id"] = random.choice(element_ids)

    if random.random() > 0.2:  # 80% chance to have text
        payload["text"] = random.choice(texts)

    if random.random() > 0.5:  # 50% chance to have xpath
        payload["xpath"] = random.choice(xpaths)

    return payload

def generate_location_payload():
    """Generate realistic location event payload"""
    # Focus on major cities coordinates
    cities = [
        {"lat": 40.7128, "lon": -74.0060, "name": "New York"},
        {"lat": 34.0522, "lon": -118.2437, "name": "Los Angeles"},
        {"lat": 41.8781, "lon": -87.6298, "name": "Chicago"},
        {"lat": 29.7604, "lon": -95.3698, "name": "Houston"},
        {"lat": 39.9526, "lon": -75.1652, "name": "Philadelphia"},
        {"lat": 33.4484, "lon": -112.0740, "name": "Phoenix"},
        {"lat": 32.7767, "lon": -96.7970, "name": "Dallas"},
        {"lat": 37.7749, "lon": -122.4194, "name": "San Francisco"},
        {"lat": 47.6062, "lon": -122.3321, "name": "Seattle"},
        {"lat": 25.7617, "lon": -80.1918, "name": "Miami"}
    ]

    city = random.choice(cities)

    # Add some random variation to coordinates
    lat_variation = random.uniform(-0.1, 0.1)
    lon_variation = random.uniform(-0.1, 0.1)

    payload = {
        "latitude": round(city["lat"] + lat_variation, 6),
        "longitude": round(city["lon"] + lon_variation, 6)
    }

    if random.random() > 0.3:  # 70% chance to have accuracy
        payload["accuracy"] = round(random.uniform(5.0, 100.0), 2)

    return payload

def generate_events(num_events=3000):
    """Generate sample events and insert into database"""
    create_tables()

    session = SessionLocal()

    try:
        print(f"Generating {num_events} sample events...")

        # Generate user IDs
        user_ids = [f"user_{i:04d}" for i in range(1, 201)]  # 200 unique users
        session_ids = [f"session_{fake.uuid4()[:8]}" for _ in range(500)]  # 500 sessions
        all_user_ids = user_ids + session_ids

        # Event type distribution
        event_types = ["view", "click", "location"]
        event_weights = [0.6, 0.3, 0.1]  # 60% views, 30% clicks, 10% location

        # Time range: May 1, 2025 to May 29, 2025
        start_date = datetime(2025, 5, 1, tzinfo=timezone.utc)
        end_date = datetime(2025, 5, 29, tzinfo=timezone.utc)
        time_diff = end_date - start_date

        events_to_insert = []

        for i in range(num_events):
            # Random timestamp within the range
            random_seconds = random.randint(0, int(time_diff.total_seconds()))
            timestamp = start_date + timedelta(seconds=random_seconds)

            # Select event type based on weights
            event_type = random.choices(event_types, weights=event_weights)[0]

            # Generate payload based on event type
            if event_type == "view":
                payload = generate_view_payload()
            elif event_type == "click":
                payload = generate_click_payload()
            else:  # location
                payload = generate_location_payload()

            # Create event
            event = Event(
                user_id=random.choice(all_user_ids),
                event_type=event_type,
                timestamp=timestamp,
                payload=json.dumps(payload)
            )

            events_to_insert.append(event)

            # Batch insert every 100 events
            if len(events_to_insert) >= 100:
                session.add_all(events_to_insert)
                session.commit()
                events_to_insert = []
                print(f"Inserted {i + 1}/{num_events} events...")

        # Insert remaining events
        if events_to_insert:
            session.add_all(events_to_insert)
            session.commit()

        print(f"Successfully generated and inserted {num_events} events!")

        # Print some statistics
        view_count = session.query(Event).filter(Event.event_type == "view").count()
        click_count = session.query(Event).filter(Event.event_type == "click").count()
        location_count = session.query(Event).filter(Event.event_type == "location").count()

        print(f"\nEvent Statistics:")
        print(f"View events: {view_count}")
        print(f"Click events: {click_count}")
        print(f"Location events: {location_count}")
        print(f"Total events: {view_count + click_count + location_count}")

    except Exception as e:
        session.rollback()
        print(f"Error generating events: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    generate_events(3000)  # Generate 3000 events

"""Seed script for Azzurro Hotels Review Insights Dashboard.

Seeds the 4 hotel properties and ~100 realistic, fictional demo reviews covering all 8 operational topics.
Idempotent: safe to run multiple times without duplicating data.
Also exports the reviews to data/sample_reviews.csv.
"""

import os
import sys
from datetime import date, timedelta
import csv

# Add backend directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.database import SessionLocal, engine
from app.models.property import Property
from app.models.review import Review
from app.services.ingestion_service import IngestionService


PROPERTIES_DATA = [
    {
        "id": 1,
        "name": "Olympic Hotel Paddington",
        "booking_url": "https://www.booking.com/hotel/au/olympic-paddington.html",
        "location": "Paddington, Sydney, Australia",
    },
    {
        "id": 2,
        "name": "Potts Point",
        "booking_url": "https://www.booking.com/hotel/au/venus-potts-point-sydney.html",
        "location": "Potts Point, Sydney, Australia",
    },
    {
        "id": 3,
        "name": "Central Sydney",
        "booking_url": "https://www.booking.com/hotel/au/venus-surry-hills.html",
        "location": "Surry Hills, Sydney, Australia",
    },
    {
        "id": 4,
        "name": "Darling Harbour",
        "booking_url": "https://www.booking.com/hotel/au/chateau-de-venus.html",
        "location": "Darling Harbour, Sydney, Australia",
    },
]

# Base date for relative date calculations (current date is ~Nov 24, 2026)
BASE_DATE = date(2026, 11, 24)

# Carefully engineered review templates covering all 8 operational topics
SAMPLE_REVIEWS_TEMPLATE = [
    # Cleanliness issues & praises
    {
        "prop": "Olympic Hotel Paddington",
        "title": "[DEMO] Dirty bathroom and dusty linen",
        "pos": "The historic building architecture was quite charming.",
        "neg": "Housekeeping was disappointing. Dirty bathroom tiles with visible mold, dusty surfaces, and stained bedsheets.",
        "rating": 3.5,
        "days_ago": 1,
        "country": "Australia",
        "traveler": "Couple",
        "room": "Standard Queen",
    },
    {
        "prop": "Olympic Hotel Paddington",
        "title": "[DEMO] Impeccably clean and neat room",
        "pos": "The room was spotless and clean. Fresh towels daily and the housekeeping team did a wonderful job.",
        "neg": "A bit of street noise from Oxford Street at night.",
        "rating": 8.5,
        "days_ago": 9,
        "country": "New Zealand",
        "traveler": "Solo traveler",
        "room": "Deluxe Queen",
    },
    {
        "prop": "Potts Point",
        "title": "[DEMO] Unhygienic carpet and odor in room",
        "neg": "Unpleasant smell in the corridor. Dusty furniture and the carpet had unhygienic stains.",
        "pos": "Friendly receptionist at the desk.",
        "rating": 4.0,
        "days_ago": 2,
        "country": "United Kingdom",
        "traveler": "Business traveler",
        "room": "Studio Apartment",
    },
    {
        "prop": "Darling Harbour",
        "title": "[DEMO] Clean, modern and spacious suite",
        "pos": "Extremely clean room with pristine bathroom, spotless sheets, and fresh towels provided each morning.",
        "neg": "None whatsoever, had a lovely stay.",
        "rating": 9.5,
        "days_ago": 3,
        "country": "United States",
        "traveler": "Family",
        "room": "Harbour View Suite",
    },

    # Check-in experience
    {
        "prop": "Central Sydney",
        "title": "[DEMO] Lengthy wait during check-in process",
        "neg": "Waited over 45 minutes in a long queue at the front desk reception. The keycard system was down and check-in was chaotic.",
        "pos": "Location near Central Station was unbeatable for train connections.",
        "rating": 4.5,
        "days_ago": 2,
        "country": "Singapore",
        "traveler": "Solo traveler",
        "room": "Compact King",
    },
    {
        "prop": "Central Sydney",
        "title": "[DEMO] Seamless early check-in and friendly greeting",
        "pos": "Check-in was quick and effortless. They accommodated early arrival without any extra fee and handed keys immediately.",
        "neg": "Room was slightly small, but comfortable.",
        "rating": 9.0,
        "days_ago": 11,
        "country": "Australia",
        "traveler": "Couple",
        "room": "Standard King",
    },
    {
        "prop": "Darling Harbour",
        "title": "[DEMO] Frustrating check-in delays with keys",
        "neg": "Receptionist gave us keys that didn't work twice. Had to walk back down to reception with heavy bags. Slow check-in queue.",
        "pos": "The view over the harbour was beautiful once inside.",
        "rating": 5.0,
        "days_ago": 4,
        "country": "Canada",
        "traveler": "Family",
        "room": "Two Bedroom Suite",
    },

    # Staff and receptionist behaviour
    {
        "prop": "Potts Point",
        "title": "[DEMO] Incompetent and rude staff at front desk",
        "neg": "Rude and dismissive receptionist when we asked for luggage assistance. Unprofessional attitude from the morning staff.",
        "pos": "Close to trendy cafes in Potts Point.",
        "rating": 3.0,
        "days_ago": 1,
        "country": "Australia",
        "traveler": "Couple",
        "room": "Deluxe Double",
    },
    {
        "prop": "Potts Point",
        "title": "[DEMO] Wonderfully welcoming and helpful staff",
        "pos": "The receptionist Sarah was incredibly friendly, helpful with local dinner recommendations, and truly polite.",
        "neg": "Lift was slightly slow during morning checkout peak.",
        "rating": 9.0,
        "days_ago": 10,
        "country": "Germany",
        "traveler": "Solo traveler",
        "room": "Standard Double",
    },
    {
        "prop": "Olympic Hotel Paddington",
        "title": "[DEMO] Attentive customer service and friendly smiles",
        "pos": "Staff were very welcoming and hospitable. Any question we had was answered with a smile and genuine kindness.",
        "neg": "Rooms are a little dated.",
        "rating": 8.0,
        "days_ago": 5,
        "country": "United Kingdom",
        "traveler": "Group",
        "room": "Superior Twin",
    },

    # Noise
    {
        "prop": "Olympic Hotel Paddington",
        "title": "[DEMO] Loud street noise and poor soundproofing",
        "neg": "Extremely noisy all night! Thin walls allowed us to hear neighbours talking, and traffic noise from Oxford Street was constant.",
        "pos": "Good cafes nearby in Paddington.",
        "rating": 4.0,
        "days_ago": 3,
        "country": "Australia",
        "traveler": "Solo traveler",
        "room": "Standard Single",
    },
    {
        "prop": "Central Sydney",
        "title": "[DEMO] Construction disturbance early morning",
        "neg": "Loud drilling and construction noise started at 6:30 AM right outside our window. No soundproofing at all.",
        "pos": "Bed was comfortable enough.",
        "rating": 4.5,
        "days_ago": 4,
        "country": "United States",
        "traveler": "Business traveler",
        "room": "Executive Queen",
    },
    {
        "prop": "Darling Harbour",
        "title": "[DEMO] Quiet and peaceful stay despite central location",
        "pos": "Remarkably quiet room with excellent double glazed windows. Didn't hear a peep from street traffic or neighbours.",
        "neg": "Wi-Fi dropped out once.",
        "rating": 8.8,
        "days_ago": 8,
        "country": "Japan",
        "traveler": "Couple",
        "room": "Deluxe King",
    },

    # Facilities
    {
        "prop": "Darling Harbour",
        "title": "[DEMO] Broken air conditioning during humid weekend",
        "neg": "The air conditioning was broken and only blew lukewarm air. Maintenance took hours to inspect it. Gym equipment was dated.",
        "pos": "Great swimming pool and prime location near the harbour.",
        "rating": 5.0,
        "days_ago": 2,
        "country": "Australia",
        "traveler": "Family",
        "room": "Family Suite",
    },
    {
        "prop": "Central Sydney",
        "title": "[DEMO] Fast wifi and reliable amenities",
        "pos": "Strong and fast wifi internet throughout the hotel. The kettle, fridge, and air conditioning worked flawlessly.",
        "neg": "Bathroom was somewhat compact.",
        "rating": 8.7,
        "days_ago": 6,
        "country": "South Korea",
        "traveler": "Solo traveler",
        "room": "Queen Room",
    },
    {
        "prop": "Potts Point",
        "title": "[DEMO] Elevator out of service",
        "neg": "The elevator was out of order for 2 days. Had to carry three heavy suitcases up four flights of stairs.",
        "pos": "Quiet residential street.",
        "rating": 3.8,
        "days_ago": 5,
        "country": "France",
        "traveler": "Couple",
        "room": "Deluxe Apartment",
    },

    # Location
    {
        "prop": "Central Sydney",
        "title": "[DEMO] Perfect location right near Central Station",
        "pos": "Outstanding location! Just a 3 minute walk to Central train station and light rail. Great restaurants in Surry Hills nearby.",
        "neg": "Nothing major, street can be busy.",
        "rating": 9.2,
        "days_ago": 7,
        "country": "Ireland",
        "traveler": "Couple",
        "room": "King Suite",
    },
    {
        "prop": "Olympic Hotel Paddington",
        "title": "[DEMO] Fantastic walkable location in Paddington",
        "pos": "Convenient walking distance to boutique shops, Allianz Stadium, and bus transport directly into Sydney CBD.",
        "neg": "Parking is difficult to find nearby.",
        "rating": 8.5,
        "days_ago": 12,
        "country": "Australia",
        "traveler": "Group",
        "room": "Classic Queen",
    },
    {
        "prop": "Darling Harbour",
        "title": "[DEMO] Inconvenient walk with luggage from transit",
        "neg": "Distance from the nearest train station was further than expected with heavy bags uphill.",
        "pos": "Nice harbour views from the room terrace.",
        "rating": 6.0,
        "days_ago": 13,
        "country": "Netherlands",
        "traveler": "Solo traveler",
        "room": "Superior King",
    },

    # Room condition
    {
        "prop": "Potts Point",
        "title": "[DEMO] Damaged furniture and low water pressure in shower",
        "neg": "Worn and damaged furniture in the room. The bathroom shower had terrible weak water pressure and toilet handle was loose.",
        "pos": "Comfortable bed mattress.",
        "rating": 4.2,
        "days_ago": 3,
        "country": "Australia",
        "traveler": "Solo traveler",
        "room": "Studio Room",
    },
    {
        "prop": "Olympic Hotel Paddington",
        "title": "[DEMO] Cramped room with plumbing leak",
        "neg": "Very cramped small room. Water leak underneath the bathroom sink created a puddle. Maintenance was slow.",
        "pos": "Pub downstairs had great food.",
        "rating": 4.0,
        "days_ago": 4,
        "country": "Australia",
        "traveler": "Couple",
        "room": "Standard Double",
    },
    {
        "prop": "Central Sydney",
        "title": "[DEMO] Modern, newly renovated bathroom and room",
        "pos": "Beautiful modern renovation! The bed was exceptionally comfortable, spacious shower with strong hot water pressure.",
        "neg": "Check-in line was slightly slow.",
        "rating": 9.1,
        "days_ago": 14,
        "country": "United States",
        "traveler": "Business traveler",
        "room": "Deluxe King",
    },

    # Value for money
    {
        "prop": "Darling Harbour",
        "title": "[DEMO] Overpriced for the standard provided",
        "neg": "Far too expensive for what you receive. Overpriced room rates, costly breakfast, and unexpected parking charges.",
        "pos": "Decent location near ICC Sydney.",
        "rating": 4.8,
        "days_ago": 3,
        "country": "Australia",
        "traveler": "Business traveler",
        "room": "Executive Suite",
    },
    {
        "prop": "Central Sydney",
        "title": "[DEMO] Great value for money in prime location",
        "pos": "Very affordable and economical given the central Sydney location. Worth every dollar spent.",
        "neg": "Elevator was a little cramped.",
        "rating": 8.9,
        "days_ago": 15,
        "country": "India",
        "traveler": "Family",
        "room": "Family Room",
    },
    {
        "prop": "Potts Point",
        "title": "[DEMO] Poor value, not worth the expensive price",
        "neg": "Felt like a rip off. Paid premium weekend rates for an outdated room with peeling wallpaper.",
        "pos": "Good cafes nearby.",
        "rating": 4.0,
        "days_ago": 5,
        "country": "United Kingdom",
        "traveler": "Couple",
        "room": "Classic Double",
    },
]


def expand_dataset(base_templates: list[dict], target_count: int = 100) -> list[dict]:
    """Generates ~100 realistic reviews by permuting dates, traveler types, countries, and rooms."""
    expanded = []
    countries = [
        "Australia", "United Kingdom", "United States", "New Zealand",
        "Germany", "Singapore", "Canada", "Japan", "France", "China", "Ireland"
    ]
    traveler_types = ["Couple", "Solo traveler", "Family", "Business traveler", "Group of friends"]
    room_types = [
        "Deluxe King Room", "Standard Queen Room", "Studio Apartment",
        "Executive Suite", "Superior Twin Room", "Family Room"
    ]

    idx = 1
    # First add all templates
    for item in base_templates:
        rev_date = BASE_DATE - timedelta(days=item["days_ago"])
        stay_date = rev_date - timedelta(days=2)
        expanded.append({
            "external_id": f"DEMO-REV-{idx:04d}",
            "property_name": item["prop"],
            "title": item["title"],
            "positive_text": item.get("pos"),
            "negative_text": item.get("neg"),
            "rating": item["rating"],
            "review_date": rev_date.isoformat(),
            "stay_date": stay_date.isoformat(),
            "reviewer_country": item.get("country", countries[idx % len(countries)]),
            "traveler_type": item.get("traveler", traveler_types[idx % len(traveler_types)]),
            "room_type": item.get("room", room_types[idx % len(room_types)]),
            "language": "en",
            "is_demo": True,
        })
        idx += 1

    # Now generate variations across properties and past weeks (up to 40 days ago)
    import copy
    import random
    rng = random.Random(42)  # Deterministic seed for reproducible data

    properties_list = [p["name"] for p in PROPERTIES_DATA]

    while len(expanded) < target_count:
        template = rng.choice(base_templates)
        prop = rng.choice(properties_list)
        # Spread across past 35 days (covers current week, prev week, and 4 weeks prior)
        days_ago = rng.randint(0, 35)
        rev_date = BASE_DATE - timedelta(days=days_ago)
        stay_date = rev_date - timedelta(days=rng.randint(1, 4))

        # Add slight rating variation (+/- 0.5) within [1.0, 10.0]
        rating_jitter = round(rng.choice([-0.5, 0.0, 0.5]), 1)
        adjusted_rating = max(1.0, min(10.0, template["rating"] + rating_jitter))

        expanded.append({
            "external_id": f"DEMO-REV-{idx:04d}",
            "property_name": prop,
            "title": template["title"],
            "positive_text": template.get("pos"),
            "negative_text": template.get("neg"),
            "rating": adjusted_rating,
            "review_date": rev_date.isoformat(),
            "stay_date": stay_date.isoformat(),
            "reviewer_country": rng.choice(countries),
            "traveler_type": rng.choice(traveler_types),
            "room_type": rng.choice(room_types),
            "language": "en",
            "is_demo": True,
        })
        idx += 1

    return expanded


def seed_database():
    db = SessionLocal()
    try:
        print("1. Seeding Properties...")
        for prop_data in PROPERTIES_DATA:
            existing = db.query(Property).filter(Property.name == prop_data["name"]).first()
            if not existing:
                p = Property(
                    id=prop_data["id"],
                    name=prop_data["name"],
                    booking_url=prop_data["booking_url"],
                    location=prop_data["location"],
                )
                db.add(p)
                db.commit()
                print(f"  + Added property: {p.name}")
            else:
                print(f"  - Property already exists: {existing.name}")

        print("\n2. Generating realistic demo reviews (~100 reviews)...")
        reviews_data = expand_dataset(SAMPLE_REVIEWS_TEMPLATE, target_count=105)

        # Export to data/sample_reviews.csv
        data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
        os.makedirs(data_dir, exist_ok=True)
        csv_path = os.path.join(data_dir, "sample_reviews.csv")

        keys = [
            "property_name", "external_id", "title", "positive_text", "negative_text",
            "rating", "review_date", "stay_date", "reviewer_country", "traveler_type",
            "room_type", "language", "is_demo"
        ]
        with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for r in reviews_data:
                writer.writerow(r)
        print(f"  Saved demo dataset to: {csv_path}")

        print("\n3. Ingesting reviews via IngestionService...")
        service = IngestionService(db)
        log = service.ingest_records(
            raw_records=reviews_data,
            source_name="demo_seed:sample_reviews.csv",
            is_demo=True,
        )
        print(f"  Ingestion finished. Status: {log.status}")
        print(f"  Processed: {log.records_processed}, Added: {log.records_added}, Skipped: {log.records_skipped}")

        # Summary of database counts
        total_props = db.query(Property).count()
        total_revs = db.query(Review).count()
        demo_revs = db.query(Review).filter(Review.is_demo == True).count()
        print(f"\nSeeding Complete! Total Properties: {total_props}, Total Reviews: {total_revs} (Demo: {demo_revs})")

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

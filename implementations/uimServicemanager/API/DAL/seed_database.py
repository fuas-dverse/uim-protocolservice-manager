"""
Unified Database Seeding Script - FIXED for UIM Format

Seeds both services and intents from a single JSON file.
Works with UIM-compliant structure (intent_name, http_method, etc.)

Usage:
    python seed_database.py
"""
import sys
import json
from pathlib import Path
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

# Add parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

from DBconnection import GetDBConnection

# Get database connection
db = GetDBConnection()
services_collection = db["services"]
intents_collection = db["intents"]


def clear_database():
    """Clear all services and intents from database"""
    print("\n⚠️  Clearing database...")

    services_deleted = services_collection.delete_many({})
    intents_deleted = intents_collection.delete_many({})

    print(f"   Deleted {services_deleted.deleted_count} services")
    print(f"   Deleted {intents_deleted.deleted_count} intents\n")


def seed_database(seed_file: str = "seed_data.json"):
    """
    Seed the database with services and intents from JSON file.

    Args:
        seed_file: Path to JSON file containing service definitions
    """
    print("=" * 70)
    print("🌱 DVerse Service Catalogue - Database Seeding")
    print("=" * 70)

    # Load seed data
    seed_path = Path(__file__).parent / seed_file

    if not seed_path.exists():
        print(f"❌ Error: Seed file not found: {seed_path}")
        return

    print(f"\n📂 Loading seed data from: {seed_file}")

    try:
        with open(seed_path, 'r', encoding='utf-8') as f:
            seed_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in seed file: {e}")
        return

    services_data = seed_data.get("services", [])

    if not services_data:
        print("❌ Error: No services found in seed file")
        return

    print(f"   Found {len(services_data)} services to seed\n")

    # Process each service
    total_intents = 0
    failed_services = 0
    failed_intents = 0

    for idx, service_data in enumerate(services_data, 1):
        service_name = service_data.get("name", f"Service {idx}")
        print(f"\n{'─' * 70}")
        print(f"📦 Processing Service {idx}/{len(services_data)}: {service_name}")
        print(f"{'─' * 70}")

        # Extract intents from service
        intents_data = service_data.pop("intents", [])

        print(f"   ✓ Service: {service_name}")
        print(f"   ✓ URL: {service_data.get('service_url', 'N/A')}")
        print(f"   ✓ Intents: {len(intents_data)}")

        # Insert intents first and collect their IDs
        intent_ids = []

        for intent_data in intents_data:
            intent_name = intent_data.get("intent_name", "unknown")

            # Add timestamp
            intent_data["created_at"] = datetime.utcnow()
            intent_data["updated_at"] = datetime.utcnow()

            try:
                # Insert intent directly (bypass validation for now)
                result = intents_collection.insert_one(intent_data)
                intent_ids.append(str(result.inserted_id))

                print(f"      └─ Intent: {intent_name}")
                print(f"         • UID: {intent_data.get('intent_uid', 'N/A')}")
                print(f"         • Method: {intent_data.get('http_method', 'POST')} {intent_data.get('endpoint_path', '/')}")
                print(f"         • Parameters: {len(intent_data.get('input_parameters', []))}")

                total_intents += 1
            except Exception as e:
                failed_intents += 1
                print(f"      ✗ Failed to create intent {intent_name}: {e}")

        # Add intent_ids to service
        service_data["intent_ids"] = intent_ids

        # Add timestamps
        service_data["created_at"] = datetime.utcnow()
        service_data["updated_at"] = datetime.utcnow()

        try:
            # Insert service directly
            service_result = services_collection.insert_one(service_data)
            print(f"\n   ✅ Service inserted with ID: {service_result.inserted_id}")
        except Exception as e:
            failed_services += 1
            print(f"\n   ❌ Failed to insert service: {e}")

    # Summary
    print(f"\n{'=' * 70}")
    print("✨ Seeding Complete!")
    print(f"{'=' * 70}")
    print(f"   📦 Services seeded: {len(services_data) - failed_services}")
    print(f"   ❌ Services failed: {failed_services}")
    print(f"   🎯 Intents seeded:  {total_intents}")
    print(f"   ❌ Intents failed:  {failed_intents}")
    print(f"{'=' * 70}\n")

    # Verify
    print("🔍 Verification:")
    print(f"   Services in DB: {services_collection.count_documents({})}")
    print(f"   Intents in DB:  {intents_collection.count_documents({})}")
    print()


if __name__ == "__main__":
    # Ask user if they want to clear existing data
    print("\n⚠️  This will clear existing services and intents!")
    response = input("Continue? (y/n): ")

    if response.lower() == 'y':
        clear_database()
        seed_database("seed_data.json")
    else:
        print("❌ Seeding cancelled")
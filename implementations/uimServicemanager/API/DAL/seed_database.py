"""
Database Seeding Script
This script loads mock data from seed_data.json and populates the MongoDB database
using the existing DAL layer for proper validation and relationship handling.

Usage:
    python DAL/seed_database.py  (from API directory)
    or
    python seed_database.py (from DAL directory)
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path so we can import from DAL and logicLayer
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

# Import your DAL and Logic layers
from DAL.serviceDAL import ServiceDAL
from DAL.intentDAL import IntentDAL
from logicLayer.Logic.serviceLogic import ServiceLogic
from logicLayer.Logic.intentLogic import IntentLogic



class DatabaseSeeder:
    """Handles seeding the database with mock data"""

    def __init__(self, service_logic: ServiceLogic, intent_logic: IntentLogic):
        self.service_logic = service_logic
        self.intent_logic = intent_logic
        self.stats = {
            "services_created": 0,
            "services_failed": 0,
            "intents_created": 0,
            "intents_failed": 0,
            "errors": []
        }

    def load_seed_data(self, file_path: str) -> Dict[str, Any]:
        """Load seed data from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✓ Successfully loaded seed data from {file_path}")
            return data
        except FileNotFoundError:
            print(f"✗ Error: Seed data file not found at {file_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"✗ Error: Invalid JSON in seed file: {e}")
            sys.exit(1)

    def seed_service_with_intents(self, service_data: Dict[str, Any]) -> bool:
        """
        Seed a single service along with its intents.
        Returns True if successful, False otherwise.
        """
        service_name = service_data.get("name", "Unknown")
        intents_data = service_data.pop("intents", [])

        try:
            print(f"\n📦 Processing service: {service_name}")

            # Step 1: Create all intents first
            intent_ids = []
            for intent_data in intents_data:
                try:
                    # Call addIntent with correct parameters
                    intent_id = self.intent_logic.addIntent(
                        intentName=intent_data["name"],
                        intentDescription=intent_data["description"],
                        intentTags=intent_data["tags"],
                        rateLimit=intent_data["rateLimit"],
                        price=intent_data["price"]
                    )

                    if intent_id:
                        intent_ids.append(intent_id)
                        self.stats["intents_created"] += 1
                        print(f"  ✓ Created intent: {intent_data['name']} (ID: {intent_id})")
                    else:
                        self.stats["intents_failed"] += 1
                        print(f"  ✗ Failed to create intent: {intent_data['name']}")

                except Exception as e:
                    self.stats["intents_failed"] += 1
                    error_msg = f"Intent '{intent_data.get('name')}' in service '{service_name}': {str(e)}"
                    self.stats["errors"].append(error_msg)
                    print(f"  ✗ Error creating intent: {intent_data.get('name')} - {e}")

            # Step 2: Create service with intent IDs
            try:
                service_id = self.service_logic.addService(
                    serviceName=service_data["name"],
                    serviceDescription=service_data["description"],
                    service_URL=service_data.get("url"),
                    intent_ids=intent_ids
                )

                if service_id:
                    self.stats["services_created"] += 1
                    print(f"✓ Service created: {service_name} (ID: {service_id})")
                    print(f"  └─ Linked {len(intent_ids)} intents")
                    return True
                else:
                    self.stats["services_failed"] += 1
                    error_msg = f"Failed to create service: {service_name}"
                    self.stats["errors"].append(error_msg)
                    print(f"✗ Failed to create service: {service_name}")

                    # Rollback: delete created intents
                    print(f"  🔄 Rolling back {len(intent_ids)} intents...")
                    for intent_id in intent_ids:
                        try:
                            self.intent_logic.deleteIntent(intent_id)
                        except Exception as e:
                            print(f"  ⚠️  Failed to rollback intent {intent_id}: {e}")

                    return False

            except Exception as e:
                self.stats["services_failed"] += 1
                error_msg = f"Service '{service_name}': {str(e)}"
                self.stats["errors"].append(error_msg)
                print(f"✗ Error creating service {service_name}: {e}")

                # Rollback: delete created intents
                print(f"  🔄 Rolling back {len(intent_ids)} intents...")
                for intent_id in intent_ids:
                    try:
                        self.intent_logic.deleteIntent(intent_id)
                    except Exception as e:
                        print(f"  ⚠️  Failed to rollback intent {intent_id}: {e}")

                return False

        except Exception as e:
            self.stats["services_failed"] += 1
            error_msg = f"Service '{service_name}': {str(e)}"
            self.stats["errors"].append(error_msg)
            print(f"✗ Error processing service {service_name}: {e}")
            return False

    def seed_all(self, seed_data: Dict[str, Any]) -> None:
        """Seed all services and their intents"""
        services = seed_data.get("services", [])

        if not services:
            print("⚠️  No services found in seed data")
            return

        print(f"\n🌱 Starting to seed {len(services)} services...\n")
        print("=" * 70)

        for service_data in services:
            self.seed_service_with_intents(service_data)

        print("\n" + "=" * 70)
        self.print_summary()

    def print_summary(self) -> None:
        """Print seeding summary"""
        print("\n📊 Seeding Summary:")
        print(f"  Services created: {self.stats['services_created']}")
        print(f"  Services failed:  {self.stats['services_failed']}")
        print(f"  Intents created:  {self.stats['intents_created']}")
        print(f"  Intents failed:   {self.stats['intents_failed']}")

        if self.stats["errors"]:
            print(f"\n❌ Errors encountered ({len(self.stats['errors'])}):")
            for i, error in enumerate(self.stats["errors"][:10], 1):  # Show first 10 errors
                print(f"  {i}. {error}")
            if len(self.stats["errors"]) > 10:
                print(f"  ... and {len(self.stats['errors']) - 10} more errors")
        else:
            print("\n✅ All data seeded successfully!")


def main():
    """Main function to run the seeding script"""
    print("=" * 70)
    print("🌱 DATABASE SEEDING SCRIPT")
    print("=" * 70)

    # Initialize DAL layers
    try:
        intent_dal = IntentDAL()
        service_dal = ServiceDAL()
    except Exception as e:
        print(f"✗ Error initializing DAL layers: {e}")
        print("Make sure your MongoDB connection is properly configured.")
        sys.exit(1)

    # Initialize Logic layers with DAL instances
    try:
        intent_logic = IntentLogic(intent_dal)
        service_logic = ServiceLogic(service_dal)
    except Exception as e:
        print(f"✗ Error initializing Logic layers: {e}")
        sys.exit(1)

    # Create seeder instance
    seeder = DatabaseSeeder(service_logic, intent_logic)

    # Load seed data
    seed_file = "arxiv_service_seed.json"
    seed_data = seeder.load_seed_data(seed_file)

    # Seed the database
    seeder.seed_all(seed_data)

    print("\n" + "=" * 70)
    print("🏁 Seeding complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
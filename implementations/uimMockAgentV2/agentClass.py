import requests
import argparse
import json


class agentClass:
    def __init__(self, external_url, catalogue_url):
        self.external_url = external_url.rstrip("/")
        self.catalogue_url = catalogue_url.rstrip("/")

    # === Fetch /agents.json from external UIM service ===
    def fetch_external_agents_json(self):
        try:
            response = requests.get(f"{self.external_url}/agents.json")
            response.raise_for_status()
            data = response.json()
            print("\n--- External UIM agents.json Data ---")
            #print(json.dumps(data, indent=2))
            return data
        except Exception as e:
            print(f"❌ Error fetching external agents.json: {e}")
            return None

    # === Add service to catalogue ===
    def add_service(self, service_info):
        payload = {
            "name": service_info.get("name"),
            "description": service_info.get("description"),
            "service_URL": service_info.get("service_url"),
        }
        try:
            response = requests.post(f"{self.catalogue_url}/services/", json=payload)
            response.raise_for_status()
            print(f"✅ Service '{payload['name']}' added successfully.")
        except Exception as e:
            print(f"❌ Failed to add service: {e}")

    # === Add intents to catalogue ===
    def add_intents(self, intents):
        for intent in intents:
            payload = {
                "intent_name": intent.get("intent_name"),
                "description": intent.get("description"),
                "tags": intent.get("tags", []),
                "rateLimit": self._extract_number(intent.get("rateLimit") or intent.get("rate_limit")),
                "price": self._extract_number(intent.get("price")),
            }
            try:
                response = requests.post(f"{self.catalogue_url}/intents/", json=payload)
                response.raise_for_status()
                print(f"✅ Intent '{payload['intent_name']}' added.")
            except Exception as e:
                print(f"❌ Failed to add intent '{payload.get('intent_name', '?')}': {e}")
                if hasattr(e, "response") and e.response is not None:
                    print("🔍 Response text:", e.response.text)

    # === Add UIM protocol metadata to catalogue ===
    def add_uimprotocol(self, data):
        payload = {
            "uimpublickey": data.get("uim-public-key"),
            "uimpolicyfile": data.get("uim-policy-file"),
            "uimApiDiscovery": data.get("uim-api-discovery"),
            "uimApiExceute": data.get("uim-api-execute"),
        }
        try:
            response = requests.post(f"{self.catalogue_url}/uimprotocol/", json=payload)
            response.raise_for_status()
            print("✅ UIM Protocol entry added.")
        except Exception as e:
            print(f"❌ Failed to add UIM Protocol: {e}")

    # === Fetch data from your catalogue ===
    def fetch_catalogue(self):
        try:
            print("\n--- Services ---")
            print(json.dumps(requests.get(f"{self.catalogue_url}/services/").json(), indent=2))

            print("\n--- Intents ---")
            print(json.dumps(requests.get(f"{self.catalogue_url}/intents/").json(), indent=2))

            print("\n--- UIM Protocol ---")
            print(json.dumps(requests.get(f"{self.catalogue_url}/uimprotocol/").json(), indent=2))

        except Exception as e:
            print(f"❌ Error fetching catalogue data: {e}")

    # === Extract number helper ===
    def _extract_number(self, value):
        if not value:
            return None
        try:
            return float("".join(c for c in value if (c.isdigit() or c == ".")))
        except Exception:
            return None

    # === Full sync: /agents.json → catalogue ===
    def sync_to_catalogue(self):
        data = self.fetch_external_agents_json()
        if not data:
            print("⚠️ No data fetched from external source. Aborting sync.")
            return

        service_info = data.get("service-info")
        intents = data.get("intents", [])

        if service_info:
            self.add_service(service_info)
        if intents:
            self.add_intents(intents)
        self.add_uimprotocol(data)

        print("\n✅ Sync completed successfully.")


def main():
    parser = argparse.ArgumentParser(description="UIM Agent to sync data into catalogue")
    parser.add_argument("--external", default="http://localhost:4000", help="External UIM service URL")
    parser.add_argument("--catalogue", default="http://127.0.0.1:8000", help="Catalogue API URL")
    parser.add_argument("--action", choices=["fetch-external", "fetch-catalogue", "sync"], required=True)
    args = parser.parse_args()

    agent = agentClass(args.external, args.catalogue)

    if args.action == "fetch-external":
        agent.fetch_external_agents_json()
    elif args.action == "fetch-catalogue":
        agent.fetch_catalogue()
    elif args.action == "sync":
        agent.sync_to_catalogue()


if __name__ == "__main__":
    main()

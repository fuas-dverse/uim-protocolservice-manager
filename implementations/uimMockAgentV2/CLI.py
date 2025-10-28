from agentClass import agentClass

def print_menu(catalogue_url, external_url):
    print("\n==============================")
    print("        UIM CLI MENU")
    print("==============================")
    print(f"Catalogue connection: {catalogue_url or '❌ Not set'}")
    print(f"External connection:  {external_url or '❌ Not set'}")
    print("------------------------------")
    print("1️⃣  Set catalogue connection")
    print("2️⃣  Set external service connection")
    print("3️⃣  Sync with catalogue (from external)")
    print("4️⃣  Display current catalogue entries")
    print("5️⃣  Exit")
    print("==============================")

def cli():
    # Default catalogue URL
    catalogue_url = "http://127.0.0.1:8000"
    external_url = "http://127.0.0.1:4000"
    Agent = None

    while True:
        print_menu(catalogue_url, external_url)
        choice = input("Select an option (1–5): ").strip()

        if choice == "1":
            catalogue_url = input("Enter new catalogue URL: ").strip() or catalogue_url
            print(f"✅ Catalogue connection set to: {catalogue_url}")

        elif choice == "2":
            external_url = input("Enter external service URL: ").strip() or None
            if external_url:
                print(f"External connection set to: {external_url}")
            else:
                print("️No external URL set.")

        elif choice == "3":
            if not external_url:
                print("Please set the external connection first.")
                continue
            Agent = agentClass(external_url, catalogue_url)
            Agent.sync_to_catalogue()

        elif choice == "4":
            Agent = agentClass(external_url or "", catalogue_url)
            Agent.fetch_catalogue()

        elif choice == "5":
            print("Exiting CLI. Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    cli()

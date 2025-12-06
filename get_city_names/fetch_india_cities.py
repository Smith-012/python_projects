import requests
import csv
from pathlib import Path

API_URL = "https://countriesnow.space/api/v0.1/countries/cities"

def get_cities(country: str) -> list[str]:
    """Return a clean, sorted list of cities for the given country."""
    resp = requests.post(API_URL, json={"country": country})
    resp.raise_for_status()
    data = resp.json().get("data", [])
    cities = {c.strip() for c in data if isinstance(c, str) and c.strip()}
    return sorted(cities)

def save_to_csv(cities: list[str], file_path: str | Path):
    """Save the list of cities into a CSV file."""
    file_path = Path(file_path)
    with file_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["city"])
        for city in cities:
            writer.writerow([city])
    print(f"Saved {len(cities)} cities to {file_path.resolve()}")

def fetch_and_save(country: str, file_path: str):
    """Reusable combined function."""
    cities = get_cities(country)
    save_to_csv(cities, file_path)

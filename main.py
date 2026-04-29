import csv
from pathlib import Path

import folium


DATA_FILE = Path("locations.csv")
OUTPUT_FILE = Path("map.html")
JABALPUR_COORDINATES = [23.1815, 79.9864]


def load_locations(file_path):
    """Load location data from a CSV file."""
    locations = []

    with file_path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            locations.append(
                {
                    "name": row["name"],
                    "latitude": float(row["latitude"]),
                    "longitude": float(row["longitude"]),
                }
            )

    return locations


def create_map(locations):
    """Create a Folium map centered on Jabalpur."""
    jabalpur_map = folium.Map(location=JABALPUR_COORDINATES, zoom_start=11)

    for location in locations:
        folium.Marker(
            location=[location["latitude"], location["longitude"]],
            popup=location["name"],
        ).add_to(jabalpur_map)

    return jabalpur_map


def main():
    locations = load_locations(DATA_FILE)
    jabalpur_map = create_map(locations)
    jabalpur_map.save(str(OUTPUT_FILE))
    print(f"Interactive map saved as {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

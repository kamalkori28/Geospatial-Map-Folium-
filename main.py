import html
from pathlib import Path

import folium
import pandas as pd
from folium.plugins import HeatMap, MarkerCluster


DATA_FILE = Path("locations.csv")
OUTPUT_FILE = Path("map.html")
JABALPUR_COORDINATES = [23.1815, 79.9864]
REQUIRED_COLUMNS = {"Name", "Latitude", "Longitude"}
VALID_MARKER_COLORS = {
    "red",
    "blue",
    "green",
    "purple",
    "orange",
    "darkred",
    "lightred",
    "beige",
    "darkblue",
    "darkgreen",
    "cadetblue",
    "lightgray",
    "gray",
    "black",
}
FALLBACK_COLORS = [
    "blue",
    "green",
    "red",
    "purple",
    "orange",
    "darkblue",
    "darkgreen",
    "cadetblue",
]
FALLBACK_ICONS = [
    "map-marker",
    "leaf",
    "camera",
    "road",
    "star",
    "train",
    "building",
    "book",
]
COLUMN_ALIASES = {
    "name": "Name",
    "latitude": "Latitude",
    "longitude": "Longitude",
    "category": "Category",
    "info": "Info",
    "icon": "Icon",
    "markercolor": "MarkerColor",
}


def normalize_columns(columns):
    """Allow simple header variations like name/Name or marker_color/MarkerColor."""
    normalized = {}

    for column in columns:
        cleaned_name = column.strip()
        normalized_key = cleaned_name.lower().replace(" ", "").replace("_", "")
        normalized[column] = COLUMN_ALIASES.get(normalized_key, cleaned_name)

    return normalized


def load_locations(file_path):
    """Read the CSV file and return clean location data."""
    if not file_path.exists():
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    data = pd.read_csv(file_path)
    data = data.rename(columns=normalize_columns(data.columns))

    missing_columns = REQUIRED_COLUMNS.difference(data.columns)
    if missing_columns:
        missing_list = ", ".join(sorted(missing_columns))
        raise ValueError(
            "The CSV file is missing required columns: "
            f"{missing_list}. Required columns are Name, Latitude, and Longitude."
        )

    for column_name in ["Category", "Info", "Icon", "MarkerColor"]:
        if column_name not in data.columns:
            data[column_name] = ""

        data[column_name] = data[column_name].fillna("").astype(str).str.strip()

    data["Name"] = data["Name"].fillna("").astype(str).str.strip()
    data["Latitude"] = pd.to_numeric(data["Latitude"], errors="coerce")
    data["Longitude"] = pd.to_numeric(data["Longitude"], errors="coerce")

    valid_rows = (
        data["Name"].ne("")
        & data["Latitude"].notna()
        & data["Longitude"].notna()
    )
    skipped_rows = len(data) - int(valid_rows.sum())

    cleaned_data = data.loc[valid_rows].copy()
    if cleaned_data.empty:
        raise ValueError("No valid rows were found in the CSV file.")

    cleaned_data["Coordinates"] = cleaned_data.apply(
        lambda row: f'{row["Latitude"]:.5f}, {row["Longitude"]:.5f}',
        axis=1,
    )

    return cleaned_data.reset_index(drop=True), skipped_rows


def build_popup(location):
    """Create a clean popup showing the most useful location details."""
    details = [
        f"<strong>Name:</strong> {html.escape(location.Name)}",
        f"<strong>Coordinates:</strong> {location.Coordinates}",
    ]

    if location.Category:
        details.append(f"<strong>Category:</strong> {html.escape(location.Category)}")
    if location.Info:
        details.append(f"<strong>Info:</strong> {html.escape(location.Info)}")

    popup_html = "<br>".join(details)
    return folium.Popup(popup_html, max_width=320)


def build_category_style_map(locations):
    """Give each category a consistent color and icon when categories exist."""
    category_style_map = {}
    categories = [category for category in locations["Category"].unique() if category]

    for index, category in enumerate(categories):
        category_style_map[category] = {
            "color": FALLBACK_COLORS[index % len(FALLBACK_COLORS)],
            "icon": FALLBACK_ICONS[index % len(FALLBACK_ICONS)],
        }

    return category_style_map


def get_marker_style(location, row_index, category_style_map):
    """Choose a marker color and icon, with optional CSV overrides."""
    if location.Category and location.Category in category_style_map:
        style = category_style_map[location.Category].copy()
    else:
        style = {
            "color": FALLBACK_COLORS[row_index % len(FALLBACK_COLORS)],
            "icon": FALLBACK_ICONS[row_index % len(FALLBACK_ICONS)],
        }

    custom_color = location.MarkerColor.lower()
    if custom_color in VALID_MARKER_COLORS:
        style["color"] = custom_color

    if location.Icon:
        style["icon"] = location.Icon

    return style


def add_marker_layer(map_object, locations):
    """Add clustered markers to a toggleable layer."""
    markers_group = folium.FeatureGroup(name="Markers", show=True)

    marker_cluster = MarkerCluster(
        name="Marker Cluster",
        control=False,
        show=True,
        chunkedLoading=True,
        disableClusteringAtZoom=15,
        maxClusterRadius=50,
    )
    marker_cluster.add_to(markers_group)

    category_style_map = build_category_style_map(locations)

    for row_index, location in enumerate(locations.itertuples(index=False)):
        marker_style = get_marker_style(location, row_index, category_style_map)

        folium.Marker(
            location=[location.Latitude, location.Longitude],
            popup=build_popup(location),
            icon=folium.Icon(
                color=marker_style["color"],
                icon=marker_style["icon"],
                prefix="fa",
            ),
        ).add_to(marker_cluster)

    markers_group.add_to(map_object)


def add_heatmap_layer(map_object, locations):
    """Add a heatmap layer for quick density visualization."""
    heatmap_group = folium.FeatureGroup(name="Heatmap", show=False)
    heat_data = locations[["Latitude", "Longitude"]].values.tolist()

    HeatMap(
        heat_data,
        radius=18,
        blur=14,
        min_opacity=0.35,
    ).add_to(heatmap_group)

    heatmap_group.add_to(map_object)


def create_map(locations):
    """Build the Folium map with tiles, clustered markers, and a heatmap."""
    folium_map = folium.Map(
        location=JABALPUR_COORDINATES,
        zoom_start=11,
        zoom_control=True,
        control_scale=True,
        prefer_canvas=True,
        tiles=None,
    )

    folium.TileLayer("OpenStreetMap", name="OpenStreetMap").add_to(folium_map)
    folium.TileLayer("CartoDB Positron", name="Light Map").add_to(folium_map)

    add_marker_layer(folium_map, locations)
    add_heatmap_layer(folium_map, locations)

    folium.LayerControl(collapsed=False).add_to(folium_map)
    return folium_map


def save_map(map_object, output_file):
    """Save the generated map as an HTML file."""
    map_object.save(str(output_file))


def main():
    locations, skipped_rows = load_locations(DATA_FILE)
    jabalpur_map = create_map(locations)
    save_map(jabalpur_map, OUTPUT_FILE)

    print(f"Loaded {len(locations)} valid location(s) from {DATA_FILE}")
    if skipped_rows:
        print(f"Skipped {skipped_rows} row(s) because required data was missing.")
    print(f"Interactive map saved as {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

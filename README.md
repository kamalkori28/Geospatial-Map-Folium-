# Jabalpur Folium GIS Map

This project reads location data from a CSV file and creates an interactive Folium map using a single Python file: `main.py`.

## Features

- Reads `Name`, `Latitude`, and `Longitude` from `locations.csv`
- Centers the map on Jabalpur, India
- Groups nearby points with `MarkerCluster`
- Adds a heatmap layer using `HeatMap`
- Adds `LayerControl` to toggle marker and heatmap layers
- Uses clean popups that show the location name and coordinates
- Supports optional marker color and icon variation for richer maps
- Uses a structure that stays beginner-friendly while scaling better for larger datasets

## Optional CSV columns

The script also supports these optional columns when available:

- `Category`
- `Info`
- `Icon`
- `MarkerColor`

## How to run

1. Install Python
2. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the script:

   ```bash
   python main.py
   ```

4. Open `map.html` in a browser

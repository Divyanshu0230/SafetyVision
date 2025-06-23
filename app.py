from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import networkx as nx
from sklearn.ensemble import RandomForestClassifier
import folium
from folium.plugins import MarkerCluster
import re

app = Flask(__name__)

# Load and process data
df = pd.read_csv('drone_sensor_data.csv')
df['hazard'] = (
    (df['lidar_distance_m'] < 2.0) |
    (df['thermal_temp_C'] > 45) |
    (df['lidar_quality_flag'].astype(str).str.lower() != "good")
)

features = ['lidar_distance_m', 'thermal_temp_C', 'wind_speed_mps']
model = RandomForestClassifier()
model.fit(df[features], df['hazard'])

# Build safe graph
G = nx.Graph()
for _, row in df.iterrows():
    coords = (row['latitude'], row['longitude'])
    if not row['hazard']:
        G.add_node(coords)
for i, row1 in df.iterrows():
    for j, row2 in df.iterrows():
        if i != j:
            coord1 = (row1['latitude'], row1['longitude'])
            coord2 = (row2['latitude'], row2['longitude'])
            if not row1['hazard'] and not row2['hazard']:
                dist = ((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)**0.5
                if dist < 0.005:
                    G.add_edge(coord1, coord2, weight=dist)

# Extract coordinates from Google Maps URL
def extract_coordinates_from_url(url):
    match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', url)
    if match:
        return float(match.group(1)), float(match.group(2))
    return None, None

def generate_map(start, end, route):
    m = folium.Map(location=start, zoom_start=14)
    cluster = MarkerCluster().add_to(m)

    for _, row in df.iterrows():
        coord = (row['latitude'], row['longitude'])
        hazard = row['hazard']
        label = "Hazard" if hazard else "Safe"
        color = "red" if hazard else "green"
        folium.Marker(coord, tooltip=label, icon=folium.Icon(color=color)).add_to(cluster)

    folium.Marker(start, tooltip="Start", icon=folium.Icon(color="blue")).add_to(m)
    folium.Marker(end, tooltip="Destination", icon=folium.Icon(color="purple")).add_to(m)

    if route:
        folium.PolyLine(route, color="darkblue", weight=5, tooltip="Safest Route").add_to(m)

    direction_steps = ""
    for i, (lat, lon) in enumerate(route):
        point_df = df[(df['latitude'] == lat) & (df['longitude'] == lon)]
        hazard_status = "Unknown"
        if not point_df.empty:
            hazard_status = "High" if point_df.iloc[0]['hazard'] else "Low"
        direction_steps += f"Step {i+1}: Proceed to ({lat:.5f}, {lon:.5f}) - Hazard: {hazard_status}<br>"

    info_box = f'''
     <div style="position: fixed; bottom: 50px; left: 50px; width: 280px; height: 400px;
     border:2px solid grey; z-index:9999; font-size:13px;
     background-color:white; padding: 10px; overflow:auto">
     <b>Legend</b><br>
     <span style="color:red;">●</span> Hazard Zone<br>
     <span style="color:green;">●</span> Safe Point<br>
     <span style="color:blue;">●</span> Start Point<br>
     <span style="color:purple;">●</span> Destination<br>
     <span style="color:darkblue;">━</span> Safest Path<br><br>
     <b>Travel Directions:</b><br>{direction_steps}
     </div>
    '''
    m.get_root().html.add_child(folium.Element(info_box))
    m.save("static/output_map.html")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/route", methods=["POST"])
def find_route():
    try:
        # Step 1: Try to get from Google Maps link
        gmaps_link = request.form.get("gmaps_link", "")
        start_lat = request.form.get("start_lat")
        start_lon = request.form.get("start_lon")

        if gmaps_link:
            lat, lon = extract_coordinates_from_url(gmaps_link)
            if lat is not None and lon is not None:
                start_lat = lat
                start_lon = lon

        start_lat = float(start_lat)
        start_lon = float(start_lon)
        end_lat = float(request.form['end_lat'])
        end_lon = float(request.form['end_lon'])

        start = min(G.nodes, key=lambda n: (n[0] - start_lat)**2 + (n[1] - start_lon)**2)
        end = min(G.nodes, key=lambda n: (n[0] - end_lat)**2 + (n[1] - end_lon)**2)
        route = nx.astar_path(G, start, end, weight='weight')

        generate_map(start, end, route)
        return redirect(url_for('static', filename='output_map.html'))

    except Exception as e:
        return f"<h3>Error: {str(e)}</h3>"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

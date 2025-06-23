# SafetyVision

SafetyVision is an AI-powered hazard detection and safe route planning web application designed for industrial environments. It leverages drone sensor data, machine learning, and interactive maps to help users identify hazards and find the safest path between two points.

## Features
- **Hazard Detection:** Uses LIDAR, thermal, and wind sensor data to detect hazardous zones.
- **Safe Route Finder:** Calculates and displays the safest route between two locations, avoiding hazards.
- **Interactive Map:** Visualizes hazards, safe points, start/end locations, and the computed route using Folium and Leaflet.
- **User-Friendly Interface:** Modern Bootstrap-based frontend for easy interaction.
- **Google Maps Integration:** Optionally extract coordinates from a Google Maps link for convenience.

## How It Works
1. **Data Processing:**
   - Loads drone sensor data from `drone_sensor_data.csv`.
   - Classifies each point as hazardous or safe using a Random Forest model.
2. **Graph Construction:**
   - Builds a graph of safe points and connects nearby safe locations.
3. **Route Calculation:**
   - Uses A* algorithm to find the safest path between user-specified start and end points.
4. **Visualization:**
   - Displays hazards, safe points, and the route on an interactive map.

## Setup Instructions
1. **Clone the repository:**
   ```sh
   git clone https://github.com/Divyanshu0230/SafetyVision.git
   cd SafetyVision
   ```
2. **Install dependencies:**
   ```sh
   pip install flask pandas networkx scikit-learn folium
   ```
3. **Run the app:**
   ```sh
   python3 app.py
   ```
4. **Open in browser:**
   Visit [http://127.0.0.1:5000/](http://127.0.0.1:5000/) or [http://localhost:5000/](http://localhost:5000/)

## File Structure
- `app.py` — Main Flask application
- `drone_sensor_data.csv` — Sample drone sensor data
- `templates/` — HTML templates (frontend)
- `static/` — Static files (generated maps)

## Usage
- Enter start and end coordinates (or a Google Maps link) in the web form.
- The app will display the safest route and highlight hazards on the map.

## License
This project is for educational and demonstration purposes. 
<<<<<<< Updated upstream
=======

import streamlit as st
>>>>>>> Stashed changes
import requests
import streamlit as st
import urllib.parse
import folium
from streamlit_folium import folium_static
<<<<<<< Updated upstream
=======
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import urllib.parse
from pyrosm import OSM
import pyrosm
import os
>>>>>>> Stashed changes

API_URL = "https://api.bbbike.org/api/0.2/bbbike/"
<<<<<<< Updated upstream
API_ID = "smatthies"

# Funktion, um die Route basierend auf Adressen zu berechnen
def get_route(start_address, end_address):
    if not start_address or not end_address:
        st.error("Ungültige Start- oder Zieladresse.")
        return None
    
    # Füge Städteinformationen zu den Adressen hinzu
    start_address_full = f"{start_address}, Berlin, Germany"
    end_address_full = f"{end_address}, Berlin, Germany"
    
    # Adressen kodieren, um sie in der URL verwenden zu können
    start_address_encoded = urllib.parse.quote(start_address_full)
    end_address_encoded = urllib.parse.quote(end_address_full)
    
    # Baue die API-URL
    url = (f"{API_URL}?appid={API_ID}"
           f"&start={start_address_encoded}"
           f"&ziel={end_address_encoded}"
           f"&pref_seen=1&pref_cat=N1&output_as=json")  # Bevorzugter Straßentyp = Nebenstraßen (pref_cat=N1)
    
    # Debugging-Ausgabe der URL
    st.write(f"Routen-URL: {url}")
    
    # Anfrage an die BBBike API senden
=======
APP_ID = "smatthies"

# Absolute Pfadangabe zur OSM-Datei
#file_path = r"C:\Users\Lenovo\Documents\FIW\ikt_projekt\safecycling\data\berlin-latest.osm.pbf"
file_path = "../data/berlin-latest.osm.pbf"

def check_file_path(file_path):
    """Check if the file path exists and is a file"""
    st.write(f"Überprüfe Datei: {file_path}")  # Ausgabe zur Überprüfung des Pfades

    if not os.path.exists(file_path):
        st.write(f"Das Verzeichnis von {file_path} existiert nicht.")

    if not os.path.isfile(file_path):
        st.error(f"Die Datei '{file_path}' existiert nicht. Bitte überprüfe den Pfad und den Dateinamen.")
        return False

    if not os.access(file_path, os.R_OK):
        st.error(f"Keine Leseberechtigung für die Datei '{file_path}'.")
        return False

    st.write(f"Die Datei '{file_path}' wurde gefunden.")
    return True

def get_coordinates(address):
    """Use Nominatim to get coordinates for a given address"""
    address_encoded = urllib.parse.quote(address)
    url = f"https://nominatim.openstreetmap.org/search?q={address_encoded}&format=json"
    response = requests.get(url)
    if response.status_code != 200:
        st.error(f"Fehler beim Abrufen der Koordinaten für Adresse '{address}': HTTP {response.status_code}")
        return None, None

    try:
        response_json = response.json()
        if response_json:
            return float(response_json[0]['lat']), float(response_json[0]['lon'])
        else:
            st.error(f"Keine Koordinaten für Adresse '{address}' gefunden.")
    except (ValueError, KeyError, IndexError) as e:
        st.error(f"Fehler beim Verarbeiten der Antwort für Adresse '{address}': {e}")
    return None, None

def get_route(start_coords, end_coords):
    """Fetch route from BBBike API with preferred settings"""
    if start_coords is None or end_coords is None:
        st.error("Ungültige Koordinaten für Start- oder Zieladresse.")
        return None

    url = (f"{API_URL}?appid={APP_ID}"
           f"&startc_wgs84={start_coords[1]},{start_coords[0]}"
           f"&zielc_wgs84={end_coords[1]},{end_coords[0]}"
           f"&pref_seen=1&pref_cat=N1&output_as=json")  # Bevorzugter Straßentyp = Nebenstraßen (pref_cat=N1)

    st.write(f"Routen-URL: {url}")  # Debugging-Ausgabe der URL
>>>>>>> Stashed changes
    response = requests.get(url)
    if response.status_code == 200:
        try:
            result = response.json()
            return result
        except ValueError as e:
            st.error(f"Fehler beim Abrufen der Route: {e}")
    else:
        st.error(f"Fehler beim Abrufen der Route: {response.status_code}")
    return None

# Funktion, um die Route auf einer Karte darzustellen
def display_route_on_map(route_data):
    if route_data is None:
        return None
    
    m = folium.Map(location=[52.5200, 13.4050], zoom_start=12)  # Karte mit Start in Berlin
    
    # Extrahiere die LongLatPath-Daten und zeichne die Route auf der Karte
    if 'LongLatPath' in route_data:
        points = [(float(coord.split(',')[1]), float(coord.split(',')[0])) for coord in route_data['LongLatPath']]
        folium.PolyLine(points, color='blue', weight=5).add_to(m)
        
        # Optional: Markiere Start und Ziel auf der Karte
        folium.Marker(location=points[0], popup="Start", icon=folium.Icon(color="green")).add_to(m)
        folium.Marker(location=points[-1], popup="Ziel", icon=folium.Icon(color="red")).add_to(m)
        
<<<<<<< Updated upstream
        return m
    else:
        st.error("Fehler: Keine 'LongLatPath' in den Routen-Daten gefunden.")
        return None

# Streamlit App Benutzeroberfläche
st.title("Fahrradroute berechnen 🚴‍♂️")

# Eingabefelder für Start- und Zieladresse
start_address = st.text_input("Startadresse eingeben:")
end_address = st.text_input("Zieladresse eingeben:")
=======
    return m

@st.cache_data
def load_osm_data(file_path):
    """Load OSM data for a given file path"""
    osm = OSM(file_path)
    return osm.get_network(network_type="cycling", extra_attributes=["highway"])

def fetch_osm_segment_info(route_data, file_path):
    """Fetch OSM segment info for the points in the route"""
    if not check_file_path(file_path):
        return gpd.GeoDataFrame()

    osm_data = []
    try:
        cycle_net_berlin = load_osm_data(file_path)

        for coord in route_data['LongLatPath']:
            lat, lon = map(float, coord.split(','))
            point = gpd.GeoSeries([Point(lon, lat)], crs="EPSG:4326")
            mask = cycle_net_berlin['geometry'].apply(lambda x: x.contains(point.iloc[0])).values
            
            segment_info = cycle_net_berlin[mask]
            if not segment_info.empty:
                osm_data.append(segment_info)
    except KeyError as e:
        st.error("Fehler: API-Antwortstruktur enthält keine 'LongLatPath'.")
    except Exception as e:
        st.error(f"Allgemeiner Fehler: {e}")

    if osm_data:
        osm_gdf = gpd.GeoDataFrame(pd.concat(osm_data, ignore_index=True))

        # Extrahieren der relevanten Spalten
        highways = osm_gdf[['geometry', 'highway']]

        # verschiedene Straßentypen und deren Häufigkeit zählen
        highway_count = highways['highway'].value_counts(normalize=True)*100
        st.write("Verteilung der Straßentypen auf der Route:")
        st.write(highway_count)

        # Schwelle für seltene Straßentypen
        threshold = 1

         # Identifizieren von seltenen Straßentypen im gesamten Datensatz
        rare_highways = highway_count[highway_count < threshold]
        st.write("Seltene Straßentypen:")
        st.write(rare_highways)

        # Erstellen einer neuen Spalte und Ersetzen der seltenen Straßentypen durch 'highway_rare'
        osm_gdf['highway'] = osm_gdf['highway'].apply(lambda x: 'highway_rare' if x in rare_highways else x)

        return osm_gdf
    return gpd.GeoDataFrame()

def pipeline(start_address, end_address):
    start_coords = get_coordinates(start_address)
    end_coords = get_coordinates(end_address)
    if None in start_coords or None in end_coords:
        st.error("Konnte die Koordinaten für eine der eingegebenen Adressen nicht ermitteln.")
        return

    st.write(f"Route von {start_address} nach {end_address}:")
    route_data = get_route(start_coords, end_coords)
    if route_data:
        route_map = visualize_route(route_data)
        folium_static(route_map, width=725)
        
        osm_segment_info = fetch_osm_segment_info(route_data, file_path)
        if not osm_segment_info.empty:
            st.write(osm_segment_info[['highway']].dropna())
        else:
            st.write("Keine OSM-Segmentinformationen verfügbar.")
    else:
        st.error("Konnte die Route nicht abrufen.")
        
# Streamlit App Setup
st.set_page_config(
    page_title="SafeCycling Berlin",
    page_icon="🚲",
)

st.title("Deine Fahrradroute in Berlin 🚲")

start_address = st.text_input("Startadresse eingeben", value="Wildenbruchstraße 33, Berlin")
end_address = st.text_input("Zieladresse eingeben",  value="Rubensstr. 6, Berlin")
>>>>>>> Stashed changes

# Button zur Berechnung der Route
if st.button("Route berechnen"):
    if start_address and end_address:
        # Route von BBBike API abrufen
        route_data = get_route(start_address, end_address)
        
        if route_data:
            st.write("Route erfolgreich abgerufen!")
            
            # Route auf einer Karte darstellen
            route_map = display_route_on_map(route_data)
            if route_map:
                folium_static(route_map)  # Zeige die Karte in Streamlit an
        else:
            st.error("Route konnte nicht abgerufen werden.")
    else:
        st.error("Bitte sowohl Start- als auch Zieladresse eingeben.")
<<<<<<< Updated upstream
=======

# Option zum Löschen des Caches hinzufügen
if st.button('Cache löschen'):
    st.cache_data.clear()
    st.success("Cache erfolgreich gelöscht!")
>>>>>>> Stashed changes


import streamlit as st
import requests
import folium
from streamlit_folium import folium_static
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import urllib.parse
import pyrosm
import os

# KOnfiguration 
# BBBike API Parameters
API_URL = "https://api.bbbike.org/api/0.2/bbbike/"
APP_ID = "smatthies"

# OpenCage API Key
OPENCAGE_API_KEY = "46bbbd3be1674994a02ad03b9569c0ed"  

# Pfad zum Fahrradnetzwerk in Berlin (OSM)
file_path = "../data/berlin-latest.osm.pbf"

# OpenCage-API wird verwendet, um Koordinaten für eine angegebene Adresse zu erhalten
def get_coordinates(address):
    """Use OpenCage to get coordinates for a given address"""
    address_encoded = urllib.parse.quote(address)
    url = f"https://api.opencagedata.com/geocode/v1/json?q={address_encoded}&key={OPENCAGE_API_KEY}"
    
    response = requests.get(url)
    if response.status_code != 200:
        st.error(f"Fehler beim Abrufen der Koordinaten für Adresse '{address}': HTTP {response.status_code}")
        return None, None

    try:
        response_json = response.json()
        if response_json and response_json['results']:
            return float(response_json['results'][0]['geometry']['lat']), float(response_json['results'][0]['geometry']['lng'])
        else:
            st.error(f"Keine Koordinaten für Adresse '{address}' gefunden.")
    except (ValueError, KeyError, IndexError) as e:
        st.error(f"Fehler beim Verarbeiten der Antwort für Adresse '{address}': {e}")
    return None, None

# BBBike-API wird verwendet, um eine Fahrradroutenplanung zwischen zwei Koordinatenpunkten zu erhalten.
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


# Visualisierung der Route mit Folium
def visualize_route(route_data):
    """Visualize route on map"""
    m = folium.Map(location=[52.5200, 13.4050], zoom_start=12)
    try:
        points = [(float(coord.split(',')[1]), float(coord.split(',')[0])) for coord in route_data['LongLatPath']]
        folium.PolyLine(points, color='blue', weight=5).add_to(m)
        
        for point in points:
            folium.CircleMarker(location=point,
                                radius=3,
                                color="red",
                                fill=True,
                                fill_color="red").add_to(m)
    except KeyError as e:
        st.error(f"Fehler beim Verarbeiten der Routenpunkte: {e}")
        
    return m


# OSM-Segmentinformationen werden für die Punkte in der Route abgerufen
def fetch_osm_segment_info(route_data, file_path):
    """Fetch OSM segment info for the points in the route"""
    osm_data = []
    try:
        berlin_osm = pyrosm.OSM(file_path)
        cycle_net_berlin = berlin_osm.get_network(network_type="cycling", extra_attributes=["highway"])

        for coord in route_data['LongLatPath']:
            lat, lon = map(float, coord.split(','))
            point = Point(lon, lat)
            mask = cycle_net_berlin['geometry'].apply(lambda x: x.contains(point)).values
            
            segment_info = cycle_net_berlin.loc[mask]  # Verbesserung: Verwendung der .loc Methode statt chained assignment
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
        osm_gdf.loc[osm_gdf['highway'].isin(rare_highways.index), 'highway'] = 'highway_rare'  # Update per loc

        return osm_gdf
    return gpd.GeoDataFrame()


# Pipeline-Funktion: kombiniert die Funktionen, um alles zusammenzubringen
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
        folium_static(route_map)
        
        osm_segment_info = fetch_osm_segment_info(route_data, file_path)
        if not osm_segment_info.empty:
            st.write(osm_segment_info[['highway']].dropna())
        else:
            st.write("Keine OSM-Segmentinformationen verfügbar.")
    else:
        st.error("Konnte die Route nicht abrufen.")
        

# Streamlit-App Setup

st.title("Berlin Fahrradroute Planung")

start_address = st.text_input("Startadresse eingeben", value="Wildenbruchstraße 33, Berlin")
end_address = st.text_input("Zieladresse eingeben",  value="Rubensstr. 6, Berlin")

if st.button("Route berechnen"):
    if start_address and end_address:
        pipeline(start_address, end_address)
    else:
        st.error("Bitte sowohl Start- als auch Zieladresse eingeben.")
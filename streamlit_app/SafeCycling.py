import streamlit as st
import pandas as pd


st.set_page_config(
    page_title="SafeCycling",
    page_icon="🚲",
)

st.title("SafeCycling 🚲")
# st.markdown('<h1 style="color: #9370DB ;">SafeCycling</h1>', unsafe_allow_html=True)


st.sidebar.markdown("# SafeCycling 🚲") # Titel der Sidebar

st.sidebar.success("Wähle eine Seite.") # 

# Untertitel 
st.subheader("Prognose des Gefahrenpotenzials im Berliner Fahrradverkehr")

# Fragestellung
st.write("Wie sicher ist deine Fahrradroute? Nutze die untenstehenden Funktionen, \
        um dir einzelne Aspekte, wie Maximalgeschwindigkeit, Straßenbelag \
        und Gefahrenpunkte auf deiner Route anzeigen zu lassen.")











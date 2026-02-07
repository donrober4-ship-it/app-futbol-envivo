import streamlit as st
import requests

# Configuración de la página
st.set_page_config(page_title="Mi App de Fútbol", page_icon="⚽")

# --- CONFIGURACIÓN DE TU LLAVE ---
API_KEY = 'b595c09921444acb96654e5552b4c4eb'  # <---
HEADERS = { 'X-Auth-Token': API_KEY }

st.title("⚽ Marcadores Internacionales")
st.write("Resultados en vivo y próximos partidos")

# Función para obtener datos
def obtener_partidos():
    url = 'https://api.football-data.org/v4/matches'
    response = requests.get(url, headers=HEADERS)
    return response.json()

try:
    data = obtener_partidos()
    partidos = data.get('matches', [])

    if not partidos:
        st.info("No hay partidos programados para hoy.")
    
    for match in partidos:
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 2])
            
            # Datos del partido
            liga = match['competition']['name']
            home_team = match['homeTeam']['name']
            away_team = match['awayTeam']['name']
            home_logo = match['homeTeam']['crest']
            away_logo = match['awayTeam']['crest']
            
            # Marcador (si es None, ponemos 0)
            score_h = match['score']['fullTime']['home'] if match['score']['fullTime']['home'] is not None else "-"
            score_a = match['score']['fullTime']['away'] if match['score']['fullTime']['away'] is not None else "-"

            with col1:
                st.image(home_logo, width=50)
                st.subheader(home_team)
            
            with col2:
                st.title(f"{score_h} : {score_a}")
                st.caption(match['status'])
            
            with col3:
                st.image(away_logo, width=50)
                st.subheader(away_team)
            
            st.divider()

except Exception as e:
    st.error(f"Hubo un problema al cargar los datos: {e}")

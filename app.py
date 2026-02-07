import streamlit as st
import requests

# Configuración de la página
st.set_page_config(page_title="Mi App de Fútbol", page_icon="⚽", layout="wide")

# --- SEGURIDAD Y LLAVE ---
# Si guardaste tu llave en 'Secrets' de Streamlit (recomendado):
API_KEY = st.secrets["API_KEY"] if "API_KEY" in st.secrets else 'b595c09921444acb96654e5552b4c4eb'
HEADERS = { 'X-Auth-Token': API_KEY }

# --- BARRA LATERAL (FAVORITOS) ---
st.sidebar.title("⭐ Mis Favoritos")
st.sidebar.write("Escribe los equipos que quieres resaltar:")

# Aquí es donde aplicamos tu preferencia de guardar datos
equipos_fav_input = st.sidebar.text_input(
    "Equipos (ej: Real Madrid, Millonarios, Colombia)", 
    value="Real Madrid, Barcelona"
)
# Limpiamos la lista para que sea fácil de buscar
favoritos = [e.strip().lower() for e in equipos_fav_input.split(",")]

st.title("⚽ Resultados Internacionales")

# Función para obtener datos
@st.cache_data(ttl=300) # Guarda los datos por 5 minutos para no agotar tu API gratis
def obtener_partidos():
    url = 'https://api.football-data.org/v4/matches'
    try:
        response = requests.get(url, headers=HEADERS)
        return response.json().get('matches', [])
    except:
        return []

partidos = obtener_partidos()

if not partidos:
    st.warning("No hay partidos para mostrar en este momento.")
else:
    # --- MOSTRAR PARTIDOS ---
    for match in partidos:
        home = match['homeTeam']['name']
        away = match['awayTeam']['name']
        
        # Lógica de resaltado
        es_favorito = any(fav in home.lower() or fav in away.lower() for fav in favoritos)
        
        # Si es favorito, ponemos un borde dorado o un color distinto
        with st.container(border=True):
            if es_favorito:
                st.markdown("### ⭐ PARTIDO DESTACADO")
            
            col1, col2, col3 = st.columns([2, 1, 2])
            
            with col1:
                st.image(match['homeTeam']['crest'], width=60)
                st.subheader(home)
            
            with col2:
                s_h = match['score']['fullTime']['home'] if match['score']['fullTime']['home'] is not None else "-"
                s_a = match['score']['fullTime']['away'] if match['score']['fullTime']['away'] is not None else "-"
                st.markdown(f"<h1 style='text-align: center;'>{s_h} - {s_a}</h1>", unsafe_allow_html=True)
                st.caption(f"<p style='text-align: center;'>{match['status']}</p>", unsafe_allow_html=True)
            
            with col3:
                st.image(match['awayTeam']['crest'], width=60)
                st.subheader(away)

import streamlit as st
import requests
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Configuración visual
st.set_page_config(page_title="Futbol App Pro", page_icon="⚽", layout="wide")

# --- CONEXIÓN Y LLAVES ---
# Se asume que pondrás tu API_KEY en los Secrets de Streamlit
FOOTBALL_API_KEY = st.secrets["API_KEY"]
HEADERS = { 'X-Auth-Token': FOOTBALL_API_KEY }

# Conector a la base de datos (Google Sheets oculto)
conn = st.connection("gsheets", type=GSheetsConnection)

# --- LÓGICA DE FAVORITOS (INTERFAZ) ---
st.sidebar.title("⭐ Mis Favoritos")

# 1. Leer favoritos actuales (ttl=0 para refrescar al instante)
try:
    df_favs = conn.read(worksheet="Sheet1", ttl=0)
except:
    # Si la hoja está vacía, creamos una estructura básica
    df_favs = pd.DataFrame({"Equipos": ["Real Madrid", "Colombia"]})

# 2. Editor interactivo en la App
with st.sidebar.expander("📝 Editar Lista"):
    nuevo_df = st.data_editor(df_favs, num_rows="dynamic", use_container_width=True)
    if st.sidebar.button("💾 Guardar Cambios"):
        conn.update(worksheet="Sheet1", data=nuevo_df)
        st.sidebar.success("¡Favoritos guardados!")
        st.rerun()

lista_favoritos = [str(e).lower() for e in nuevo_df['Equipos'].tolist()]

# --- OBTENER PARTIDOS ---
@st.cache_data(ttl=300)
def cargar_datos():
    url = 'https://api.football-data.org/v4/matches'
    res = requests.get(url, headers=HEADERS)
    return res.json().get('matches', [])

st.title("⚽ Resultados en Vivo")
partidos = cargar_datos()

if not partidos:
    st.info("No hay partidos para hoy.")
else:
    for match in partidos:
        home = match['home_team_name'] = match['homeTeam']['name']
        away = match['away_team_name'] = match['awayTeam']['name']
        
        # ¿Es un partido favorito?
        es_fav = any(f in home.lower() or f in away.lower() for f in lista_favoritos)
        
        # Diseño de la tarjeta
        with st.container(border=True):
            if es_fav:
                st.write("🌟 **PARTIDO SEGUIDO**")
            
            c1, c2, c3 = st.columns([2, 1, 2])
            with c1:
                st.image(match['homeTeam']['crest'], width=40)
                st.markdown(f"**{home}**")
            with c2:
                g_h = match['score']['fullTime']['home'] if match['score']['fullTime']['home'] is not None else "-"
                g_a = match['score']['fullTime']['away'] if match['score']['fullTime']['away'] is not None else "-"
                st.markdown(f"### {g_h} - {g_a}")
                st.caption(match['status'])
            with c3:
                st.image(match['awayTeam']['crest'], width=40)
                st.markdown(f"**{away}**")

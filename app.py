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

# --- OBTENER PARTIDOS (Hoy y Próximos) ---
@st.cache_data(ttl=300)
def cargar_datos():
    # 'dateFrom' y 'dateTo' nos aseguran ver un rango más amplio (hoy y mañana)
    url = 'https://api.football-data.org/v4/matches'
    try:
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            return res.json().get('matches', [])
        else:
            st.error(f"Error de API: {res.status_code}")
            return []
    except Exception as e:
        st.error(f"Fallo de conexión: {e}")
        return []

st.title("⚽ Cartelera de Fútbol")
partidos = cargar_datos()

if not partidos:
    st.info("No hay partidos destacados programados para hoy en las ligas principales.")
    st.caption("Nota: La versión gratuita cubre Premier League, LaLiga, Serie A, Bundesliga, Ligue 1 y Champions.")
else:
    # Separamos favoritos de los demás para que aparezcan ARRIBA
    fav_matches = []
    other_matches = []

    for m in partidos:
        home = m['homeTeam']['name']
        away = m['awayTeam']['name']
        if any(f in home.lower() or f in away.lower() for f in lista_favoritos):
            fav_matches.append(m)
        else:
            other_matches.append(m)

    # 1. MOSTRAR FAVORITOS PRIMERO
    if fav_matches:
        st.subheader("🌟 Tus Partidos Seguidos")
        for match in fav_matches:
            with st.container(border=True):
                st.info(f"📍 {match['competition']['name']}")
                c1, c2, c3 = st.columns([2, 1, 2])
                with c1:
                    st.image(match['homeTeam']['crest'], width=40)
                    st.write(f"**{match['homeTeam']['name']}**")
                with c2:
                    score = match['score']['fullTime']
                    st.markdown(f"### {score['home'] if score['home'] is not None else ''} - {score['away'] if score['away'] is not None else ''}")
                    st.caption(match['status'])
                with c3:
                    st.image(match['awayTeam']['crest'], width=40)
                    st.write(f"**{match['awayTeam']['name']}**")

    # 2. MOSTRAR EL RESTO (EL GLOBAL)
    st.divider()
    st.subheader("🌍 Todos los Resultados")
    for match in other_matches:
        with st.expander(f"{match['homeTeam']['name']} vs {match['awayTeam']['name']} ({match['competition']['name']})"):
            c1, c2, c3 = st.columns(3)
            c1.write(f"🏠 {match['homeTeam']['name']}")
            score = match['score']['fullTime']
            c2.write(f"🏁 {score['home'] if score['home'] is not None else 0} - {score['away'] if score['away'] is not None else 0}")
            c3.write(f"🚀 {match['awayTeam']['name']}")

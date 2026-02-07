import streamlit as st
import requests
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Configuración visual
st.set_page_config(page_title="Futbol App Pro", page_icon="⚽", layout="wide")

# --- CONEXIÓN Y LLAVES ---
FOOTBALL_API_KEY = st.secrets["API_KEY"]
HEADERS = { 'X-Auth-Token': FOOTBALL_API_KEY }

# Conector a la base de datos (Google Sheets)
conn = st.connection("gsheets", type=GSheetsConnection)

# --- LÓGICA DE FAVORITOS ---
st.sidebar.title("⭐ Mis Favoritos")

try:
    df_favs = conn.read(worksheet="Sheet1", ttl=0)
except:
    df_favs = pd.DataFrame({"Equipos": ["Real Madrid", "Colombia"]})

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
    try:
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            return res.json().get('matches', [])
        return []
    except:
        return []

partidos = cargar_datos()

# --- INTERFAZ DE FILTROS ---
st.title("⚽ Resultados Globales")

if not partidos:
    st.info("No hay partidos destacados para hoy.")
else:
    # Extraer ligas únicas para el filtro
    ligas = sorted(list(set([m['competition']['name'] for m in partidos])))
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        liga_seleccionada = st.multiselect("🏆 Filtrar por Liga", ligas, default=ligas)
    with col_f2:
        estado_seleccionado = st.multiselect("⏱️ Estado", ["IN_PLAY", "FINISHED", "TIMED"], default=["IN_PLAY", "FINISHED", "TIMED"])

    # Aplicar Filtros
    partidos_filtrados = [
        m for m in partidos 
        if m['competition']['name'] in liga_seleccionada and m['status'] in estado_seleccionado
    ]

    # Separar Favoritos
    fav_matches = []
    other_matches = []
    for m in partidos_filtrados:
        home = m['homeTeam']['name'].lower()
        away = m['awayTeam']['name'].lower()
        if any(f in home or f in away for f in lista_favoritos):
            fav_matches.append(m)
        else:
            other_matches.append(m)

    # --- MOSTRAR RESULTADOS ---
    if fav_matches:
        st.subheader("🌟 Tus Partidos Seguidos")
        for m in fav_matches:
            with st.container(border=True):
                st.caption(f"{m['competition']['name']} • {m['status']}")
                c1, c2, c3 = st.columns([2, 1, 2])
                score = m['score']['fullTime']
                c1.markdown(f"**{m['homeTeam']['name']}**")
                c2.markdown(f"### {score['home'] if score['home'] is not None else '-'} : {score['away'] if score['away'] is not None else '-'}")
                c3.markdown(f"**{m['awayTeam']['name']}**")

    st.divider()
    st.subheader("🌍 Resto de la Jornada")
    if not other_matches:
        st.write("No hay otros partidos con los filtros seleccionados.")
    else:
        for m in other_matches:
            with st.expander(f"{m['homeTeam']['name']} vs {m['awayTeam']['name']} ({m['status']})"):
                st.write(f"Competencia: {m['competition']['name']}")
                score = m['score']['fullTime']
                st.write(f"Resultado: {score['home'] if score['home'] is not None else 0} - {score['away'] if score['away'] is not None else 0}")

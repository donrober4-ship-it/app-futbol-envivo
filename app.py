import streamlit as st
import requests
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Configuración visual
st.set_page_config(page_title="Futbol App Pro", page_icon="⚽", layout="wide")

# --- ESTILO CSS PARA EL PARPADEO ---
st.markdown("""
    <style>
    @keyframes blinker {
        50% { opacity: 0; }
    }
    .live-indicator {
        color: red;
        font-weight: bold;
        animation: blinker 1s linear infinite;
    }
    </style>
    """, unsafe_allow_html=True)

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
    df_favs = pd.DataFrame({"Equipos": ["Real Madrid", "Millonarios", "Nacional"]})

with st.sidebar.expander("📝 Editar Lista"):
    nuevo_df = st.data_editor(df_favs, num_rows="dynamic", use_container_width=True)
    if st.sidebar.button("💾 Guardar Cambios"):
        conn.update(worksheet="Sheet1", data=nuevo_df)
        st.sidebar.success("¡Favoritos guardados!")
        st.rerun()

lista_favoritos = [str(e).lower() for e in nuevo_df['Equipos'].tolist()]

# --- OBTENER PARTIDOS ---
@st.cache_data(ttl=60) # Actualizar cada minuto para el "En Vivo"
def cargar_datos():
    # Intentamos traer partidos generales
    url = 'https://api.football-data.org/v4/matches'
    try:
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            return res.json().get('matches', [])
        return []
    except:
        return []

partidos = cargar_datos()

st.title("⚽ Resultados en Tiempo Real")

if not partidos:
    st.info("No hay partidos destacados para hoy. La liga colombiana se mostrará cuando la API reporte encuentros disponibles.")
else:
    # Filtros
    ligas = sorted(list(set([m['competition']['name'] for m in partidos])))
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        liga_seleccionada = st.multiselect("🏆 Filtrar por Liga/Copa", ligas, default=ligas)
    with col_f2:
        estado_seleccionado = st.multiselect("⏱️ Estado", ["IN_PLAY", "FINISHED", "TIMED", "PAUSED"], default=["IN_PLAY", "FINISHED", "TIMED", "PAUSED"])

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

    # --- MOSTRAR FAVORITOS ---
    if fav_matches:
        st.subheader("🌟 Tus Partidos Seguidos")
        for m in fav_matches:
            with st.container(border=True):
                # Indicador de EN VIVO
                status_text = m['status']
                if status_text in ["IN_PLAY", "PAUSED"]:
                    st.markdown('<p class="live-indicator">● EN VIVO</p>', unsafe_allow_html=True)
                else:
                    st.caption(f"{m['competition']['name']} • {status_text}")
                
                c1, c2, c3 = st.columns([2, 1, 2])
                score = m['score']['fullTime']
                
                with c1:
                    st.image(m['homeTeam']['crest'], width=35)
                    st.write(f"**{m['homeTeam']['name']}**")
                with c2:
                    st.markdown(f"<h2 style='text-align: center;'>{score['home'] if score['home'] is not None else '-'} : {score['away'] if score['away'] is not None else '-'}</h2>", unsafe_allow_html=True)
                with c3:
                    st.image(m['awayTeam']['crest'], width=35)
                    st.write(f"**{m['awayTeam']['name']}**")

    st.divider()
    st.subheader("🌍 Todos los Partidos")
    for m in other_matches:
        label = f"{m['homeTeam']['name']} vs {m['awayTeam']['name']}"
        if m['status'] == "IN_PLAY":
            label = f"🔴 {label} (EN VIVO)"
        
        with st.expander(label):
            st.write(f"Competición: {m['competition']['name']}")
            score = m['score']['fullTime']
            st.write(f"Marcador: {score['home'] if score['home'] is not None else 0} - {score['away'] if score['away'] is not None else 0}")

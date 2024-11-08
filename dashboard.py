# dashboard.py
import streamlit as st
import pandas as pd
import folium
import numpy as np
import plotly.express as px
from streamlit_folium import st_folium
from secciones.mapa_ubicacion import generar_mapa_ubicacion
from secciones.tabla_estadisticas import generar_tabla_estadisticas


image_url = 'https://drive.google.com/thumbnail?id=1kY4-rRTGbDpgkR8GcLvNkMrhZ7KXCtLL'


# Configurar el fondo con una imagen
st.markdown(f"""
    <style>
        body {{
            background-image: url('{image_url}'); /* URL de la imagen */
            background-size: cover;  /* Hacer que la imagen cubra toda la pantalla */
            background-position: center center;  /* Centrar la imagen */
            background-attachment: fixed;  /* Mantener la imagen fija al hacer scroll */
            color: white;  /* Color de texto blanco para asegurar visibilidad */
        }}
        .stApp {{
            background: transparent;  /* Mantener el fondo transparente para los componentes de Streamlit */
        }}
    </style>
""", unsafe_allow_html=True)


# Carga de datos
@st.cache_data(show_spinner=False)
def cargar_datos():
    df = pd.read_csv("TB_CENTRO_VACUNACION.csv", sep=";")
    df1 = df.copy()
    df1.rename(columns={'nombre': 'Centro_vacunacion'}, inplace=True)
    df1.drop(['id_centro_vacunacion', 'id_eess'], axis=1, inplace=True)
    df1.replace('', np.nan, inplace=True)
    df1['entidad_administra'] = df1['entidad_administra'].fillna('No especificado')

    df_ubigeo = pd.read_csv("TB_UBIGEOS.csv", sep=";")
    df_ub = df_ubigeo[['id_ubigeo', 'provincia', 'distrito', 'region']]
    df3 = pd.merge(df1, df_ub, on='id_ubigeo', how='left')
    df3 = df3[(df3['latitud'] != 0) & (df3['longitud'] != 0)]
    return df3

df3 = cargar_datos()

# Configuración de título y barra lateral
st.markdown("""
    <style>
        .title {
            background-color: black;
            color: white;
            font-size: 40px;
            padding: 20px;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# Título con la clase personalizada
st.markdown('<div class="title">Mapa de Ubicación del Centro de Vacunación Seleccionado</div>', unsafe_allow_html=True)

st.sidebar.title("Elige tu Centro de Vacunación")

# Agregar una opción "Seleccione una opción" al selectbox de región
region_opciones = ["Seleccione una opción"] + sorted(df3['region'].unique().tolist())
region_seleccionada = st.sidebar.selectbox("Seleccione la región", options=region_opciones)

# Variables para almacenar los valores seleccionados
provincia_seleccionada = "Seleccione una opción"
distrito_seleccionado = "Seleccione una opción"
centro_seleccionado = "Seleccione una opción"

# Filtrar provincias según región
if region_seleccionada != "Seleccione una opción":
    provincias_filtradas = df3[df3['region'] == region_seleccionada]['provincia'].unique()
    provincia_opciones = ["Seleccione una opción"] + sorted(provincias_filtradas.tolist())
    provincia_seleccionada = st.sidebar.selectbox("Seleccione la provincia", options=provincia_opciones)

# Filtrar distritos según provincia
if provincia_seleccionada != "Seleccione una opción":
    distritos_filtrados = df3[(df3['region'] == region_seleccionada) & (df3['provincia'] == provincia_seleccionada)]['distrito'].unique()
    distrito_opciones = ["Seleccione una opción"] + sorted(distritos_filtrados.tolist())
    distrito_seleccionado = st.sidebar.selectbox("Seleccione el distrito", options=distrito_opciones)

# Filtrar centros de vacunación según distrito
if distrito_seleccionado != "Seleccione una opción":
    centros_filtrados = df3[(df3['region'] == region_seleccionada) & (df3['provincia'] == provincia_seleccionada) & (df3['distrito'] == distrito_seleccionado)]['Centro_vacunacion'].unique()
    centro_opciones = ["Seleccione una opción"] + sorted(centros_filtrados.tolist())
    centro_seleccionado = st.sidebar.selectbox("Seleccione el centro de vacunación", options=centro_opciones)

# Filtrar el DataFrame para obtener las coordenadas del centro de vacunación seleccionado
centro_df = df3[df3['Centro_vacunacion'] == centro_seleccionado]

# Mostrar las secciones
if centro_seleccionado != "Seleccione una opción" and not centro_df.empty:
    # Generar las secciones según la selección del usuario
    st.markdown("""
        <style>
            .element-container {
                margin-top: 0px;
                margin-bottom: 0px;
                padding: 0;
            }
            .stMarkdown { margin-top: 0px; margin-bottom: 0px; }
        </style>
    """, unsafe_allow_html=True)

    with st.container():
        generar_mapa_ubicacion(df3, centro_df, centro_seleccionado)
        generar_tabla_estadisticas(df3, region_seleccionada, provincia_seleccionada, distrito_seleccionado)
else:
    st.markdown("""
        <div style="background-color: #f9c74f; padding: 15px; border-radius: 5px; font-size: 18px; text-align: center; color: #333;">
            <strong>Selecciona un centro de vacunación para ver la información.</strong>
        </div>
    """, unsafe_allow_html=True)

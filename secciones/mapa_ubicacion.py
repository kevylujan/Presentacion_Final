# secciones/mapa_ubicacion.py
import streamlit as st
import pandas as pd
import folium
import numpy as np
import plotly.express as px
import folium
from streamlit_folium import st_folium


def generar_mapa_ubicacion(df3, centro_df, centro_seleccionado):
    if centro_df.empty:
        st.warning("No hay datos disponibles para este centro.")
        return  # No mostrar el mapa si no hay datos disponibles

    latitud = centro_df['latitud'].values[0]
    longitud = centro_df['longitud'].values[0]
    entidad_administra = centro_df['entidad_administra'].values[0]

    mapa = folium.Map(location=[latitud, longitud], zoom_start=15)
    folium.Marker([latitud, longitud], popup=centro_seleccionado).add_to(mapa)

    # Mostrar el mapa
    st_folium(mapa, width=700, height=500)

    # Mostrar la entidad administradora con un margen inferior
    st.markdown(f"""
        <div style="background-color: #e9c46a; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
            <h3 style="color: #264653; text-align: center;">Entidad Administradora: {entidad_administra}</h3>
        </div>
    """, unsafe_allow_html=True)


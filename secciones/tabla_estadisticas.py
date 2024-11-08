# secciones/tabla_estadisticas.py
import streamlit as st
import pandas as pd
import folium
import numpy as np
import plotly.express as px
from folium.plugins import HeatMap
import streamlit as st

def generar_tabla_estadisticas(df3, region_seleccionada, provincia_seleccionada, distrito_seleccionado):
    if df3.empty:
        st.warning("No hay datos disponibles para mostrar estadísticas.")
        return  # No mostrar tabla si no hay datos disponibles

    # Añadir la sección de estadísticas con fondo
    st.subheader("Estadísticas Resumidas")
    
    # Crear el diccionario con las estadísticas
    estadisticas = {
        "Total de Centros en Región": df3[df3['region'] == region_seleccionada].shape[0],
        "Total de Centros en Provincia": df3[(df3['region'] == region_seleccionada) & (df3['provincia'] == provincia_seleccionada)].shape[0],
        "Total de Centros en Distrito": df3[(df3['region'] == region_seleccionada) & (df3['provincia'] == provincia_seleccionada) & (df3['distrito'] == distrito_seleccionado)].shape[0]
    }

    # Añadir métricas solo si hay valores para mostrar
    for key, value in estadisticas.items():
        if value > 0:
            st.metric(label=key, value=value)

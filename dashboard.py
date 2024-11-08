# dashboard.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
#import folium
import numpy as np
#import plotly.express as px
#from streamlit_folium import st_folium
from secciones.mapa_ubicacion import generar_mapa_ubicacion
from secciones.tabla_estadisticas import generar_tabla_estadisticas
#from folium.plugins import MarkerCluster


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

#Funcion definir conversión de datos de edad_anio en un rango menos extenso
def convertir_edad_anio(x1,y1):
  edad_anio=""
  x = int(x1)
  y = int(y1)
  if y != -1:
    if x >= 0 and y >= 0 and x<16 and y<16:
      edad_anio="0 - 15"
    elif x >= 16 and y >= 16 and x<25 and y<25:
      edad_anio="16 - 24"
    elif x >= 25 and y >= 25 and x<50 and y<50:
      edad_anio="25 - 49"
    elif x >= 50 and y >= 50 and x<80 and y<80:
      edad_anio="50 - 79"
    elif x >= 80 and y >= 80 :
      edad_anio="80+"
  else:
    if x >= 0 and x<16:
      edad_anio="0 - 15"
    elif x >= 16 and x<25:
      edad_anio="16 - 24"
    elif x >= 25 and x<50:
      edad_anio="25 - 49"
    elif x >= 50  and x<80 :
      edad_anio="50 - 79"
    elif x >= 80 :
      edad_anio="80+"
  return edad_anio
#Definicion de funciones filtro previo a la conversion del rango de año
def convertir_ea_prefiltro(var):
  x="-1"
  y="-1"
  if '-' in var:
      x,y=var.split('-')
  else:
    if '+' in var:
      x=var.replace('+','')
    else:
      x=var
  return convertir_edad_anio(x,y)
#Fin de funciones
# Carga de datos
@st.cache_data(show_spinner=False)
def cargar_datos():
    df = pd.read_csv("TB_CENTRO_VACUNACION.csv", sep=";")
    df1 = df.copy()
    df1.rename(columns={'nombre': 'Centro_vacunacion'}, inplace=True)
    df1.drop(['id_centro_vacunacion', 'id_eess'], axis=1, inplace=True)
    df1.replace('', np.nan, inplace=True)
    df1['entidad_administra'] = df1['entidad_administra'].fillna('OTROS')
    valores_comparacion = ["MINSA", "ESSALUD", "PRIVADO","DIRESA", "OTROS"]
    df1.loc[~df1['entidad_administra'].isin(valores_comparacion), 'entidad_administra'] = "OTROS"
    df_ubigeo = pd.read_csv("TB_UBIGEOS.csv", sep=";")
    df_ub = df_ubigeo[['id_ubigeo', 'provincia', 'distrito', 'region','ubigeo_inei','ubigeo_reniec']]
    df3 = pd.merge(df1, df_ub, on='id_ubigeo', how='left')
    df3 = df3[(df3['latitud'] != 0) & (df3['longitud'] != 0)]
    return df3
def cargar_datos_inei():
    #Tratamiento de Datos del dataframe de poblacion de acuerdo a inei
    df_inei=pd.read_csv("TB_POBLACION_INEI.csv", sep=";")
    df_inei['Edad_Anio'] = df_inei['Edad_Anio'].astype(str)
    df_inei['Edad_Anio'] = df_inei['Edad_Anio'].apply(convertir_ea_prefiltro)
    df_inei.to_csv("TB_INEI_POBLACION.csv", sep=",")
    return df_inei
df3 = cargar_datos()
df_inei = cargar_datos_inei()
ubigeo_reniec= 0
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
    distritos_filtrados = df3[(df3['region'] == region_seleccionada) & 
                              (df3['provincia'] == provincia_seleccionada)]['distrito'].unique()
    distrito_opciones = ["Seleccione una opción"] + sorted(distritos_filtrados.tolist())
    distrito_seleccionado = st.sidebar.selectbox("Seleccione el distrito", options=distrito_opciones)

# Filtrar centros de vacunación según distrito
if distrito_seleccionado != "Seleccione una opción":
    entidad_administradora ="OTROS"
    options = ["OTROS","MINSA", "ESSALUD", "PRIVADO", "DIRESA"]
    default_index = options.index("OTROS")
    entidad_administradora = st.radio(
        "Seleccione la entidad administradora",
        options=options,
        index=default_index  # Establecer "OTROS" como opción predeterminada
    )
    centros_filtrados = df3[(df3['region'] == region_seleccionada) &
                            (df3['provincia'] == provincia_seleccionada) & 
                            (df3['entidad_administra'] == entidad_administradora) &
                            (df3['distrito'] == distrito_seleccionado)]['Centro_vacunacion'].unique()
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
        centro_df = df3[df3['Centro_vacunacion'] == centro_seleccionado]
        ubigeo_reniec=centro_df[(centro_df['region'] == region_seleccionada) & 
                                (centro_df['provincia'] == provincia_seleccionada) & 
                                (centro_df['distrito'] == distrito_seleccionado)]['ubigeo_reniec'].values[0]
        df_inei_by = df_inei[df_inei['ubigeo_reniec'] == ubigeo_reniec]
        df_inei_by = df_inei_by.sort_values(by='Edad_Anio')
        generar_mapa_ubicacion(df3, centro_df, centro_seleccionado)
        titulo_grafico = "Total de Poblacion del Distrito: " +  distrito_seleccionado
        plt.title(titulo_grafico)
        sns.barplot(x='Edad_Anio', y='Cantidad', data=df_inei_by, errorbar=None, hue='Sexo')
        plt.xlabel('Edad (Rangos de Edad) agrupados por Sexo')
        plt.ylabel('Poblacion') 
        st.pyplot(plt)
        generar_tabla_estadisticas(df3, region_seleccionada, provincia_seleccionada, distrito_seleccionado)
else:
    st.markdown("""
        <div style="background-color: #f9c74f; padding: 15px; border-radius: 5px; font-size: 18px; text-align: center; color: #333;">
            <strong>Selecciona un centro de vacunación para ver la información.</strong>
        </div>
    """, unsafe_allow_html=True)

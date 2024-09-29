import streamlit as st
import pandas as pd

# Función para cargar el archivo Excel
def load_excel(file):
    df = pd.read_excel(file)
    return df

# Interfaz de la aplicación
st.title('Filtrar Ciudades por País')

# Subir el archivo Excel
uploaded_file = st.file_uploader("Sube un archivo Excel", type=["xlsx"])

if uploaded_file:
    # Leer el archivo Excel
    df = load_excel(uploaded_file)
    
    # Mostrar una vista previa del archivo
    st.write("Vista previa del archivo cargado:")
    st.write(df.head())
    
    # Seleccionar un país de la lista
    paises = df.iloc[:, 0].unique()  # Obtener lista única de países
    pais_seleccionado = st.selectbox("Selecciona un país", paises)
    
    # Filtrar las ciudades del país seleccionado
    ciudades = df[df.iloc[:, 0] == pais_seleccionado].iloc[:, 1]
    
    # Mostrar las ciudades del país seleccionado
    st.write(f"Ciudades de {pais_seleccionado}:")
    st.write(ciudades)


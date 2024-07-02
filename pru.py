import streamlit as st
import pandas as pd
import pyodbc
from datetime import datetime, timedelta

# Función para conectarse a BD y ejecutar una consulta
def execute_query(query):
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=" + st.secrets["server"] + ";"
        "DATABASE=" + st.secrets["database"] + ";"
        "UID=" + st.secrets["username"] + ";"
        "PWD=" + st.secrets["password"] + ";"
    )
    df = pd.read_sql(query, conn)
    conn.close()
    return df
    
#Título de la aplicación 
st.title("Visualización")

#Consulta SQL
query = f"""
    select 
    IdmaeAnexo_Cliente, 
    NommaeAnexoCliente 
    from maeAnexoCliente
            
    """

# Ejecutar la consulta
df = execute_query(query)

# Artificio para quitar la columna que numera las filas
df = df.set_index(df.columns[0])

# Mostrar el número de registros
st.write(f"Número de registros: {len(df)}")

# Mostrar el resultado en formato de tabla
st.dataframe(df)




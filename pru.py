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
    SELECT  
        IdmaeAnexo_Cliente, 
        NommaeAnexoCliente 
        FROM maeAnexoCliente
    """
    
# Ejecutar la consulta y mostrar los resultados
df = execute_query(query)
st.dataframe(df)




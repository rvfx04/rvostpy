import streamlit as st
import pandas as pd
import pyodbc
from datetime import datetime, timedelta

# Función para conectar a la base de datos
def get_connection():
    try:
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=" + st.secrets["server"] + ";"
            "DATABASE=" + st.secrets["database"] + ";"
            "UID=" + st.secrets["username"] + ";"
            "PWD=" + st.secrets["password"] + ";"
        )
        return conn
    except Exception as e:
        st.error(f"Error al conectar a la base de datos: {e}")
        return None
        
def get_data():
    conn = get_connection()
    
    query = f"""


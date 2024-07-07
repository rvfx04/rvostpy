import streamlit as st
import pyodbc
import pandas as pd

# Inicializar conexion
#@st.cache_resource
def init_connection():
    return pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};SERVER="
        + st.secrets["server"]+ ";DATABASE="+ st.secrets["database"]+ ";UID="
        + st.secrets["username"]+ ";PWD="+ st.secrets["password"])

conn = init_connection()

# Se hace la consulta
#@st.cache_data(ttl=600)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        columns = [column[0] for column in cur.description]
        data = cur.fetchall()
    return columns, data

columns, rows = run_query("SELECT * from defecto;")

# Asegúrese de que las filas sean tuplas
rows = [tuple(row) for row in rows]
# Convertir datos a un DataFrame de pandas
df = pd.DataFrame(rows, columns=columns)
# Artificio para anular la columna que numera las filas
#df = df.set_index(df.columns[0])

# Obtener valores únicos del campo 'idgrupodefecto'
unique_idgrupodefecto = df['idgrupodefecto'].unique()

# Crear un multiselect para escoger los valores del campo 'idgrupodefecto'
selected_idgrupodefecto = st.multiselect('Seleccione idgrupodefecto:', unique_idgrupodefecto)

# Filtrar el DataFrame según los valores seleccionados
if selected_idgrupodefecto:
    filtered_df = df[df['idgrupodefecto'].isin(selected_idgrupodefecto)]
else:
   filtered_df = df

# Mostrar el DataFrame filtrado
st.dataframe(filtered_df, hide_index=True)
#st.dataframe(df) 

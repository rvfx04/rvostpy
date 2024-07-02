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
        c.CoddocOrdenProduccion AS PARTIDA,
        c.nvDocumentoReferencia AS REF_PEDIDO,
        a.CoddocOrdenProduccionCalidad AS REPORTE,
        b.CodmaeItemInventario AS CODIGO,
        b.NommaeItemInventario AS TELA,
        d.nommaecolor AS COLOR,
        a.ntDescripcionAcabado AS ACABADO,
        a.dAnchoAcabado AS ANCHO_ACABADO,
        a.AATCC135_EncogLargo AS ENCOG_LARGO,
        a.AATCC135_EncogAncho AS ENCOG_ANCHO,
        a.AATCC179_ReviradoLavado AS REVIRADO,
        a.AATCC179_DensidadAcabada AS DENSIDAD,
        a.nvTituloObservacion AS OBSERV1,
        a.ntObservacion AS OBSERV2,
        CONVERT(DATE,a.dtFechaReporte) AS FECH_REPORTE,
        e.NommaeAnexoCliente AS CLIENTE
    FROM 
        [GarmentData].[dbo].[docOrdenProduccionCalidad] a
    INNER JOIN 
        maeItemInventario b ON a.idmaeitem = b.IdmaeItem_Inventario
    INNER JOIN 
        docOrdenProduccion c ON a.IdDocumento_OrdenProduccion = c.IdDocumento_OrdenProduccion
    INNER JOIN 
        maecolor d ON c.IdmaeColor = d.idmaecolor
    INNER JOIN 
        maeAnexoCliente e ON e.IdmaeAnexo_Cliente = c.IdmaeAnexo_Cliente
   
    """
    
# Ejecutar la consulta y mostrar los resultados
df = execute_query(query)
st.dataframe(df)




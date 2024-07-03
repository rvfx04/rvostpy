import streamlit as st
import pandas as pd
import pyodbc
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

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
         a.CoddocOrdenVenta AS PEDIDO,
            CASE WHEN ISDATE(a.dtFechaEmision) = 1 THEN CONVERT(DATE, a.dtFechaEmision) ELSE NULL END AS F_EMISION,
            CASE WHEN ISDATE(a.dtFechaEntrega) = 1 THEN CONVERT(DATE, a.dtFechaEntrega) ELSE NULL END AS F_ENTREGA,
            SUBSTRING(b.NommaeAnexoCliente,1,15) AS CLIENTE,
            a.nvDocumentoReferencia AS PO,
            CONVERT(INT, a.dCantidad) AS UNID,
            --CONVERT(INT, a.dCantidadProducido) AS UNID_PRODUC,
            CONVERT(INT, COALESCE(d.KG, 0)) AS KG_REQ,
            CONVERT(INT, KG_ARM) AS KG_ARM,
            CONVERT(INT, KG_TEÑIDOS) AS KG_TEÑIDOS,
            CONVERT(INT, KG_PRODUC) AS KG_PRODUC
        FROM docOrdenVenta a
        INNER JOIN maeAnexoCliente b ON a.IdmaeAnexo_Cliente = b.IdmaeAnexo_Cliente
        LEFT JOIN (
            SELECT
                c.IdDocumento_Referencia AS PEDIDO,
                SUM(c.dCantidad) AS KG
            FROM docOrdenVentaItem c
            WHERE c.IdDocumento_Referencia > 0
            GROUP BY c.IdDocumento_Referencia
        ) d ON a.IdDocumento_OrdenVenta = d.PEDIDO
        LEFT JOIN (
            SELECT
                x.IdDocumento_Referencia AS PEDIDO,
                SUM(y.dCantidadProgramado) AS KG_ARM,
                SUM(z.bcerrado * y.dCantidadRequerido) AS KG_PRODUC,
                SUM(s.bcerrado * y.dCantidadProgramado) AS KG_TEÑIDOS
            FROM docOrdenProduccionItem y
            INNER JOIN docOrdenProduccion z ON y.IdDocumento_OrdenProduccion = z.IdDocumento_OrdenProduccion
            INNER JOIN docOrdenVentaItem x ON (z.IdDocumento_Referencia = x.IdDocumento_OrdenVenta AND y.idmaeItem = x.IdmaeItem)
            INNER JOIN docOrdenProduccionRuta s ON y.IdDocumento_OrdenProduccion = s.IdDocumento_OrdenProduccion
            WHERE
                s.IdmaeReceta > 0
            GROUP BY x.IdDocumento_Referencia
        ) t ON a.IdDocumento_OrdenVenta = t.PEDIDO
        WHERE
            a.IdtdDocumentoForm = 10
            AND a.IdtdTipoVenta = 4 AND a.bAnulado = 0
            AND (CASE WHEN ISDATE(a.dtFechaEntrega) = 1 THEN CONVERT(DATE, a.dtFechaEntrega) ELSE NULL END) BETWEEN '01-07-2024' AND '31-08-2024'
                      
    """

# Ejecutar la consulta
df = execute_query(query)


# Definir los filtros en el sidebar
with st.sidebar:
    start_date = st.date_input("Fecha de entrega - Desde", datetime(2024, 7, 1))
    end_date = st.date_input("Fecha de entrega - Hasta", datetime(2024, 8, 31))
    cliente = st.text_input("Cliente", "")
    pedido = st.text_input("Pedido", "")
    po = st.text_input("PO", "")
    

# Aplicar filtros al DataFrame
filtered_df = df.loc[df["CLIENTE"].astype(str).str.contains(cliente, case=False) 
                 & df["PEDIDO"].astype(str).str.contains(pedido, case=False) 
                 & df["PO"].astype(str).str.contains(po, case=False) 
                 & (df["F_ENTREGA"] >= start_date) & (df["F_ENTREGA"] <= end_date)]

with st.expander("Resultados"):
    st.write(f"Número de registros: {len(filtered_df)}")
    st.dataframe(filtered_df)

 


#cliente = sorted(df["CLIENTE"].unique())

#columns= st.columns(1)
#sidebar= st.sidebar

#with sidebar:
    #client = st.multiselect("Cliente", options=cliente, default=cliente)



#with columns[0]:
    
    #f_df = df.loc[df["CLIENTE"].isin(client)]
    #st.write(f"Número de registros: {len(f_df)}")
    # Calcular totales
    #totals = f_df.sum(numeric_only=True)
    #totals['CLIENTE'] = 'TOTAL' # La etiqueta de TOTAL la coloca al final de la columna CLIENTE
    #totals_df = pd.DataFrame(totals).transpose()
    #filtered_df = pd.concat([f_df, totals_df], ignore_index=True)
    # Quita la columna que numera los registros
    #f_df = f_df.set_index(df.columns[0])
    #st.dataframe(f_df, use_container_width = True)


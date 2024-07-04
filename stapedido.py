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
            CONVERT(INT,COALESCE(d.KG, 0) *1.09 - KG_ARM) AS KG_X_ARM,
            CONVERT(INT, KG_TEÑIDOS) AS KG_TEÑIDOS,
            CONVERT(INT,KG_ARM - KG_TEÑIDOS) AS KG_ARM_X_TEÑIR,
            CONVERT(INT, KG_PRODUC) AS KG_PRODUC,
            --CONVERT(INT,COALESCE(d.KG, 0)- KG_PRODUC) AS KG_X_PRODUC
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
            AND (CASE WHEN ISDATE(a.dtFechaEntrega) = 1 THEN CONVERT(DATE, a.dtFechaEntrega) ELSE NULL END) BETWEEN '01-01-2024' AND '31-12-2025'
            
    """

# Ejecutar la consulta
df = execute_query(query)
st.dataframe(df, hide_index=True)

"""
# Fecha de inicio y fin por defecto al inicio y fin del mes actual
today = datetime.today()
start_date_default = today.replace(day=1)
end_date_default = (start_date_default + timedelta(days=32)).replace(day=1) - timedelta(days=1)

columns= st.columns(1)

# Definir los filtros en el sidebar
with st.sidebar:
    st.sidebar.header("Progreso de los Pedidos")
    start_date = st.date_input("Fecha de entrega - Desde", start_date_default)
    end_date = st.date_input("Fecha de entrega - Hasta",end_date_default )
    cliente = st.text_input("Cliente", "")
    pedido = st.text_input("Pedido", "")
    po = st.text_input("PO", "")

    # Botón para aplicar filtros y mostrar resultados
    if st.button("Aplicar Filtros"):
        # Aplicar filtros al DataFrame
        filtered_df = df.loc[df["CLIENTE"].astype(str).str.contains(cliente, case=False) 
                         & df["PEDIDO"].astype(str).str.contains(pedido, case=False) 
                         & df["PO"].astype(str).str.contains(po, case=False) 
                         & (df["F_ENTREGA"] >= start_date) & (df["F_ENTREGA"] <= end_date)]

        totals = filtered_df.select_dtypes(include=["int", "float"]).sum().rename("Total")
        totals_df = pd.DataFrame(totals).T
        filtered_df = pd.concat([filtered_df, totals_df], ignore_index=True)
        with columns[0]:
            st.write(f"Número de registros: {len(filtered_df)-1}")
            st.dataframe(filtered_df, hide_index=True)
            
            #filtered_df = df.loc[:, ['PEDIDO', 'CLIENTE']]
           
    else:
        with columns[0]:
            st.write("Por favor, aplica los filtros para ver resultados.")
"""

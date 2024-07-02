import streamlit as st
import pandas as pd
import pyodbc
from datetime import datetime, timedelta

# Función para conectar a la base de datos
@st.cache_data(ttl=600)
def get_connection():
    
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=" + st.secrets["server"] + ";"
        "DATABASE=" + st.secrets["database"] + ";"
        "UID=" + st.secrets["username"] + ";"
        "PWD=" + st.secrets["password"] + ";"
    )
    return conn

# Función para cargar datos de la base de datos
@st.cache_data(ttl=600)
def load_data(start_date, end_date, pedido, cliente, po):
    query = f"""
    SELECT
        a.CoddocOrdenVenta AS PEDIDO,
        CONVERT(DATE, a.dtFechaEmision) AS F_EMISION,
        CONVERT(DATE, a.dtFechaEntrega) AS F_ENTREGA,
        b.NommaeAnexoCliente AS CLIENTE,
        a.nvDocumentoReferencia AS PO,
        CONVERT(INT, a.dCantidad) AS UNID,
        CONVERT(INT, a.dCantidadProducido) AS UNID_PRODUC,
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
        AND a.IdtdTipoVenta = 4
        AND a.dtFechaEntrega BETWEEN '{start_date}' AND '{end_date}'
        AND a.CoddocOrdenVenta LIKE '%{pedido}%'
        AND b.NommaeAnexoCliente LIKE '%{cliente}%'
        AND a.nvDocumentoReferencia LIKE '%{po}%'
    """
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Configuración de filtros en el sidebar
st.sidebar.header("Filtros")

# Fecha de inicio y fin por defecto al inicio y fin del mes actual
today = datetime.today()
start_date_default = today.replace(day=1)
end_date_default = (start_date_default + timedelta(days=32)).replace(day=1) - timedelta(days=1)

start_date = st.sidebar.date_input("Fecha de inicio", start_date_default)
end_date = st.sidebar.date_input("Fecha de fin", end_date_default)

pedido = st.sidebar.text_input("Pedido")
cliente = st.sidebar.text_input("Cliente")
po = st.sidebar.text_input("PO")

# Botón para aplicar filtros
if st.sidebar.button("Aplicar filtros"):
    data = load_data(start_date, end_date, pedido, cliente, po)
    st.dataframe(data)
else:
    st.write("Por favor, aplica los filtros para ver los resultados.")

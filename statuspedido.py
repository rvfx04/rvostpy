import streamlit as st
import pandas as pd
import pyodbc
from datetime import datetime, timedelta

st.set_page_config(layout="wide")


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

# Función para cargar datos de la base de datos
#@st.cache_data(ttl=600)
def load_data(start_date, end_date, pedido, cliente, po):
    try:
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
            CONVERT(INT, KG_PRODUC) AS KG_DESPACH,
            CONVERT(INT,COALESCE(d.KG, 0)- KG_PRODUC) AS KG_X_DESPACH,
            KG_PRODUC/COALESCE(d.KG, 0)*100 AS R
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
            AND (CASE WHEN ISDATE(a.dtFechaEntrega) = 1 THEN CONVERT(DATE, a.dtFechaEntrega) ELSE NULL END) BETWEEN '{start_date}' AND '{end_date}'
            AND a.CoddocOrdenVenta LIKE '%{pedido}%'
            AND b.NommaeAnexoCliente LIKE '%{cliente}%'
            AND a.nvDocumentoReferencia LIKE '%{po}%'
        """
        conn = get_connection()
        if conn:
            df = pd.read_sql(query, conn)
            
            conn.close()
            return df
        else:
            st.error("No se pudo establecer la conexión con la base de datos.")
            return pd.DataFrame()  # Devolver un DataFrame vacío en caso de error
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return pd.DataFrame()  # Devolver un DataFrame vacío en caso de error

# Configuración de filtros en el sidebar
st.sidebar.header("Progreso de los Pedidos")

# Fecha de inicio y fin por defecto al inicio y fin del mes actual
today = datetime.today()
start_date_default = today.replace(day=1)
end_date_default = (start_date_default + timedelta(days=32)).replace(day=1) - timedelta(days=1)

start_date = st.sidebar.date_input("Fecha de entrega: Desde", start_date_default)
end_date = st.sidebar.date_input("Fecha de entrega: Hasta", end_date_default)

pedido = st.sidebar.text_input("Pedido")
cliente = st.sidebar.text_input("Cliente")
po = st.sidebar.text_input("PO")

# Botón para aplicar filtros
if st.sidebar.button("Aplicar filtros"):
    
    data = load_data(start_date, end_date, pedido, cliente, po)
    
    totals = data.select_dtypes(include=["int", "float"]).sum().rename("Total")
    totals_df = pd.DataFrame(totals).T
    data1 = pd.concat([data, totals_df], ignore_index=True)
    columns_to_show = ['PEDIDO','F_EMISION', 'F_ENTREGA','CLIENTE','PO','UNID','KG_REQ','KG_ARM','KG_TEÑIDOS','KG_DESPACH','R']
    st.write(f"Número de Pedidos: {len(data1)-1}")
    st.dataframe(data1[columns_to_show], hide_index=True)
    if not data1.empty:
        
        kgxarm_df = data.loc[data['KG_X_ARM'] > 0]
        totals = kgxarm_df.select_dtypes(include=["int", "float"]).sum().rename("Total")
        totals_df = pd.DataFrame(totals).T
        kgxarm_df = pd.concat([kgxarm_df, totals_df], ignore_index=True)
        columns_to_show = ['PEDIDO', 'F_ENTREGA','CLIENTE','UNID','KG_REQ','KG_X_ARM']
        st.write(f"Por armar: {len(kgxarm_df)-1} Pedidos")
        st.dataframe(kgxarm_df[columns_to_show], hide_index=True)
        
        kgxtenir_df = data.loc[data['KG_ARM_X_TEÑIR'] > 0]
        totals = kgxtenir_df.select_dtypes(include=["int", "float"]).sum().rename("Total")
        totals_df = pd.DataFrame(totals).T
        kgxtenir_df = pd.concat([kgxtenir_df, totals_df], ignore_index=True)
        columns_to_show = ['PEDIDO', 'F_ENTREGA','CLIENTE','UNID','KG_REQ','KG_ARM_X_TEÑIR']
        st.write(f"Por teñir lo armado: {len(kgxtenir_df)-1} Pedidos")
        st.dataframe(kgxtenir_df[columns_to_show], hide_index=True)
        
        #kgproduc_df = data.loc[data['KG_X_DESPACH'] / data['KG_REQ'] * 100> 98]
        #kgproduc_df = data.loc[data['KG_X_DESPACH'].astype(float) / data['KG_REQ'].astype(float) > 0.975]
        kgproduc_df = data.loc[data['R'] < 97.5]
       
        totals = kgproduc_df.select_dtypes(include=["int", "float"]).sum().rename("Total")
        totals_df = pd.DataFrame(totals).T
        kgproduc_df = pd.concat([kgproduc_df, totals_df], ignore_index=True)
        columns_to_show = ['PEDIDO', 'F_ENTREGA','CLIENTE','UNID','KG_REQ','KG_DESPACH','KG_X_DESPACH','R']
        st.write(f"Por Despachar: {len(kgproduc_df)-1} Pedidos")
        st.dataframe(kgproduc_df[columns_to_show], hide_index=True)

    else:
        st.write("No se encontraron datos con los filtros aplicados.")
else:
    st.write("Por favor, aplica los filtros para ver los resultados.")


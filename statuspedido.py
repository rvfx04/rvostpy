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
      WITH cte_produccion AS (
    SELECT 
        g.CoddocOrdenVenta,
        ISNULL(programado.PROG, 0) AS PROG,
        ISNULL(cortado.CORTADO, 0) AS CORTADO,
        ISNULL(cosido.COSIDO, 0) AS COSIDO
    FROM dbo.docOrdenVenta g
    LEFT JOIN (
        SELECT 
            g.IdDocumento_OrdenVenta,
            SUM(a.dCantidadProgramado) AS PROG
        FROM dbo.docOrdenProduccion c WITH (NOLOCK)
        INNER JOIN dbo.docOrdenProduccionItem a WITH (NOLOCK)
            ON c.IdDocumento_OrdenProduccion = a.IdDocumento_OrdenProduccion
        INNER JOIN dbo.docOrdenVenta g WITH (NOLOCK)
            ON c.IdDocumento_Referencia = g.IdDocumento_OrdenVenta
        INNER JOIN dbo.docOrdenProduccionRuta b WITH (NOLOCK)
            ON c.IdDocumento_OrdenProduccion = b.IdDocumento_OrdenProduccion
        INNER JOIN dbo.maeCentroCosto d WITH (NOLOCK)
            ON b.IdmaeCentroCosto = d.IdmaeCentroCosto
            AND d.bConOrdenProduccion = 1
        WHERE c.bCerrado = 0
            AND c.bAnulado = 0
            AND c.IdtdDocumentoForm = 127
            AND b.IdmaeCentroCosto = 29
        GROUP BY g.IdDocumento_OrdenVenta
    ) AS programado
    ON g.IdDocumento_OrdenVenta = programado.IdDocumento_OrdenVenta
    LEFT JOIN (
        SELECT 
            g.IdDocumento_OrdenVenta,
            SUM(b.dCantidadIng) AS CORTADO
        FROM dbo.docNotaInventario a WITH (NOLOCK)
        INNER JOIN dbo.maeCentroCosto a1 WITH (NOLOCK)
            ON a.IdmaeCentroCosto = a1.IdmaeCentroCosto
            AND a1.bConOrdenProduccion = 1
        INNER JOIN dbo.docNotaInventarioItem b WITH (NOLOCK)
            ON a.IdDocumento_NotaInventario = b.IdDocumento_NotaInventario
            AND b.dCantidadIng <> 0
        INNER JOIN dbo.docOrdenProduccion c WITH (NOLOCK)
            ON a.IdDocumento_OrdenProduccion = c.IdDocumento_OrdenProduccion
            AND c.bCerrado = 0
            AND c.bAnulado = 0
            AND c.IdtdDocumentoForm = 127
        INNER JOIN dbo.docOrdenVenta g WITH (NOLOCK)
            ON c.IdDocumento_Referencia = g.IdDocumento_OrdenVenta
        INNER JOIN dbo.docOrdenProduccionRuta d WITH (NOLOCK)
            ON a.IddocOrdenProduccionRuta = d.IddocOrdenProduccionRuta
        INNER JOIN dbo.docOrdenProduccionItem e WITH (NOLOCK)
            ON c.IdDocumento_OrdenProduccion = e.IdDocumento_OrdenProduccion
            AND b.IdmaeItem_Inventario = e.IdmaeItem
        INNER JOIN dbo.maeItemInventario f WITH (NOLOCK)
            ON b.IdmaeItem_Inventario = f.IdmaeItem_Inventario
            AND f.IdtdItemForm = 10
        WHERE a.IdtdDocumentoForm = 131
            AND a.bDevolucion = 0
            AND a.bDesactivado = 0
            AND a.bAnulado = 0
            AND a.IdDocumento_OrdenProduccion <> 0
            AND a.IdmaeCentroCosto = 29
        GROUP BY g.IdDocumento_OrdenVenta
    ) AS cortado
    ON g.IdDocumento_OrdenVenta = cortado.IdDocumento_OrdenVenta
    LEFT JOIN (
        SELECT 
            g.IdDocumento_OrdenVenta,
            SUM(b.dCantidadIng) AS COSIDO
        FROM dbo.docNotaInventario a WITH (NOLOCK)
        INNER JOIN dbo.maeCentroCosto a1 WITH (NOLOCK)
            ON a.IdmaeCentroCosto = a1.IdmaeCentroCosto
            AND a1.bConOrdenProduccion = 1
        INNER JOIN dbo.docNotaInventarioItem b WITH (NOLOCK)
            ON a.IdDocumento_NotaInventario = b.IdDocumento_NotaInventario
            AND b.dCantidadIng <> 0
        INNER JOIN dbo.docOrdenProduccion c WITH (NOLOCK)
            ON a.IdDocumento_OrdenProduccion = c.IdDocumento_OrdenProduccion
            AND c.bCerrado = 0
            AND c.bAnulado = 0
            AND c.IdtdDocumentoForm = 127
        INNER JOIN dbo.docOrdenVenta g WITH (NOLOCK)
            ON c.IdDocumento_Referencia = g.IdDocumento_OrdenVenta
        INNER JOIN dbo.docOrdenProduccionRuta d WITH (NOLOCK)
            ON a.IddocOrdenProduccionRuta = d.IddocOrdenProduccionRuta
        INNER JOIN dbo.docOrdenProduccionItem e WITH (NOLOCK)
            ON c.IdDocumento_OrdenProduccion = e.IdDocumento_OrdenProduccion
            AND b.IdmaeItem_Inventario = e.IdmaeItem
        INNER JOIN dbo.maeItemInventario f WITH (NOLOCK)
            ON b.IdmaeItem_Inventario = f.IdmaeItem_Inventario
            AND f.IdtdItemForm = 10
        WHERE a.IdtdDocumentoForm = 131
            AND a.bDevolucion = 0
            AND a.bDesactivado = 0
            AND a.bAnulado = 0
            AND a.IdDocumento_OrdenProduccion <> 0
            AND a.IdmaeCentroCosto = 47
        GROUP BY g.IdDocumento_OrdenVenta
    ) AS cosido
    ON g.IdDocumento_OrdenVenta = cosido.IdDocumento_OrdenVenta
)
SELECT
    a.CoddocOrdenVenta AS PEDIDO,
    CASE WHEN ISDATE(a.dtFechaEmision) = 1 THEN CONVERT(DATE, a.dtFechaEmision) ELSE NULL END AS F_EMISION,
    CASE WHEN ISDATE(a.dtFechaEntrega) = 1 THEN CONVERT(DATE, a.dtFechaEntrega) ELSE NULL END AS F_ENTREGA,
    CONVERT(INT, a.dtFechaEntrega - a.dtFechaEmision) AS DIAS,
    SUBSTRING(b.NommaeAnexoCliente, 1, 15) AS CLIENTE,
    a.nvDocumentoReferencia AS PO,
    CONVERT(INT, a.dCantidad) AS UNID,
    CONVERT(INT, COALESCE(d.KG, 0)) AS KG_REQ,
    CONVERT(INT, KG_ARM) AS KG_ARM,
    CONVERT(INT, COALESCE(d.KG, 0) * 1.075 - KG_ARM) AS KG_X_ARM,
    CONVERT(INT, KG_TEÑIDOS) AS KG_TEÑIDOS,
    CONVERT(INT, KG_ARM - KG_TEÑIDOS) AS KG_ARM_X_TEÑIR,
    CONVERT(INT, KG_PRODUC) AS KG_DESPACH,
    CONVERT(INT, KG_APROB_D) AS KG_APROB_D,
    CONVERT(INT, COALESCE(d.KG, 0) - KG_PRODUC) AS KG_X_DESPACH,
    KG_PRODUC / COALESCE(d.KG, 0) * 100 AS R,
    FORMAT(KG_ARM / COALESCE(d.KG, 0), '0%') AS KG_ARMP,
    CONVERT(INT,cte_produccion.PROG) AS PROG,
    CONVERT(INT,cte_produccion.CORTADO) AS CORTADO,
    CONVERT(INT,cte_produccion.COSIDO) AS COSIDO,
    FORMAT((COALESCE(d.KG, 0) * 1.075 - KG_ARM) / COALESCE(d.KG, 0), '0%') AS KG_X_ARMP,
    FORMAT(KG_TEÑIDOS / COALESCE(d.KG, 0), '0%') AS KG_TEÑIDOSP,
    FORMAT((KG_ARM - KG_TEÑIDOS) / COALESCE(d.KG, 0), '0%') AS KG_ARM_X_TEÑIRP,
    FORMAT(KG_PRODUC / COALESCE(d.KG, 0), '0%') AS KG_DESPACHP,
    FORMAT(KG_APROB_D / COALESCE(d.KG, 0), '0%') AS KG_APROB_DP,
    FORMAT((COALESCE(d.KG, 0) - KG_PRODUC) / COALESCE(d.KG, 0), '0%') AS KG_X_DESPACHP,
    FORMAT(cte_produccion.PROG / a.dCantidad, '0%') AS PROGP,
    FORMAT(cte_produccion.CORTADO / a.dCantidad, '0%') AS CORTADOP,
    FORMAT(cte_produccion.COSIDO / a.dCantidad, '0%') AS COSIDOP



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
        SUM(s.bcerrado * y.dCantidadProgramado) AS KG_TEÑIDOS,
		SUM(z.bCierreAprobado * y.dCantidadProgramado*0.9) AS KG_APROB_D
    FROM docOrdenProduccionItem y
    INNER JOIN docOrdenProduccion z ON y.IdDocumento_OrdenProduccion = z.IdDocumento_OrdenProduccion
    INNER JOIN docOrdenVentaItem x ON (z.IdDocumento_Referencia = x.IdDocumento_OrdenVenta AND y.idmaeItem = x.IdmaeItem)
    INNER JOIN docOrdenProduccionRuta s ON y.IdDocumento_OrdenProduccion = s.IdDocumento_OrdenProduccion
    WHERE s.IdmaeReceta > 0
    GROUP BY x.IdDocumento_Referencia
) t ON a.IdDocumento_OrdenVenta = t.PEDIDO
LEFT JOIN cte_produccion ON a.CoddocOrdenVenta = cte_produccion.CoddocOrdenVenta
WHERE
    a.IdtdDocumentoForm = 10
    AND a.IdtdTipoVenta = 4
    AND a.bAnulado = 0
    
    AND (CASE WHEN ISDATE(a.dtFechaEntrega) = 1 THEN CONVERT(DATE, a.dtFechaEntrega) ELSE NULL END) BETWEEN '{start_date}' AND '{end_date}'
    AND a.CoddocOrdenVenta LIKE '%{pedido}%'
    AND b.NommaeAnexoCliente LIKE '%{cliente}%'
    AND a.nvDocumentoReferencia LIKE '%{po}%'
        ;

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
st.sidebar.header("Progreso de los Pedidos (%)")
st.sidebar.write("Sólo incluye OPs activas")

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
if st.sidebar.button("Aplicar filtro"):
    st.session_state.start_date = start_date
    st.session_state.end_date = end_date
    st.session_state.pedido = pedido
    st.session_state.cliente = cliente
    st.session_state.po = po

    # Cargar los datos con los filtros aplicados
    data = load_data(start_date, end_date, pedido, cliente, po)

    totals = data.select_dtypes(include=["int", "float"]).sum().rename("Total")
    totals_df = pd.DataFrame(totals).T
    data1 = pd.concat([data, totals_df], ignore_index=True)

    # Rellenar los valores 'None' con espacio en blanco
    data1.fillna('', inplace=True)
	
    columns_to_show = ['PEDIDO','F_EMISION', 'F_ENTREGA','DIAS','CLIENTE','PO','KG_REQ','KG_ARMP','KG_TEÑIDOSP','KG_DESPACHP','UNID','PROGP','CORTADOP','COSIDOP']
    st.write(f"Número de Pedidos: {len(data1)-1}")
    st.dataframe(data1[columns_to_show], hide_index=True)
    if not data1.empty:

        # Generación de las tablas adicionales
        
        #kgxarm_df = data.loc[data['KG_X_ARM'] > 0]
        kgxarm_df = data.loc[(data['KG_X_ARM'] > 0) | (data['KG_X_ARM'].isnull())]
        totals = kgxarm_df.select_dtypes(include=["int", "float"]).sum().rename("Total")
        totals_df = pd.DataFrame(totals).T
        kgxarm_df = pd.concat([kgxarm_df, totals_df], ignore_index=True)
	kgxarm_df.fillna('', inplace=True)  
        columns_to_show = ['PEDIDO', 'F_ENTREGA','CLIENTE','UNID','KG_REQ','KG_X_ARMP','KG_ARMP']
        st.write(f"Por armar: {len(kgxarm_df)-1} Pedidos")
        st.dataframe(kgxarm_df[columns_to_show], hide_index=True)
        
        kgxtenir_df = data.loc[data['KG_ARM_X_TEÑIR'] > 0]
        totals = kgxtenir_df.select_dtypes(include=["int", "float"]).sum().rename("Total")
        totals_df = pd.DataFrame(totals).T
        kgxtenir_df = pd.concat([kgxtenir_df, totals_df], ignore_index=True)
        columns_to_show = ['PEDIDO', 'F_ENTREGA','CLIENTE','UNID','KG_REQ','KG_ARM_X_TEÑIRP']
        st.write(f"Por teñir lo armado: {len(kgxtenir_df)-1} Pedidos")
        st.dataframe(kgxtenir_df[columns_to_show], hide_index=True)
        
        #kgproduc_df = data.loc[data['R'] < 97.5]
        kgproduc_df = data.loc[(data['R'] < 97.5) | (data['R'].isnull())]
        totals = kgproduc_df.select_dtypes(include=["int", "float"]).sum().rename("Total")
        totals_df = pd.DataFrame(totals).T
        kgproduc_df = pd.concat([kgproduc_df, totals_df], ignore_index=True)
        columns_to_show = ['PEDIDO', 'F_ENTREGA','CLIENTE','UNID','KG_REQ','KG_DESPACHP','KG_APROB_DP','KG_X_DESPACHP']
        st.write(f"Por Despachar: {len(kgproduc_df)-1} Pedidos")
        
        #filtro_valor = st.number_input('Introduce un valor:', min_value=0)
        
        st.dataframe(kgproduc_df[columns_to_show], hide_index=True)
        
        #filtro_df = kgproduc_df[kgproduc_df['KG_X_DESPACH'] > filtro_valor]
        #st.write(filtro_df[columns_to_show], hide_index=True)

    else:
        st.write("No se  encontraron datos con los filtros aplicados.")
else:
    st.write("Por favor, aplica los filtros para ver los resultados.")

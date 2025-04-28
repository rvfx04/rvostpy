import streamlit as st
import pandas as pd
import pyodbc
from datetime import datetime, timedelta
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder

st.set_page_config(layout="wide")

# Función para configurar opciones de AgGrid
def configure_grid(df, height=400):
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(
        resizable=True, 
        filterable=True, 
        sortable=True, 
        editable=False
    )
    
    # Configuraciones específicas para columnas clave
    if "PEDIDO" in df.columns:
        gb.configure_column("PEDIDO", filter=True, pinned="left")
    if "F_ENTREGA" in df.columns:
        gb.configure_column("F_ENTREGA", filter=True)
    if "CLIENTE" in df.columns:
        gb.configure_column("CLIENTE", filter=True)
    
    # Formato para columnas numéricas
    for col in df.select_dtypes(include=['int', 'float']).columns:
        gb.configure_column(col, type=["numericColumn", "numberColumnFilter"])
    
    # Configuración para fechas
    if "F_ENTREGA" in df.columns:
        gb.configure_column("F_ENTREGA", type=["dateColumnFilter"])
    if "F_EMISION" in df.columns:
        gb.configure_column("F_EMISION", type=["dateColumnFilter"])
    
    grid_options = gb.build()
    
    return AgGrid(
        df,
        gridOptions=grid_options,
        height=height,
        allow_unsafe_jscode=True,
        theme="streamlit",
        fit_columns_on_grid_load=False,
        reload_data=True
    )

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
    FORMAT(KG_ARM / COALESCE(d.KG, 0),'0%' ) AS R1,
    CONVERT(INT,cte_produccion.PROG) AS PROG,
    CONVERT(INT,cte_produccion.CORTADO) AS CORTADO,
    CONVERT(INT,cte_produccion.COSIDO) AS COSIDO
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
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return pd.DataFrame()

# Función para mostrar totales sin errores
def display_totals(df, columns_to_show):
    # Crear un dataframe para los totales solamente con columnas numéricas
    numeric_cols = df.select_dtypes(include=["int", "float"]).columns
    totals = df[numeric_cols].sum().to_frame().T
    
    # Añadir una etiqueta para la fila de totales
    for col in df.columns:
        if col not in numeric_cols:
            if col in totals.columns:
                totals[col] = "Total"
            else:
                totals[col] = "Total"
    
    # Reordenar las columnas según columns_to_show, pero solo incluir las que existen en totals
    available_cols = [col for col in columns_to_show if col in totals.columns]
    st.dataframe(totals[available_cols], hide_index=True)

# Configuración de filtros en el sidebar
st.sidebar.header("Progreso de los Pedidos")
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
    data = load_data(start_date, end_date, pedido, cliente, po)
    
    if not data.empty:
        # Tabla principal
        st.subheader(f"Número de Pedidos: {len(data)}")
        columns_to_show = ['PEDIDO','F_EMISION', 'F_ENTREGA','DIAS','CLIENTE','PO','KG_REQ','KG_ARM','KG_TEÑIDOS','KG_DESPACH','UNID','PROG','CORTADO','COSIDO']
        main_data = data[columns_to_show].copy()
        
        # Mostrar tabla principal interactiva
        configure_grid(main_data)
        
        # Mostrar totales
        st.write("Totales:")
        display_totals(data, columns_to_show)
        
        # Tabla Por armar
        st.subheader("Por armar")
        kgxarm_df = data.loc[(data['KG_X_ARM'] > 0) | (data['KG_X_ARM'].isnull())]
        if not kgxarm_df.empty:
            st.write(f"Por armar: {len(kgxarm_df)} Pedidos")
            columns_to_show = ['PEDIDO', 'F_ENTREGA','CLIENTE','UNID','KG_REQ','KG_X_ARM','R1']
            configure_grid(kgxarm_df[columns_to_show])
            
            # Mostrar totales
            st.write("Totales:")
            display_totals(kgxarm_df, columns_to_show)
        else:
            st.write("No hay pedidos por armar.")
        
        # Tabla Por teñir
        st.subheader("Por teñir lo armado")
        kgxtenir_df = data.loc[data['KG_ARM_X_TEÑIR'] > 0]
        if not kgxtenir_df.empty:
            st.write(f"Por teñir lo armado: {len(kgxtenir_df)} Pedidos")
            columns_to_show = ['PEDIDO', 'F_ENTREGA','CLIENTE','UNID','KG_REQ','KG_TEÑIDOS','KG_ARM_X_TEÑIR']
            configure_grid(kgxtenir_df[columns_to_show])
            
            # Mostrar totales
            st.write("Totales:")
            display_totals(kgxtenir_df, columns_to_show)
        else:
            st.write("No hay pedidos por teñir.")
        
        # Tabla Por Despachar
        st.subheader("Por Despachar")
        kgproduc_df = data.loc[(data['R'] < 97.5) | (data['R'].isnull())]
        if not kgproduc_df.empty:
            st.write(f"Por Despachar: {len(kgproduc_df)} Pedidos")
            columns_to_show = ['PEDIDO', 'F_ENTREGA','CLIENTE','UNID','KG_REQ','KG_DESPACH','KG_APROB_D','KG_X_DESPACH']
            configure_grid(kgproduc_df[columns_to_show])
            
            # Mostrar totales
            st.write("Totales:")
            display_totals(kgproduc_df, columns_to_show)
        else:
            st.write("No hay pedidos por despachar.")
    else:
        st.write("No se encontraron datos con los filtros aplicados.")
else:
    st.write("Por favor, aplica los filtros para ver los resultados.")

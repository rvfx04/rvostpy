import streamlit as st

# Define the functions for each app page
def app_gtop():
    import streamlit as st
import pyodbc
import pandas as pd

# Inicializar conexión
#@st.cache_resource
def init_connection():
    return pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};SERVER="
        + st.secrets["server"]+ ";DATABASE="+ st.secrets["database"]+ ";UID="
        + st.secrets["username"]+ ";PWD="+ st.secrets["password"])
    
# Título de la aplicación
st.title("Progreso de la Orden de Producción")

conn = init_connection()

# Se hace la consulta
#@st.cache_data(ttl=600)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        columns = [column[0] for column in cur.description]
        data = cur.fetchall()
    return columns, data

# Solicitar al usuario el CoddocOrdenProduccion
coddoc_orden_produccion = st.text_input("Ingresa una OP válida:")

if coddoc_orden_produccion:
    query = f"""
    WITH ProduccionPorProceso AS (
        SELECT 
            c.CoddocOrdenProduccion, 
            a.IdDocumento_OrdenProduccion, 
            b.IddocOrdenProduccionRuta,
            b.iSecuencia, 
            b.IdmaeCentroCosto,   
            d.NommaeCentroCosto,
            a.dCantidadRequerido, 
            a.dCantidadProgramado, 
            0 AS dCantidadProducido
        FROM dbo.docOrdenProduccion c WITH (NOLOCK)
        INNER JOIN dbo.docOrdenProduccionItem a WITH (NOLOCK)
            ON c.IdDocumento_OrdenProduccion = a.IdDocumento_OrdenProduccion
        INNER JOIN dbo.docOrdenProduccionRuta b WITH (NOLOCK)
            ON c.IdDocumento_OrdenProduccion = b.IdDocumento_OrdenProduccion
        INNER JOIN dbo.maeCentroCosto d WITH (NOLOCK)
            ON b.IdmaeCentroCosto = d.IdmaeCentroCosto
            AND d.bConOrdenProduccion = 1
        WHERE c.bCerrado = 0
            AND c.bAnulado = 0
            AND c.IdtdDocumentoForm = 127
    ),
    ProducidoPorProceso AS (
        SELECT 
            c.CoddocOrdenProduccion, 
            a.IdDocumento_OrdenProduccion, 
            d.IddocOrdenProduccionRuta,
            d.iSecuencia, 
            a.IdmaeCentroCosto, 
            a1.NommaeCentroCosto,
            0 AS dCantidadRequerido, 
            0 AS dCantidadProgramado,
            b.dCantidadIng AS dCantidadProducido
        FROM dbo.docNotaInventario a WITH (NOLOCK)
        INNER JOIN dbo.maeCentroCosto a1 WITH (NOLOCK)
            ON a.IdmaeCentroCosto = a1.IdmaeCentroCosto
            AND a1.bConOrdenProduccion = 1
        INNER JOIN dbo.docNotaInventarioItem b WITH (NOLOCK)
            ON a.IdDocumento_NotaInventario = b.IdDocumento_NotaInventario
            AND b.dCantidadIng <> 0
        INNER JOIN dbo.docOrdenProduccion c WITH (NOLOCK)
            ON a.IdDocumento_OrdenProduccion = c.IdDocumento_OrdenProduccion
            AND c.bAnulado = 0
            AND c.IdtdDocumentoForm = 127
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
    )
    SELECT 
        sc.CoddocOrdenProduccion AS OP,
        sc.NommaeCentroCosto AS PROCESO,
        SUM(sc.dCantidadRequerido) AS REQUERIDO,
        SUM(sc.dCantidadProgramado) AS PROGRAMADO,
        SUM(sc.dCantidadProducido) AS PRODUCIDO
    FROM (
        SELECT * FROM ProduccionPorProceso
        UNION ALL
        SELECT * FROM ProducidoPorProceso
    ) sc
    WHERE sc.CoddocOrdenProduccion = '{coddoc_orden_produccion}'
    GROUP BY 
        sc.CoddocOrdenProduccion, 
        sc.NommaeCentroCosto,
        sc.IdmaeCentroCosto
    ORDER BY 
        sc.IdmaeCentroCosto ASC;"""
    
    columns, rows = run_query(query)

    if rows:
        # Asegúrese de que las filas sean tuplas
        rows = [tuple(row) for row in rows]
        # Convertir datos a un DataFrame de pandas
        df = pd.DataFrame(rows, columns=columns)
        # Artificio para anular la columna que numera las filas
        df = df.set_index(df.columns[0])

        # Mostrar el DataFrame
        st.dataframe(df)
    else:
        st.write("No se encontraron resultados para la OP ingresada.")
else:
    st.write("")
    pass

def app_gtpedido():
    import streamlit as st
import pyodbc
import pandas as pd

# Inicializar conexión
#@st.cache_resource
def init_connection():
    return pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};SERVER="
        + st.secrets["server"]+ ";DATABASE="+ st.secrets["database"]+ ";UID="
        + st.secrets["username"]+ ";PWD="+ st.secrets["password"])
    
# Título de la aplicación
st.title("Progreso del Pedido")

conn = init_connection()

# Se hace la consulta
#@st.cache_data(ttl=600)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        columns = [column[0] for column in cur.description]
        data = cur.fetchall()
    return columns, data

# Solicitar al usuario el pedido
pedido = st.text_input("Ingresa un Pedido válido:")

if pedido:
    query = f"""
    WITH ProduccionPorProceso AS (
        SELECT 
            c.CoddocOrdenProduccion, 
            g.CoddocOrdenVenta, 
            a.IdDocumento_OrdenProduccion, 
            b.IddocOrdenProduccionRuta,
            b.iSecuencia, 
            b.IdmaeCentroCosto,   
            d.NommaeCentroCosto,
            a.dCantidadRequerido, 
            a.dCantidadProgramado, 
            0 AS dCantidadProducido
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
    ),
    ProducidoPorProceso AS (
        SELECT 
            c.CoddocOrdenProduccion, 
            g.CoddocOrdenVenta,
            a.IdDocumento_OrdenProduccion, 
            d.IddocOrdenProduccionRuta,
            d.iSecuencia, 
            a.IdmaeCentroCosto, 
            a1.NommaeCentroCosto,
            0 AS dCantidadRequerido, 
            0 AS dCantidadProgramado,
            b.dCantidadIng AS dCantidadProducido
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
    )
    SELECT 
        sc.CoddocOrdenVenta AS PEDIDO,
        sc.NommaeCentroCosto AS PROCESO,
        SUM(sc.dCantidadRequerido) AS REQUERIDO,
        SUM(sc.dCantidadProgramado) AS PROGRAMADO,
        SUM(sc.dCantidadProducido) AS PRODUCIDO
    FROM (
        SELECT CoddocOrdenProduccion, CoddocOrdenVenta, IdDocumento_OrdenProduccion, IddocOrdenProduccionRuta,
           iSecuencia, IdmaeCentroCosto, NommaeCentroCosto, dCantidadRequerido, dCantidadProgramado, dCantidadProducido
        FROM ProduccionPorProceso
        UNION ALL
        SELECT CoddocOrdenProduccion, CoddocOrdenVenta, IdDocumento_OrdenProduccion, IddocOrdenProduccionRuta,
           iSecuencia, IdmaeCentroCosto, NommaeCentroCosto, dCantidadRequerido, dCantidadProgramado, dCantidadProducido
        FROM ProducidoPorProceso
    ) sc
    WHERE sc.CoddocOrdenVenta = '{pedido}'
    GROUP BY 
        sc.CoddocOrdenVenta, 
        sc.NommaeCentroCosto
    ORDER BY 
        sc.NommaeCentroCosto ASC

;"""
    
    columns, rows = run_query(query)

    if rows:
        # Asegúrese de que las filas sean tuplas
        rows = [tuple(row) for row in rows]
        # Convertir datos a un DataFrame de pandas
        df = pd.DataFrame(rows, columns=columns)
        # Artificio para anular la columna que numera las filas
        df = df.set_index(df.columns[0])

        # Mostrar el DataFrame
        st.dataframe(df)
    else:
        st.write("No se encontraron resultados para el pedido ingresado.")
else:
    st.write("")
    pass
ainer = st.empty()

# Create a sidebar navigation to switch between the app pages
app_selection = st.sidebar.radio("Selecciona una aplicación", ("GTOP", "GTPedido"))

# Definir la lógica para mostrar la aplicación seleccionada
if app_selection == "GTOP":
    st.page('app_gtop()')
    #app_gtop()
elif app_selection == "GTPedido":
    st.page('app_gtpedido()')
    #app_gtpedido()

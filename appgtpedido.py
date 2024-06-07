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
        a1.IdDocumento_OrdenProduccion, 
        b1.IddocOrdenProduccionRuta,
        b1.iSecuencia, 
        b1.IdmaeCentroCosto,   
        d1.NommaeCentroCosto,
        a1.dCantidadRequerido, 
        a1.dCantidadProgramado, 
        0 AS dCantidadProducido
    FROM dbo.docOrdenProduccion c WITH (NOLOCK)
    INNER JOIN dbo.docOrdenProduccionItem a1 WITH (NOLOCK)
        ON c.IdDocumento_OrdenProduccion = a1.IdDocumento_OrdenProduccion
    INNER JOIN dbo.docOrdenVenta g WITH (NOLOCK)
        ON c.IdDocumento_Referencia = g.IdDocumento_OrdenVenta
    INNER JOIN dbo.docOrdenProduccionRuta b1 WITH (NOLOCK)
        ON c.IdDocumento_OrdenProduccion = b1.IdDocumento_OrdenProduccion
    INNER JOIN dbo.maeCentroCosto d1 WITH (NOLOCK)
        ON b1.IdmaeCentroCosto = d1.IdmaeCentroCosto
        AND d1.bConOrdenProduccion = 1
    INNER JOIN dbo.docNotaInventario a2 WITH (NOLOCK)
        ON a2.IdDocumento_OrdenProduccion = c.IdDocumento_OrdenProduccion
        AND a2.IdtdDocumentoForm = 131
        AND a2.bDevolucion = 0
        AND a2.bDesactivado = 0
        AND a2.bAnulado = 0
    INNER JOIN dbo.docNotaInventarioItem b2 WITH (NOLOCK)
        ON a2.IdDocumento_NotaInventario = b2.IdDocumento_NotaInventario
        AND b2.dCantidadIng <> 0
    INNER JOIN dbo.maeItemInventario f WITH (NOLOCK)
        ON b2.IdmaeItem_Inventario = f.IdmaeItem_Inventario
        AND f.IdtdItemForm = 10
    WHERE c.bCerrado = 0
        AND c.bAnulado = 0
        AND c.IdtdDocumentoForm = 127
),
ProducidoPorProceso AS (
    SELECT 
        c.CoddocOrdenProduccion, 
        g.CoddocOrdenVenta,
        a3.IdDocumento_OrdenProduccion, 
        d3.IddocOrdenProduccionRuta,
        d3.iSecuencia, 
        a3.IdmaeCentroCosto, 
        a4.NommaeCentroCosto,
        0 AS dCantidadRequerido, 
        0 AS dCantidadProgramado,
        b3.dCantidadIng AS dCantidadProducido
    FROM dbo.docOrdenProduccion c WITH (NOLOCK)
    INNER JOIN dbo.docOrdenVenta g WITH (NOLOCK)
        ON c.IdDocumento_Referencia = g.IdDocumento_OrdenVenta
    INNER JOIN dbo.docNotaInventario a3 WITH (NOLOCK)
        ON a3.IdDocumento_OrdenProduccion = c.IdDocumento_OrdenProduccion
        AND a3.IdtdDocumentoForm = 131
        AND a3.bDevolucion = 0
        AND a3.bDesactivado = 0
        AND a3.bAnulado = 0
    INNER JOIN dbo.docNotaInventarioItem b3 WITH (NOLOCK)
        ON a3.IdDocumento_NotaInventario = b3.IdDocumento_NotaInventario
        AND b3.dCantidadIng <> 0
    INNER JOIN dbo.docOrdenProduccionRuta d3 WITH (NOLOCK)
        ON a3.IddocOrdenProduccionRuta = d3.IddocOrdenProduccionRuta
    INNER JOIN dbo.maeCentroCosto a4 WITH (NOLOCK)
        ON a3.IdmaeCentroCosto = a4.IdmaeCentroCosto
        AND a4.bConOrdenProduccion = 1
    WHERE c.bCerrado = 0
        AND c.bAnulado = 0
        AND c.IdtdDocumentoForm = 127
)
SELECT 
    sc.CoddocOrdenVenta AS PEDIDO,
    sc.NommaeCentroCosto AS PROCESO,
    SUM(sc.dCantidadRequerido) AS REQUERIDO,
    SUM(sc.dCantidadProgramado) AS PROGRAMADO,
    SUM(sc.dCantidadProducido) AS PRODUCIDO
FROM (
    SELECT * FROM ProduccionPorProceso
    UNION ALL
    SELECT * FROM ProducidoPorProceso
) sc
WHERE sc.CoddocOrdenVenta = '{pedido}'
GROUP BY 
    sc.CoddocOrdenVenta, 
    sc.NommaeCentroCosto
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

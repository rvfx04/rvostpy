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

columns, rows = run_query("""
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
        --AND c.bCerrado = 0
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
WHERE sc.CoddocOrdenProduccion = '0988-3'
GROUP BY 
    sc.CoddocOrdenProduccion, 
    sc.NommaeCentroCosto,
    sc.IdmaeCentroCosto
ORDER BY 
    sc.IdmaeCentroCosto ASC;""")

# Asegúrese de que las filas sean tuplas
rows = [tuple(row) for row in rows]
# Convertir datos a un DataFrame de pandas
df = pd.DataFrame(rows, columns=columns)
# Artificio para anular la columna que numera las filas
df = df.set_index(df.columns[0])

# Mostrar el DataFrame
#st.dataframe(filtered_df)
st.dataframe(df) 

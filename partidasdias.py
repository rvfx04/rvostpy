import streamlit as st
import pyodbc
import pandas as pd

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

# Función para ejecutar la consulta SQL
def ejecutar_consulta():
    query = f"""
    SELECT 
        a.CoddocOrdenProduccion as PARTIDA, 
        a.dtFechaEmision AS F_EMISION,
        --CONVERT(INT, GETDATE() - a.dtFechaEmision) as DIAS,
        SUBSTRING(b.NommaeAnexoCliente, 1, 15) AS CLIENTE,
        a.nvDocumentoReferencia AS PEDIDO,
        SUBSTRING(c.NommaeItemInventario,1,25) AS TELA,
        a.dCantidad AS KG, 
        d.NommaeColor AS COLOR,
        a.IdmaeRuta AS RUTA,
        g.NommaeDiseño AS DISEÑO
    FROM docOrdenProduccion a
    INNER JOIN maeAnexoCliente b ON a.IdmaeAnexo_Cliente = b.IdmaeAnexo_Cliente
    INNER JOIN maeItemInventario c ON a.IdmaeItem = c.IdmaeItem_Inventario
    INNER JOIN maeColor d ON a.IdmaeColor = d.IdmaeColor
    INNER JOIN maeRuta e ON a.IdmaeRuta = e.IdmaeRuta
    INNER JOIN maeDiseño g ON a.IdmaeDiseño = g.IdmaeDiseño
    WHERE a.IdtdDocumentoForm = 138
      AND a.ntEstado = 'REGISTRADO'
      AND a.IdmaeAnexo_Cliente IN (47,49,93,111,1445,2533,2637, 4294, 4323, 4374, 4411, 4413, 4469, 5506, 6577, 2698)
      AND a.dtFechaEmision > '2023-12-31'
      AND a.bAnulado = 0
      AND a.IdmaeReceta > 0
      --AND CONVERT(INT, GETDATE() - a.dtFechaEmision) <= {dias}
    """
    
    #if cliente_seleccionado:
        #query += f" AND SUBSTRING(b.NommaeAnexoCliente, 1, 15) = '{cliente_seleccionado}'"

    #query += " ORDER BY DIAS DESC"

    conn = get_connection()
    if conn:
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    else:
        return pd.DataFrame()  # Retorna un DataFrame vacío si no hay conexión

# Interfaz de la aplicación
st.title('Partidas de Teñido')

# Seleccionar número de días
#dias = st.number_input('Días desde emisión', value=10, min_value=1)

# Ejecutar la consulta sin cliente seleccionado inicialmente
df = ejecutar_consulta()

# Combobox para seleccionar cliente de las opciones obtenidas
#clientes = df['CLIENTE'].unique()
#cliente_seleccionado = st.selectbox('Seleccionar Cliente', options=['Todos'] + list(clientes))

# Filtrar según cliente seleccionado
#if cliente_seleccionado != 'Todos':
    #df = ejecutar_consulta(dias, cliente_seleccionado)

# Mostrar la tabla con el resultado
st.dataframe(df)


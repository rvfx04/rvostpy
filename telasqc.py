import streamlit as st
import pyodbc
import pandas as pd
import matplotlib.pyplot as plt

# Conexión a la base de datos usando Secrets
def get_db_connection():
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=" + st.secrets["server"] + ";"
        "DATABASE=" + st.secrets["database"] + ";"
        "UID=" + st.secrets["username"] + ";"
        "PWD=" + st.secrets["password"] + ";"
    )
    return conn

# Consulta SQL con filtros
def get_data(start_date, end_date, clientes, codigo, tela, color, acabado):
    conn = get_db_connection()
    
    query = f"""
    SELECT  
        c.CoddocOrdenProduccion AS PARTIDA,
        c.nvDocumentoReferencia AS REF_PEDIDO,
        a.CoddocOrdenProduccionCalidad AS REPORTE,
        b.CodmaeItemInventario AS CODIGO,
        b.NommaeItemInventario AS TELA,
        d.nommaecolor AS COLOR,
        a.ntDescripcionAcabado AS ACABADO,
        a.dAnchoAcabado AS ANCHO_ACABADO,
        a.AATCC135_EncogLargo AS ENCOG_LARGO,
        a.AATCC135_EncogAncho AS ENCOG_ANCHO,
        a.AATCC179_ReviradoLavado AS REVIRADO,
        a.AATCC179_DensidadAcabada AS DENSIDAD,
        a.nvTituloObservacion AS OBSERV1,
        a.ntObservacion AS OBSERV2,
        CONVERT(DATE,a.dtFechaReporte) AS FECH_REPORTE,
        e.NommaeAnexoCliente AS CLIENTE
    FROM 
        [GarmentData].[dbo].[docOrdenProduccionCalidad] a
    INNER JOIN 
        maeItemInventario b ON a.idmaeitem = b.IdmaeItem_Inventario
    INNER JOIN 
        docOrdenProduccion c ON a.IdDocumento_OrdenProduccion = c.IdDocumento_OrdenProduccion
    INNER JOIN 
        maecolor d ON c.IdmaeColor = d.idmaecolor
    INNER JOIN 
        maeAnexoCliente e ON e.IdmaeAnexo_Cliente = c.IdmaeAnexo_Cliente
    WHERE 
        CONVERT(DATE,a.dtFechaReporte) BETWEEN ? AND ?
        AND e.NommaeAnexoCliente LIKE ?
        AND b.CodmaeItemInventario LIKE ?
        AND b.NommaeItemInventario LIKE ?
        AND d.nommaecolor LIKE ?
        AND a.ntDescripcionAcabado LIKE ?
    """
    
    params = [start_date, end_date] + [f"%{clientes}%",f"%{codigo}%", f"%{tela}%", f"%{color}%", f"%{acabado}%"]
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df

# Interfaz de usuario
st.title('Consulta de Reportes de Calidad')

with col1:
    start_date = st.date_input('Fecha de inicio')
    clientes = st.text_input('Clientes')
    color = st.text_input('Color')

with col2:
    end_date = st.date_input('Fecha de fin')
    codigo = st.text_input('Código')
    tela = st.text_input('Tela')
    acabado = st.text_input('Acabado')

if st.button('Consultar'):
    df = get_data(start_date, end_date, clientes, codigo, tela, color, acabado)
    st.write(df)
    
     # Ajustar estilo de los gráficos
    plt.style.use('seaborn-darkgrid')
    plt.rcParams.update({'figure.figsize': (6, 3), 'axes.titlesize': 'medium', 'axes.labelsize': 'small', 'xtick.labelsize': 'small', 'ytick.labelsize': 'small'})
      
        # Histograma de DENSIDAD
    if 'DENSIDAD' in df.columns:
            st.subheader('Histograma de DENSIDAD')
            fig, ax = plt.subplots()
            ax.hist(df['DENSIDAD'].dropna(), bins=30, edgecolor='black')
            ax.set_xlabel('DENSIDAD')
            ax.set_ylabel('Frecuencia')
            st.pyplot(fig)

        # Histograma de ANCHO_ACABADO
    if 'ANCHO_ACABADO' in df.columns:
            st.subheader('Histograma de ANCHO')
            fig, ax = plt.subplots()
            ax.hist(df['ANCHO_ACABADO'].dropna(), bins=30, edgecolor='black')
            ax.set_xlabel('ANCHO_ACABADO')
            ax.set_ylabel('Frecuencia')
            st.pyplot(fig)

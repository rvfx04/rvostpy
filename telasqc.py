import streamlit as st
import pyodbc
import pandas as pd
import matplotlib.pyplot as plt

# Conexión a la base de datos usando Secrets
def get_db_connection():
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=" + st.secrets["db"]["server"] + ";"
        "DATABASE=" + st.secrets["db"]["database"] + ";"
        "UID=" + st.secrets["db"]["username"] + ";"
        "PWD=" + st.secrets["db"]["password"]
    )
    return conn

# Consulta SQL con filtros
def get_data(start_date, end_date, clientes, codigo, tela, color, acabado):
    conn = get_db_connection()
    
    clientes_placeholder = ', '.join('?' for _ in clientes)
    acabados_placeholder = ', '.join('?' for _ in acabado)
    
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
        a.dtFechaReporte AS FECH_REPORTE,
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
        a.dtFechaReporte BETWEEN ? AND ?
        AND e.NommaeAnexoCliente IN ({clientes_placeholder})
        AND b.CodmaeItemInventario LIKE ?
        AND b.NommaeItemInventario LIKE ?
        AND d.nommaecolor LIKE ?
        AND a.ntDescripcionAcabado IN ({acabados_placeholder})
    """
    
    params = [start_date, end_date] + clientes + [f"%{codigo}%", f"%{tela}%", f"%{color}%"] + acabado
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df

# Interfaz de usuario
st.title('Consulta de Base de Datos')

start_date = st.date_input('Fecha de inicio')
end_date = st.date_input('Fecha de fin')

clientes = st.multiselect('Clientes', options=['Cliente1', 'Cliente2', 'Cliente3'])  # Actualiza con tus valores de clientes
codigo = st.text_input('Código')
tela = st.text_input('Tela')
color = st.text_input('Color')
acabado = st.multiselect('Acabado', options=['Acabado1', 'Acabado2', 'Acabado3'])  # Actualiza con tus valores de acabado

if st.button('Consultar'):
    if not clientes:
        st.error('Debe seleccionar al menos un cliente')
    elif not acabado:
        st.error('Debe seleccionar al menos un acabado')
    else:
        df = get_data(start_date, end_date, clientes, codigo, tela, color, acabado)
        st.write(df)
        
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
            st.subheader('Histograma de ANCHO_ACABADO')
            fig, ax = plt.subplots()
            ax.hist(df['ANCHO_ACABADO'].dropna(), bins=30, edgecolor='black')
            ax.set_xlabel('ANCHO_ACABADO')
            ax.set_ylabel('Frecuencia')
            st.pyplot(fig)

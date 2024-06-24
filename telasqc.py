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
def get_data(start_date, end_date, clientes, codigo, tela, color, acabado, partida):
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
        AND c.CoddocOrdenProduccion LIKE ?
    """
    
    params = [start_date, end_date] + [f"%{clientes}%", f"%{codigo}%", f"%{tela}%", f"%{color}%", f"%{acabado}%", f"%{partida}%"]
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df

# Interfaz de usuario
st.title('Análisis de Reportes de Calidad')

# Organización en dos columnas
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input('Fecha de inicio')
    clientes = st.text_input('Clientes')
    color = st.text_input('Color')
    partida = st.text_input('Partida')
with col2:
    end_date = st.date_input('Fecha de fin')
    codigo = st.text_input('Código')
    tela = st.text_input('Tela')
    acabado = st.text_input('Acabado')

if st.button('Consultar'):
    df = get_data(start_date, end_date, clientes, codigo, tela, color, acabado, partida)
    
    # Agregar una columna de numeración que comience en 1
    #df.index = df.index + 1
    #df.reset_index(inplace=True)
    #df.rename(columns={'index': 'N°'}, inplace=True)
    
    # Mostrar la tabla
    st.write(df)
    
    # Mostrar el número de registros
    st.write(f"Número de registros: {len(df)}")
    
    plt.rcParams.update({'figure.figsize': (6, 3), 'axes.titlesize': 'medium', 'axes.labelsize': 'small', 'xtick.labelsize': 'small', 'ytick.labelsize': 'small'})
    
    def plot_histogram(column_name, xlabel):
        if column_name in df.columns:
            st.subheader(f'Histograma de {xlabel}')
            fig, ax = plt.subplots()
            data = df[column_name].dropna()
            counts, bins, patches = ax.hist(data, bins=30, edgecolor='black')
            total = len(data)
            # Convertir las frecuencias a porcentajes
            percentages = [(height / total) * 100 for height in counts]
            for patch, percentage in zip(patches, percentages):
                patch.set_height(percentage)
            ax.set_xlabel(xlabel)
            ax.set_ylabel('Frecuencia (%)')
            # Ajustar el eje y para que muestre porcentajes
            max_percentage = max(percentages)
            ax.set_ylim(0, max_percentage * 1.1)  # Ajuste del límite superior para proporcionar un poco de espacio
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.0f}%'.format(y)))
            st.pyplot(fig)

    plot_histogram('DENSIDAD', 'DENSIDAD')
    plot_histogram('ANCHO_ACABADO', 'ANCHO_ACABADO')
    plot_histogram('REVIRADO', 'REVIRADO')
    plot_histogram('ENCOG_ANCHO', 'ENCOG_ANCHO')
    plot_histogram('ENCOG_LARGO', 'ENCOG_LARGO')

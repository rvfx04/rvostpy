import streamlit as st
import pandas as pd
import pyodbc
import plotly.express as px

def create_connection():
    """Crear conexión a SQL Server"""
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=' + st.secrets["server"] + ';'
            'DATABASE=' + st.secrets["database"] + ';'
            'UID=' + st.secrets["username"] + ';'
            'PWD=' + st.secrets["password"]
        )
        return conn
    except Exception as e:
        st.error(f"Error al conectar a la base de datos: {e}")
        return None

def get_data(conn):
    """Ejecutar consulta SQL y obtener datos"""
    query = """
    SELECT 
        j.CoddocOrdenVenta AS PEDIDO, 
        b.CoddocOrdenProduccion AS OP, 
        c.NommaeCentroCosto AS PROCESO, 
        e.NommaeCombo AS COMBO, 
        SUBSTRING(i.NommaeAnexoCliente,1,15) AS CLIENTE, 
        h.nvModelo AS ESTILO, 
        SUM(a.dCantidadRequerido) AS Q_REQ, 
        SUM(a.dCantidadProducido) AS Q_PROD,
        ROUND(
            CASE
                WHEN SUM(a.dCantidadRequerido) <> 0 
                THEN SUM(a.dCantidadProducido) / SUM(a.dCantidadRequerido) * 100
                ELSE 0
            END, 1
        ) AS AVANCE_PORC
    FROM dbo.fntOrdenProduccion_AvanceProduccion_ComboTalla() a
    INNER JOIN dbo.docOrdenProduccion b WITH (NOLOCK)
        ON a.IdDocumento_OrdenProduccion = b.IdDocumento_OrdenProduccion
    INNER JOIN dbo.maeCentroCosto c WITH (NOLOCK)
        ON a.IdmaeCentroCosto = c.IdmaeCentroCosto
    INNER JOIN dbo.maeCombo e WITH (NOLOCK)
        ON a.IdmaeCombo = e.IdmaeCombo
    INNER JOIN dbo.maeTalla f WITH (NOLOCK)
        ON a.IdmaeTalla = f.IdmaeTalla
    INNER JOIN dbo.docOrdenProduccionRuta g WITH (NOLOCK)
        ON a.IddocOrdenProduccionRuta = g.IddocOrdenProduccionRuta
    INNER JOIN dbo.maeEstilo h WITH (NOLOCK)
        ON b.IdmaeEstilo = h.IdmaeEstilo
    INNER JOIN dbo.maeAnexoCliente i WITH (NOLOCK)
        ON b.IdmaeAnexo_Cliente = i.IdmaeAnexo_Cliente
    INNER JOIN dbo.docOrdenVenta j WITH (NOLOCK)
        ON b.IdDocumento_Referencia = j.IdDocumento_OrdenVenta
    WHERE b.dtFechaEntrega > '30-07-2024'
    GROUP BY 
        j.CoddocOrdenVenta,
        b.CoddocOrdenProduccion,
        c.NommaeCentroCosto,
        e.NommaeCombo,
        i.NommaeAnexoCliente,
        h.nvModelo
    """
    return pd.read_sql(query, conn)

def create_pivot_table(df):
    """Crear tabla dinámica con una columna de requerido y procesos como columnas de producido"""
    # Crear un DataFrame base con la información principal y cantidad requerida
    base_info = df[['PEDIDO', 'OP', 'CLIENTE', 'ESTILO', 'COMBO']].drop_duplicates()
    req_info = df[['OP', 'Q_REQ']].drop_duplicates()
    base_df = base_info.merge(req_info, on='OP')
    
    # Crear pivote para cantidades producidas por proceso
    pivot_prod = pd.pivot_table(
        df,
        values='Q_PROD',
        index=['PEDIDO', 'OP', 'CLIENTE', 'ESTILO', 'COMBO'],
        columns='PROCESO',
        aggfunc='sum',
        fill_value=0
    )
    
    # Crear pivote para porcentajes de avance
    pivot_avance = pd.pivot_table(
        df,
        values='AVANCE_PORC',
        index=['PEDIDO', 'OP', 'CLIENTE', 'ESTILO', 'COMBO'],
        columns='PROCESO',
        aggfunc='max',
        fill_value=0
    )
    
    # Renombrar columnas del pivote de avance
    pivot_avance.columns = [f"{col} %" for col in pivot_avance.columns]
    
    # Combinar toda la información
    result = pd.concat([pivot_prod, pivot_avance], axis=1).reset_index()
    
    # Asegurar que las columnas estén en el orden correcto
    processes = df['PROCESO'].unique()
    ordered_columns = ['PEDIDO', 'OP', 'CLIENTE', 'ESTILO', 'COMBO', 'Q_REQ']
    
    # Ordenar las columnas de procesos intercalando cantidad y porcentaje
    for process in processes:
        ordered_columns.extend([process, f"{process} %"])
    
    # Merge con la cantidad requerida
    result = result.merge(req_info, on='OP')
    
    # Reordenar columnas
    result = result[ordered_columns]
    
    return result

def main():
    st.set_page_config(page_title="Dashboard de Producción", layout="wide")
    
    st.title("Dashboard de Avance de Producción")
    
    # Crear conexión
    conn = create_connection()
    if not conn:
        return
    
    # Obtener datos
    try:
        with st.spinner('Cargando datos...'):
            df = get_data(conn)
    except Exception as e:
        st.error(f"Error al obtener datos: {e}")
        return
    finally:
        conn.close()

    # Filtros en la barra lateral
    st.sidebar.title("Filtros")
    
    # Filtro de Cliente
    clientes = ['Todos'] + sorted(df['CLIENTE'].unique().tolist())
    cliente_seleccionado = st.sidebar.selectbox('Cliente:', clientes)
    
    # Filtrar datos por cliente
    if cliente_seleccionado != 'Todos':
        df_filtered = df[df['CLIENTE'] == cliente_seleccionado]
    else:
        df_filtered = df.copy()
    
    # Filtro de Pedidos
    pedidos = sorted(df_filtered['PEDIDO'].unique().tolist())
    pedidos_seleccionados = st.sidebar.multiselect(
        'Pedido(s):',
        pedidos
    )
    
    # Filtrar por pedidos seleccionados
    if pedidos_seleccionados:
        df_filtered = df_filtered[df_filtered['PEDIDO'].isin(pedidos_seleccionados)]
    
    # Filtro de OPs
    ops = sorted(df_filtered['OP'].unique().tolist())
    ops_seleccionados = st.sidebar.multiselect(
        'OP(s):',
        ops,
        default=ops
    )
    
    # Filtrar por OPs seleccionadas
    if ops_seleccionados:
        df_filtered = df_filtered[df_filtered['OP'].isin(ops_seleccionados)]
    
    # Crear y mostrar tabla dinámica
    if not df_filtered.empty:
        pivot_df = create_pivot_table(df_filtered)
        
        st.subheader("Avance de Producción por Proceso")
        
        # Formatear los números en la tabla
        formatted_df = pivot_df.copy()
        for col in formatted_df.columns:
            if col.endswith('%'):
                formatted_df[col] = formatted_df[col].apply(lambda x: f"{x:.1f}%")
            elif col not in ['PEDIDO', 'OP', 'CLIENTE', 'ESTILO', 'COMBO']:
                formatted_df[col] = formatted_df[col].apply(lambda x: f"{x:,.0f}")
        
        st.dataframe(
            formatted_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Gráfico de avance por proceso
        avg_progress = df_filtered.groupby('PROCESO')['AVANCE_PORC'].mean().reset_index()
        fig = px.bar(
            avg_progress,
            x='PROCESO',
            y='AVANCE_PORC',
            title='Porcentaje de Avance por Proceso',
            labels={'AVANCE_PORC': 'Porcentaje de Avance', 'PROCESO': 'Proceso'},
            color='PROCESO'
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()

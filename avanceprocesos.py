import streamlit as st
import pandas as pd
import pyodbc
import plotly.express as px

def create_connection():
    """Crear conexión a SQL Server"""
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

def get_data(conn):
    """Ejecutar consulta SQL y obtener datos"""
    query = """
    SELECT 
        j.CoddocOrdenVenta AS PEDIDO, 
        b.CoddocOrdenProduccion AS OP, 
        c.NommaeCentroCosto AS PROCESO, 
        e.NommaeCombo AS COMBO, 
        f.NommaeTalla AS TALLA,
        SUBSTRING(i.NommaeAnexoCliente,1,15) AS CLIENTE, 
        h.nvModelo AS ESTILO, 
        a.dCantidadRequerido AS Q_REQ, 
        a.dCantidadProgramado AS Q_PROG, 
        a.dCantidadProducido AS Q_PROD,
        a.dCantidadProgramado - a.dCantidadProducido AS Q_PEND,
        ROUND(
            CASE
                WHEN a.dCantidadProgramado <> 0 THEN a.dCantidadProducido / a.dCantidadRequerido
                ELSE 0
            END, 5
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
    """
    return pd.read_sql(query, conn)

def main():
    st.set_page_config(page_title="Dashboard de Producción", layout="wide")
    
    # Aplicar estilo personalizado
    st.markdown("""
        <style>
        .stSelectbox, .stMultiSelect {
            margin-bottom: 1rem;
        }
        .metric-card {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
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

    # Crear layout de dos columnas
    col_filtros, col_contenido = st.columns([1, 3])
    
    with col_filtros:
        st.subheader("Filtros")
        
        # Filtro de Cliente
        clientes = ['Todos'] + sorted(df['CLIENTE'].unique().tolist())
        cliente_seleccionado = st.selectbox(
            'Cliente:',
            clientes,
            key='cliente_filter'
        )
        
        # Filtrar datos por cliente
        if cliente_seleccionado != 'Todos':
            df_filtered = df[df['CLIENTE'] == cliente_seleccionado]
        else:
            df_filtered = df.copy()
        
        # Filtro de Pedidos
        pedidos = sorted(df_filtered['PEDIDO'].unique().tolist())
        pedidos_seleccionados = st.multiselect(
            'Pedido(s):',
            pedidos,
            key='pedido_filter'
        )
        
        # Filtrar por pedidos seleccionados
        if pedidos_seleccionados:
            df_filtered = df_filtered[df_filtered['PEDIDO'].isin(pedidos_seleccionados)]
        
        # Filtro de OPs
        ops = sorted(df_filtered['OP'].unique().tolist())
        ops_seleccionados = st.multiselect(
            'OP(s):',
            ops,
            default=ops,  # Por defecto selecciona todas las OPs
            key='op_filter'
        )
        
        # Filtrar por OPs seleccionadas
        if ops_seleccionados:
            df_filtered = df_filtered[df_filtered['OP'].isin(ops_seleccionados)]
    
    with col_contenido:
        # Métricas principales
        st.subheader("Resumen de Cantidades")
        met1, met2, met3, met4 = st.columns(4)
        
        with met1:
            st.metric(
                "Total Requerido",
                f"{df_filtered['Q_REQ'].sum():,.0f}",
                delta=None
            )
        with met2:
            st.metric(
                "Total Programado",
                f"{df_filtered['Q_PROG'].sum():,.0f}",
                delta=None
            )
        with met3:
            st.metric(
                "Total Producido",
                f"{df_filtered['Q_PROD'].sum():,.0f}",
                delta=None
            )
        with met4:
            st.metric(
                "Total Pendiente",
                f"{df_filtered['Q_PEND'].sum():,.0f}",
                delta=None
            )
        
        # Gráfico de avance por proceso
        if not df_filtered.empty:
            st.subheader("Avance por Proceso")
            fig = px.bar(
                df_filtered, 
                x='PROCESO', 
                y='AVANCE_PORC',
                color='PROCESO',
                labels={'AVANCE_PORC': 'Porcentaje de Avance', 'PROCESO': 'Proceso'},
                height=400
            )
            fig.update_layout(
                xaxis_tickangle=-45,
                showlegend=False,
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Tabla de datos
        st.subheader("Detalle de Producción")
        st.dataframe(
            df_filtered,
            use_container_width=True,
            hide_index=True
        )

if __name__ == "__main__":
    main()

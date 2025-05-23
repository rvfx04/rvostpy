import streamlit as st
import pandas as pd
import pyodbc
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuración de la página
st.set_page_config(
    page_title="Reporte de Producción por Cliente",
    page_icon="📊",
    layout="wide"
)

# Función para conectar a SQL Server
@st.cache_resource
def init_connection():
    try:
        # Obtener credenciales desde secrets de Streamlit
        server = st.secrets["database"]["server"]
        database = st.secrets["database"]["database"]
        username = st.secrets["database"]["username"]
        password = st.secrets["database"]["password"]
        driver = st.secrets["database"].get("driver", "ODBC Driver 17 for SQL Server")
        
        connection_string = f"""
        DRIVER={{{driver}}};
        SERVER={server};
        DATABASE={database};
        UID={username};
        PWD={password};
        Trust_Connection=no;
        """
        
        return pyodbc.connect(connection_string)
    except Exception as e:
        st.error(f"Error conectando a la base de datos: {str(e)}")
        st.stop()

# Función para ejecutar la consulta
@st.cache_data(ttl=300)  # Cache por 5 minutos
def run_query(start_date, end_date):
    conn = init_connection()
    
    # La consulta SQL completa
    sql_query = """
    DECLARE @F1 DATE = ?;
    DECLARE @F2 DATE = ?;
    DECLARE @cols NVARCHAR(MAX), 
            @cols_isnull NVARCHAR(MAX),
            @cols_with_isnull NVARCHAR(MAX),
            @cols_op NVARCHAR(MAX),
            @sql NVARCHAR(MAX);

    -- Obtener columnas de clientes con ISNULL y columnas para OPs
    SELECT 
        @cols = STRING_AGG(QUOTENAME(LEFT(d.NommaeAnexoCliente, 15)), ','),
        @cols_isnull = STRING_AGG('ISNULL(' + QUOTENAME(LEFT(d.NommaeAnexoCliente, 15)) + ', 0)', ' + '),
        @cols_with_isnull = STRING_AGG('ISNULL(' + QUOTENAME(LEFT(d.NommaeAnexoCliente, 15)) + ', 0) AS ' + QUOTENAME(LEFT(d.NommaeAnexoCliente, 15)), ', '),
        @cols_op = STRING_AGG('ISNULL(' + QUOTENAME(LEFT(d.NommaeAnexoCliente, 15) + '_OP') + ', '''') AS ' + QUOTENAME(LEFT(d.NommaeAnexoCliente, 15) + '_OP'), ', ')
    FROM (
        SELECT DISTINCT LEFT(d.NommaeAnexoCliente, 15) AS NommaeAnexoCliente
        FROM dbo.docNotaInventario a
        INNER JOIN dbo.docNotaInventarioItem b 
            ON a.IdDocumento_NotaInventario = b.IdDocumento_NotaInventario AND b.dCantidadIng <> 0
        INNER JOIN dbo.docOrdenProduccion c 
            ON a.IdDocumento_OrdenProduccion = c.IdDocumento_OrdenProduccion 
            AND c.bCerrado = 0 AND c.bAnulado = 0 AND c.IdtdDocumentoForm = 127
        INNER JOIN dbo.maeAnexoCliente d 
            ON c.IdmaeAnexo_Cliente = d.IdmaeAnexo_Cliente
        WHERE a.IdtdDocumentoForm = 131
            AND a.bDevolucion = 0 
            AND a.bDesactivado = 0 
            AND a.bAnulado = 0 
            AND a.IdDocumento_OrdenProduccion <> 0 
            AND a.dtFechaRegistro BETWEEN @F1 AND @F2
            AND a.IdmaeCentroCosto = 29
    ) d;

    -- Crear columnas para el PIVOT de OPs
    DECLARE @cols_pivot_op NVARCHAR(MAX);
    SELECT @cols_pivot_op = STRING_AGG(QUOTENAME(LEFT(d.NommaeAnexoCliente, 15) + '_OP'), ',')
    FROM (
        SELECT DISTINCT LEFT(d.NommaeAnexoCliente, 15) AS NommaeAnexoCliente
        FROM dbo.docNotaInventario a
        INNER JOIN dbo.docNotaInventarioItem b 
            ON a.IdDocumento_NotaInventario = b.IdDocumento_NotaInventario AND b.dCantidadIng <> 0
        INNER JOIN dbo.docOrdenProduccion c 
            ON a.IdDocumento_OrdenProduccion = c.IdDocumento_OrdenProduccion 
            AND c.bCerrado = 0 AND c.bAnulado = 0 AND c.IdtdDocumentoForm = 127
        INNER JOIN dbo.maeAnexoCliente d 
            ON c.IdmaeAnexo_Cliente = d.IdmaeAnexo_Cliente
        WHERE a.IdtdDocumentoForm = 131
            AND a.bDevolucion = 0 
            AND a.bDesactivado = 0 
            AND a.bAnulado = 0 
            AND a.IdDocumento_OrdenProduccion <> 0 
            AND a.dtFechaRegistro BETWEEN @F1 AND @F2
            AND a.IdmaeCentroCosto = 29
    ) d;

    -- Crear la consulta dinámica usando parámetros
    SET @sql = N'
    WITH DatosCantidad AS (
        SELECT 
            CONVERT(varchar(10), a.dtFechaRegistro, 105) AS FECHA,
            LEFT(d.NommaeAnexoCliente, 15) AS CLIENTE,
            CAST(b.dCantidadIng AS INT) AS UNID
        FROM dbo.docNotaInventario a
        INNER JOIN dbo.docNotaInventarioItem b 
            ON a.IdDocumento_NotaInventario = b.IdDocumento_NotaInventario AND b.dCantidadIng <> 0
        INNER JOIN dbo.docOrdenProduccion c 
            ON a.IdDocumento_OrdenProduccion = c.IdDocumento_OrdenProduccion 
            AND c.bCerrado = 0 AND c.bAnulado = 0 AND c.IdtdDocumentoForm = 127
        INNER JOIN dbo.maeAnexoCliente d 
            ON c.IdmaeAnexo_Cliente = d.IdmaeAnexo_Cliente
        WHERE a.IdtdDocumentoForm = 131
            AND a.bDevolucion = 0 
            AND a.bDesactivado = 0 
            AND a.bAnulado = 0 
            AND a.IdDocumento_OrdenProduccion <> 0 
            AND a.dtFechaRegistro BETWEEN @pF1 AND @pF2
            AND a.IdmaeCentroCosto = 29
    ),
    DatosOP AS (
        SELECT 
            FECHA,
            NommaeAnexoCliente + ''_OP'' AS CLIENTE_OP,
            STRING_AGG(CoddocOrdenProduccion, '', '') AS OPS
        FROM (
            SELECT DISTINCT 
                CONVERT(varchar(10), a.dtFechaRegistro, 105) AS FECHA,
                LEFT(d.NommaeAnexoCliente, 15) AS NommaeAnexoCliente,
                c.CoddocOrdenProduccion
            FROM dbo.docNotaInventario a
            INNER JOIN dbo.docNotaInventarioItem b 
                ON a.IdDocumento_NotaInventario = b.IdDocumento_NotaInventario AND b.dCantidadIng <> 0
            INNER JOIN dbo.docOrdenProduccion c 
                ON a.IdDocumento_OrdenProduccion = c.IdDocumento_OrdenProduccion 
                AND c.bCerrado = 0 AND c.bAnulado = 0 AND c.IdtdDocumentoForm = 127
            INNER JOIN dbo.maeAnexoCliente d 
                ON c.IdmaeAnexo_Cliente = d.IdmaeAnexo_Cliente
            WHERE a.IdtdDocumentoForm = 131
                AND a.bDevolucion = 0 
                AND a.bDesactivado = 0 
                AND a.bAnulado = 0 
                AND a.IdDocumento_OrdenProduccion <> 0 
                AND a.dtFechaRegistro BETWEEN @pF1 AND @pF2
                AND a.IdmaeCentroCosto = 29
        ) subquery
        GROUP BY FECHA, NommaeAnexoCliente
    ),
    PivotCantidad AS (
        SELECT FECHA, ' + @cols + '
        FROM DatosCantidad
        PIVOT (SUM(UNID) FOR CLIENTE IN (' + @cols + ')) AS PivotTable
    ),
    PivotOP AS (
        SELECT FECHA, ' + @cols_pivot_op + '
        FROM DatosOP
        PIVOT (MAX(OPS) FOR CLIENTE_OP IN (' + @cols_pivot_op + ')) AS PivotTable
    )
    SELECT 
        p1.FECHA, 
        ' + @cols_with_isnull + ', 
        ' + @cols_isnull + ' AS TOTAL,
        ' + @cols_op + '
    FROM PivotCantidad p1
    LEFT JOIN PivotOP p2 ON p1.FECHA = p2.FECHA
    ORDER BY p1.FECHA;';

    -- Ejecutar la consulta dinámica con parámetros
    EXEC sp_executesql @sql, N'@pF1 DATE, @pF2 DATE', @pF1 = @F1, @pF2 = @F2;
    """
    
    try:
        df = pd.read_sql(sql_query, conn, params=[start_date, end_date])
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error ejecutando la consulta: {str(e)}")
        return pd.DataFrame()

# Función para crear gráfico de tendencia
def create_trend_chart(df):
    if df.empty:
        return None
    
    # Obtener columnas de clientes (excluyendo FECHA, TOTAL y columnas _OP)
    client_columns = [col for col in df.columns if not col.endswith('_OP') and col not in ['FECHA', 'TOTAL']]
    
    fig = go.Figure()
    
    for col in client_columns:
        fig.add_trace(go.Scatter(
            x=df['FECHA'],
            y=df[col],
            mode='lines+markers',
            name=col,
            line=dict(width=2),
            marker=dict(size=6)
        ))
    
    fig.update_layout(
        title="Tendencia de Producción por Cliente",
        xaxis_title="Fecha",
        yaxis_title="Unidades Producidas",
        hovermode='x unified',
        height=500
    )
    
    return fig

# Función para crear gráfico de barras
def create_bar_chart(df):
    if df.empty:
        return None
    
    # Sumar totales por cliente
    client_columns = [col for col in df.columns if not col.endswith('_OP') and col not in ['FECHA', 'TOTAL']]
    totals = df[client_columns].sum().sort_values(ascending=False)
    
    fig = px.bar(
        x=totals.index,
        y=totals.values,
        title="Total de Producción por Cliente",
        labels={'x': 'Cliente', 'y': 'Total Unidades'}
    )
    
    fig.update_layout(height=400)
    return fig

# Interfaz principal
def main():
    st.title("📊 Reporte de Producción por Cliente")
    st.markdown("---")
    
    # Sidebar para filtros
    with st.sidebar:
        st.header("🔧 Filtros")
        
        # Selector de fechas
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Fecha Inicio",
                value=date(2025, 5, 1),
                key="start_date"
            )
        with col2:
            end_date = st.date_input(
                "Fecha Fin",
                value=date(2025, 12, 31),
                key="end_date"
            )
        
        # Botón para ejecutar consulta
        if st.button("🔄 Actualizar Datos", type="primary"):
            st.cache_data.clear()
    
    # Validar fechas
    if start_date > end_date:
        st.error("❌ La fecha de inicio debe ser anterior a la fecha de fin")
        return
    
    # Ejecutar consulta y mostrar resultados
    with st.spinner("Ejecutando consulta..."):
        df = run_query(start_date, end_date)
    
    if df.empty:
        st.warning("⚠️ No se encontraron datos para el rango de fechas seleccionado")
        return
    
    # Mostrar métricas principales
    st.subheader("📈 Resumen Ejecutivo")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_units = df['TOTAL'].sum()
        st.metric("Total Unidades", f"{total_units:,}")
    
    with col2:
        avg_daily = df['TOTAL'].mean()
        st.metric("Promedio Diario", f"{avg_daily:.1f}")
    
    with col3:
        max_day = df['TOTAL'].max()
        st.metric("Máximo Diario", f"{max_day:,}")
    
    with col4:
        num_clients = len([col for col in df.columns if not col.endswith('_OP') and col not in ['FECHA', 'TOTAL']])
        st.metric("Clientes Activos", num_clients)
    
    st.markdown("---")
    
    # Gráficos
    st.subheader("📊 Análisis Visual")
    
    tab1, tab2 = st.tabs(["📈 Tendencia Temporal", "📊 Totales por Cliente"])
    
    with tab1:
        trend_chart = create_trend_chart(df)
        if trend_chart:
            st.plotly_chart(trend_chart, use_container_width=True)
    
    with tab2:
        bar_chart = create_bar_chart(df)
        if bar_chart:
            st.plotly_chart(bar_chart, use_container_width=True)
    
    # Tabla de datos
    st.subheader("📋 Datos Detallados")
    
    # Opciones de visualización
    col1, col2 = st.columns([1, 3])
    
    with col1:
        show_op_columns = st.checkbox("Mostrar columnas OP", value=False)
    
    # Filtrar columnas según selección
    if show_op_columns:
        display_df = df
    else:
        display_df = df[[col for col in df.columns if not col.endswith('_OP')]]
    
    # Mostrar tabla con formato
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )
    
    # Botón de descarga
    csv = display_df.to_csv(index=False)
    st.download_button(
        label="📥 Descargar CSV",
        data=csv,
        file_name=f"reporte_produccion_{start_date}_{end_date}.csv",
        mime="text/csv"
    )
    
    # Información adicional
    with st.expander("ℹ️ Información Adicional"):
        st.write(f"**Registros obtenidos:** {len(df)}")
        st.write(f"**Rango de fechas:** {start_date} - {end_date}")
        st.write(f"**Última actualización:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()

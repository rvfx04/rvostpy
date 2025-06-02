import streamlit as st
import pyodbc
import pandas as pd
from datetime import datetime, date
import os

# Configuración de la página
st.set_page_config(
    page_title="Reporte de Producción",
    page_icon="📊",
    layout="wide"
)

def get_connection():
    """Crear conexión a SQL Server usando variables de entorno o secrets de Streamlit"""
    try:
        # Intentar obtener credenciales de Streamlit secrets (para la nube)
        if hasattr(st, 'secrets') and 'database' in st.secrets:
            server = st.secrets.database.server
            database = st.secrets.database.database
            username = st.secrets.database.username
            password = st.secrets.database.password
            driver = st.secrets.database.get('driver', 'ODBC Driver 17 for SQL Server')
        else:
            # Usar variables de entorno (para desarrollo local)
            server = os.getenv('DB_SERVER')
            database = os.getenv('DB_DATABASE')
            username = os.getenv('DB_USERNAME')
            password = os.getenv('DB_PASSWORD')
            driver = os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
        
        # Crear string de conexión
        conn_str = f"""
        DRIVER={{{driver}}};
        SERVER={server};
        DATABASE={database};
        UID={username};
        PWD={password};
        """
        
        return pyodbc.connect(conn_str)
    
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {str(e)}")
        return None

def execute_query(fecha_inicio, fecha_fin):
    """Ejecutar la consulta SQL con las fechas proporcionadas"""
    
    # La consulta SQL original
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
    
    conn = get_connection()
    if conn is None:
        return None
    
    try:
        df = pd.read_sql(sql_query, conn, params=[fecha_inicio, fecha_fin])
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error al ejecutar la consulta: {str(e)}")
        conn.close()
        return None

def main():
    st.title("📊 Reporte de Producción por Cliente")
    st.markdown("---")
    
    # Sidebar para filtros
    with st.sidebar:
        st.header("🔧 Configuración")
        
        # Selector de fechas
        st.subheader("Rango de Fechas")
        fecha_inicio = st.date_input(
            "Fecha de inicio",
            value=date(2025, 5, 1),
            help="Selecciona la fecha de inicio del reporte"
        )
        
        fecha_fin = st.date_input(
            "Fecha de fin",
            value=date(2025, 12, 31),
            help="Selecciona la fecha de fin del reporte"
        )
        
        # Validar que la fecha de inicio sea menor que la de fin
        if fecha_inicio > fecha_fin:
            st.error("⚠️ La fecha de inicio debe ser anterior a la fecha de fin")
            return
        
        # Botón para ejecutar consulta
        ejecutar = st.button("🔄 Actualizar Reporte", type="primary")
    
    # Contenido principal
    if ejecutar or 'df_resultados' not in st.session_state:
        with st.spinner("Ejecutando consulta..."):
            df = execute_query(fecha_inicio, fecha_fin)
            
            if df is not None:
                st.session_state.df_resultados = df
                st.success(f"✅ Consulta ejecutada exitosamente. Se encontraron {len(df)} registros.")
            else:
                st.error("❌ No se pudo ejecutar la consulta.")
                return
    
    # Mostrar resultados si existen
    if 'df_resultados' in st.session_state:
        df = st.session_state.df_resultados
        
        if not df.empty:
            # Información del reporte
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📅 Total de días", len(df))
            with col2:
                # Sumar columna TOTAL si existe
                total_unidades = df['TOTAL'].sum() if 'TOTAL' in df.columns else 0
                st.metric("📦 Total unidades", f"{total_unidades:,}")
            with col3:
                promedio_diario = total_unidades / len(df) if len(df) > 0 else 0
                st.metric("📈 Promedio diario", f"{promedio_diario:.1f}")
            
            st.markdown("---")
            
            # Mostrar tabla
            st.subheader("📋 Datos del Reporte")
            
            # Opciones de visualización
            col1, col2 = st.columns([3, 1])
            with col2:
                mostrar_indices = st.checkbox("Mostrar índices", value=False)
            
            # Mostrar dataframe
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=not mostrar_indices
            )
            
            # Botón de descarga
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar CSV",
                data=csv,
                file_name=f'reporte_produccion_{fecha_inicio}_{fecha_fin}.csv',
                mime='text/csv'
            )
            
        else:
            st.warning("⚠️ No se encontraron datos para el rango de fechas seleccionado.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<div style="text-align: center; color: #666;">Reporte de Producción - Powered by Streamlit</div>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()

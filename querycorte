import streamlit as st
import pandas as pd
import pyodbc
from datetime import datetime, date
import calendar

# Configuración de la página
st.set_page_config(
    page_title="Consulta Avance de Producción",
    page_icon="📊",
    layout="wide"
)

# Título de la aplicación
st.title("📊 Consulta Avance de Producción")
st.markdown("---")

# Función para conectar a la base de datos
@st.cache_resource
def init_connection():
    try:
        # Obtener credenciales desde secrets
        server = st.secrets["database"]["server"]
        database = st.secrets["database"]["database"]
        username = st.secrets["database"]["username"]
        password = st.secrets["database"]["password"]
        
        # Cadena de conexión
        connection_string = f"""
        DRIVER={{ODBC Driver 17 for SQL Server}};
        SERVER={server};
        DATABASE={database};
        UID={username};
        PWD={password};
        """
        
        conn = pyodbc.connect(connection_string)
        return conn
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {str(e)}")
        return None

# Función para ejecutar la consulta
@st.cache_data
def run_query(fecha_inicio, fecha_fin, pedidos_list=None, cliente_filtro=None):
    conn = init_connection()
    if conn is None:
        return None
    
    try:
        # Query base
        query = """
        SELECT b.CoddocOrdenProduccion AS OP,
               c.NommaeCentroCosto AS PROCESO,
               e.NommaeCombo AS COMBO,
               FORMAT(CAST(b.dtFechaEntrega AS DATETIME), 'dd-MMM') AS F_ENTREGA,
               LEFT(i.NommaeAnexoCliente,15) AS CLIENTE,
               j.CoddocOrdenVenta AS PEDIDO,
               FORMAT(CAST(j.dtFechaPlanea AS DATETIME), 'dd-MMM') AS F_PLAN,
               LEFT(h.nvModelo,15) AS ESTILO,
               a.dCantidadRequerido AS REQUERI,
               a.dCantidadProgramado AS PROG,
               a.dCantidadProducido AS PRODUC,
               a.dCantidadProgramado - a.dCantidadProducido AS PENDIENTE,
               FORMAT(ROUND(
                   CASE
                      WHEN a.dCantidadProgramado <> 0 THEN a.dCantidadProducido / a.dCantidadRequerido
                      ELSE 0
                   END, 5), 'P0') AS PORCENT
        FROM dbo.fntOrdenProduccion_AvanceProduccion_Combo() a
        INNER JOIN dbo.docOrdenProduccion b WITH (NOLOCK)
           ON a.IdDocumento_OrdenProduccion = b.IdDocumento_OrdenProduccion
        INNER JOIN dbo.maeCentroCosto c WITH (NOLOCK)
           ON a.IdmaeCentroCosto = c.IdmaeCentroCosto
        INNER JOIN dbo.maeCombo e WITH (NOLOCK)
           ON a.IdmaeCombo = e.IdmaeCombo
        INNER JOIN dbo.docOrdenProduccionRuta g WITH (NOLOCK)
           ON a.IddocOrdenProduccionRuta = g.IddocOrdenProduccionRuta
        INNER JOIN dbo.maeEstilo h WITH (NOLOCK)
           ON b.IdmaeEstilo = h.IdmaeEstilo
        INNER JOIN dbo.maeAnexoCliente i WITH (NOLOCK)
           ON b.IdmaeAnexo_Cliente = i.IdmaeAnexo_Cliente
        INNER JOIN dbo.docOrdenVenta j WITH (NOLOCK)
           ON b.IdDocumento_Referencia = j.IdDocumento_OrdenVenta
        WHERE j.dtFechaPlanea BETWEEN ? AND ? AND c.IdmaeCentroCosto = 29
        """
        
        params = [fecha_inicio, fecha_fin]
        
        # Agregar filtro por pedidos si se proporciona
        if pedidos_list and len(pedidos_list) > 0:
            # Crear placeholders para los pedidos
            pedidos_placeholders = ','.join(['?' for _ in pedidos_list])
            query += f" AND j.CoddocOrdenVenta IN ({pedidos_placeholders})"
            params.extend(pedidos_list)
        
        # Agregar filtro por cliente si se proporciona
        if cliente_filtro and cliente_filtro.strip():
            query += " AND i.NommaeAnexoCliente LIKE ?"
            params.append(f"%{cliente_filtro.strip()}%")
        
        # Ejecutar consulta
        df = pd.read_sql(query, conn, params=params)
        conn.close()
        return df
    
    except Exception as e:
        st.error(f"Error al ejecutar la consulta: {str(e)}")
        conn.close()
        return None

# Función para obtener el primer y último día del mes actual
def get_current_month_dates():
    today = date.today()
    first_day = today.replace(day=1)
    last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1])
    return first_day, last_day

# Sidebar para filtros
st.sidebar.header("🔍 Filtros de Búsqueda")

# Filtro de fechas (F_PLAN)
st.sidebar.subheader("📅 Rango de Fechas (F_PLAN)")
primera_fecha, ultima_fecha = get_current_month_dates()

col1, col2 = st.sidebar.columns(2)
with col1:
    fecha_inicio = st.date_input(
        "Fecha Inicio",
        value=primera_fecha,
        key="fecha_inicio"
    )

with col2:
    fecha_fin = st.date_input(
        "Fecha Fin",
        value=ultima_fecha,
        key="fecha_fin"
    )

# Filtro por pedidos
st.sidebar.subheader("📝 Filtro por Pedidos")
pedidos_input = st.sidebar.text_area(
    "Ingrese pedidos (separados por comas):",
    placeholder="Ej: PED001, PED002, PED003",
    help="Ingrese uno o más pedidos separados por comas. Deje vacío para mostrar todos."
)

# Filtro por cliente
st.sidebar.subheader("👤 Filtro por Cliente")
cliente_input = st.sidebar.text_input(
    "Nombre del cliente (completo o parcial):",
    placeholder="Ej: ACME Corp",
    help="Ingrese el nombre completo o parte del nombre del cliente. Deje vacío para mostrar todos."
)

# Botón para ejecutar consulta
ejecutar_consulta = st.sidebar.button("🚀 Ejecutar Consulta", type="primary")

# Validación de fechas
if fecha_inicio > fecha_fin:
    st.sidebar.error("⚠️ La fecha de inicio no puede ser mayor que la fecha de fin")
    ejecutar_consulta = False

# Procesar pedidos
pedidos_list = []
if pedidos_input.strip():
    pedidos_list = [pedido.strip() for pedido in pedidos_input.split(',') if pedido.strip()]

# Área principal
if ejecutar_consulta:
    with st.spinner('Ejecutando consulta...'):
        # Ejecutar consulta
        df = run_query(
            fecha_inicio.strftime('%Y-%m-%d'),
            fecha_fin.strftime('%Y-%m-%d'),
            pedidos_list if pedidos_list else None,
            cliente_input if cliente_input.strip() else None
        )
        
        if df is not None and not df.empty:
            # Mostrar métricas
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Registros", len(df))
            
            with col2:
                total_requerido = df['REQUERI'].sum()
                st.metric("Total Requerido", f"{total_requerido:,.0f}")
            
            with col3:
                total_producido = df['PRODUC'].sum()
                st.metric("Total Producido", f"{total_producido:,.0f}")
            
            with col4:
                total_pendiente = df['PENDIENTE'].sum()
                st.metric("Total Pendiente", f"{total_pendiente:,.0f}")
            
            st.markdown("---")
            
            # Mostrar filtros aplicados
            st.subheader("🔍 Filtros Aplicados:")
            filtros_info = f"📅 **Período:** {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}"
            
            if pedidos_list:
                filtros_info += f" | 📝 **Pedidos:** {', '.join(pedidos_list)}"
            
            if cliente_input.strip():
                filtros_info += f" | 👤 **Cliente:** {cliente_input}"
            
            st.markdown(filtros_info)
            st.markdown("---")
            
            # Mostrar tabla de resultados
            st.subheader("📊 Resultados de la Consulta")
            
            # Configurar la tabla para que sea más legible
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "REQUERI": st.column_config.NumberColumn(
                        "REQUERI",
                        format="%.0f"
                    ),
                    "PROG": st.column_config.NumberColumn(
                        "PROG",
                        format="%.0f"
                    ),
                    "PRODUC": st.column_config.NumberColumn(
                        "PRODUC",
                        format="%.0f"
                    ),
                    "PENDIENTE": st.column_config.NumberColumn(
                        "PENDIENTE",
                        format="%.0f"
                    ),
                    "PORCENT": st.column_config.TextColumn("PORCENT")
                }
            )
            
            # Opción para descargar datos
            st.markdown("---")
            col1, col2 = st.columns([1, 4])
            with col1:
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Descargar CSV",
                    data=csv,
                    file_name=f'avance_produccion_{fecha_inicio}_{fecha_fin}.csv',
                    mime='text/csv'
                )
            
        elif df is not None and df.empty:
            st.warning("⚠️ No se encontraron registros con los filtros aplicados.")
        
        else:
            st.error("❌ Error al ejecutar la consulta. Verifique la conexión a la base de datos.")

else:
    # Mostrar información inicial
    st.info("👆 Configure los filtros en el panel lateral y presione 'Ejecutar Consulta' para ver los resultados.")
    
    # Mostrar información sobre los filtros
    st.markdown("""
    ### 📋 Instrucciones de Uso:
    
    1. **📅 Rango de Fechas**: Por defecto se muestran las fechas del mes actual. Modifique según necesite.
    
    2. **📝 Filtro por Pedidos**: 
       - Ingrese uno o más números de pedido separados por comas
       - Ejemplo: `PED001, PED002, PED003`
       - Deje vacío para mostrar todos los pedidos
    
    3. **👤 Filtro por Cliente**:
       - Ingrese el nombre completo o parte del nombre del cliente
       - La búsqueda no distingue mayúsculas/minúsculas
       - Deje vacío para mostrar todos los clientes
    
    4. **🚀 Ejecutar**: Presione el botón "Ejecutar Consulta" para ver los resultados
    
    5. **📥 Descargar**: Una vez obtenidos los resultados, podrá descargar los datos en formato CSV
    """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>Sistema de Consulta de Avance de Producción | Desarrollado con Streamlit</p>
    </div>
    """, 
    unsafe_allow_html=True
)

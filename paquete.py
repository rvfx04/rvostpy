import streamlit as st
import pyodbc
import pandas as pd

# Estilos CSS para hacer la presentación más compacta
st.markdown(
    """
    <style>
    /* Reduce el tamaño de los títulos */
    h1 {
        font-size: 1.5em;
    }
    h2 {
        font-size: 1.25em;
    }
    h3 {
        font-size: 1em;
    }
    
    /* Reduce el tamaño del texto */
    .reportview-container .main .block-container {
        font-size: 0.875em;
    }
    
    /* Ajusta el tamaño de las tablas */
    .dataframe th, .dataframe td, .stTable th, .stTable td {
        padding: 0.25em 0.5em;
        font-size: 0.875em;
    }
    
    /* Ajusta los márgenes y el padding para mayor compacidad */
    .main .block-container {
        padding: 1rem 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Función para establecer la conexión a la base de datos
def get_db_connection():
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=" + st.secrets["server"] + ";"
        "DATABASE=" + st.secrets["database"] + ";"
        "UID=" + st.secrets["username"] + ";"
        "PWD=" + st.secrets["password"] + ";"
    )
    return conn

# Variable de estado para controlar si se muestra el formulario o los resultados
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

def submit_form():
    st.session_state.submitted = True
    st.session_state.os = st.session_state.form_os
    st.session_state.max_prendas = st.session_state.form_max_prendas

def reset_form():
    st.session_state.submitted = False

# Mostrar el formulario solo si no se ha enviado
if not st.session_state.submitted:
    # Título del formulario
    st.title("Control de Paquetes")

    # Crear el formulario en Streamlit
    with st.form("consulta_form"):
        st.session_state.form_os = st.text_input("Número de Orden de Servicio (OS):", "")
        st.session_state.form_max_prendas = st.number_input("Número Máximo de Prendas por Paquete:", min_value=1, step=1)
        submitted = st.form_submit_button("Consultar y Generar Tabla", on_click=submit_form)

if st.session_state.submitted:
    conn = get_db_connection()

    # Consulta SQL
    sql = f"""
    SELECT d.CoddocOrdenVenta AS PEDIDO, i.NommaeAnexoCliente AS CLIENTE, d.nvDocumentoReferencia AS PO, 
           c.CoddocOrdenProduccion AS OP, b.CoddocOrdenTrabajo AS OS, f.NommaeEstilo AS ESTILO, 
           g.NommaeCombo AS COMBO, b.ntObservacion AS OBS, RIGHT(j.ntDescripcion, 35) AS MP, 
           h.NommaeTalla AS TALLA, h.iSecuencia AS ORDEN_TALLA, a.dCantidad AS CANTIDAD 
    FROM docOrdenTrabajoProduccion a 
    INNER JOIN docOrdenTrabajo b ON a.IdDocumento_OrdenTrabajo = b.IdDocumento_OrdenTrabajo
    INNER JOIN docOrdenProduccion c ON b.IdDocumento_Referencia = c.IdDocumento_OrdenProduccion
    INNER JOIN docOrdenVenta d ON c.IdDocumento_Referencia = d.IdDocumento_OrdenVenta
    INNER JOIN maeItemInventario e ON e.IdmaeItem_Inventario = a.IdmaeItem
    INNER JOIN maeEstilo f ON e.IdmaeEstilo = f.IdmaeEstilo
    INNER JOIN maeCombo g ON a.idmaecombo = g.IdmaeCombo
    INNER JOIN maeTalla h ON h.IdmaeTalla = a.IdmaeTalla
    INNER JOIN maeAnexoCliente i ON d.IdmaeAnexo_Cliente = i.IdmaeAnexo_Cliente
    INNER JOIN docOrdentrabajoItem j ON b.IdDocumento_OrdenTrabajo = j.IdDocumento_OrdenTrabajo
    WHERE b.IdmaeCentroCosto = 29 AND b.CoddocOrdenTrabajo = ?
    UNION ALL
    SELECT d.CoddocOrdenVenta AS PEDIDO, i.NommaeAnexoCliente AS CLIENTE, d.nvDocumentoReferencia AS PO, 
           c.CoddocOrdenProduccion AS OP, b.CoddocOrdenCompra AS OS, f.NommaeEstilo AS ESTILO, 
           g.NommaeCombo AS COMBO, b.ntObservacion AS OBS, RIGHT(j.ntDescripcion, 35) AS MP, 
           h.NommaeTalla AS TALLA, h.iSecuencia AS ORDEN_TALLA, a.dCantidad AS CANTIDAD 
    FROM docOrdenCompraProduccion a 
    INNER JOIN docOrdenCompra b ON a.IdDocumento_OrdenCompra = b.IdDocumento_OrdenCompra
    INNER JOIN docOrdenProduccion c ON b.IdDocumento_Referencia = c.IdDocumento_OrdenProduccion
    INNER JOIN docOrdenVenta d ON c.IdDocumento_Referencia = d.IdDocumento_OrdenVenta
    INNER JOIN maeItemInventario e ON e.IdmaeItem_Inventario = a.IdmaeItem
    INNER JOIN maeEstilo f ON e.IdmaeEstilo = f.IdmaeEstilo
    INNER JOIN maeCombo g ON a.idmaecombo = g.IdmaeCombo
    INNER JOIN maeTalla h ON h.IdmaeTalla = a.IdmaeTalla
    INNER JOIN maeAnexoCliente i ON d.IdmaeAnexo_Cliente = i.IdmaeAnexo_Cliente
    INNER JOIN docOrdenCompraItem j ON b.IdDocumento_OrdenCompra = j.IdDocumento_OrdenCompra
    WHERE b.IdmaeCentroCosto = 29 AND b.CoddocOrdenCompra = ?
    ORDER BY ORDEN_TALLA
    """
    
    # Ejecutar la consulta
    cursor = conn.cursor()
    cursor.execute(sql, (st.session_state.os, st.session_state.os))
    rows = cursor.fetchall()
    
    # Procesar resultados
    resultado = []
    for row in rows:
        talla = row.TALLA.strip()
        cantidad = int(row.CANTIDAD)
        num_prenda_inicial = 1
        
        pedido = row.PEDIDO
        cliente = row.CLIENTE
        po = row.PO
        op = row.OP
        os = row.OS
        estilo = row.ESTILO
        combo = row.COMBO
        obs = row.OBS
        mp = row.MP

        while cantidad > 0:
            if cantidad <= st.session_state.max_prendas:
                prendas_en_caja = cantidad
            else:
                if cantidad - st.session_state.max_prendas < 10:
                    prendas_en_caja = cantidad
                else:
                    prendas_en_caja = st.session_state.max_prendas
            num_prenda_final = num_prenda_inicial + prendas_en_caja - 1
            resultado.append((talla, prendas_en_caja, num_prenda_inicial, num_prenda_final))
            num_prenda_inicial += prendas_en_caja
            cantidad -= prendas_en_caja

    # Calcular las cantidades totales por talla
    cantidades_totales = {}
    for row in resultado:
        talla = row[0]
        cantidad = row[1]
        if talla in cantidades_totales:
            cantidades_totales[talla] += cantidad
        else:
            cantidades_totales[talla] = cantidad

    # Mostrar resultados
    st.subheader("Control de paquetes:")
    st.write("**PEDIDO:** {}".format(pedido))
    st.write("**CLIENTE:** {}".format(cliente))
    st.write("**PO:** {}".format(po))
    st.write("**OP:** {}".format(op))
    st.write("**OS:** {}".format(os))
    st.write("**ESTILO:** {}".format(estilo))
    st.write("**COMBO:** {}".format(combo))
    st.write("**OBS:** {}".format(obs))
    st.write("**MP:** {}".format(mp))

    # Tabla de cantidades por talla
    st.subheader("Cantidades por Talla:")
    cantidades_por_talla_df = pd.DataFrame(cantidades_totales.items(), columns=['Talla', 'Cantidad'])
    st.table(cantidades_por_talla_df)

    # Tabla resultante con número correlativo
    st.subheader("Distribución de Prendas en las Cajas:")
    resultado_df = pd.DataFrame(resultado, columns=['TALLA', 'CANTIDAD', 'Prenda Ini', 'Prenda Fin'])
    resultado_df['#'] = range(1, len(resultado_df) + 1)
    st.table(resultado_df[['#', 'TALLA', 'CANTIDAD', 'Prenda Ini', 'Prenda Fin']])

    # Cerrar la conexión
    cursor.close()
    conn.close()

    # Botón para realizar otra consulta
    if st.button('Realizar otra consulta'):
        reset_form()




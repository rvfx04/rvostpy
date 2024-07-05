import streamlit as st
from op import app as op_app
from pedido import app as pedido_app
from taller import app as taller_app
from progreso import app as progreso_app

# Crear páginas para cada aplicación
page_op = st.page(title='Operaciones')
page_pedido = st.page(title='Pedidos')
page_taller = st.page(title='Taller')
page_progreso = st.page(title='Progreso')

# Contenido de la página de Operaciones
with page_op:
    op_app()  # Ejecutar la aplicación de operaciones

# Contenido de la página de Pedidos
with page_pedido:
    pedido_app()  # Ejecutar la aplicación de pedidos

# Contenido de la página de Taller
with page_taller:
    taller_app()  # Ejecutar la aplicación de taller

# Contenido de la página de Progreso
with page_progreso:
    progreso_app()  # Ejecutar la aplicación de progreso

import streamlit as st

def main():
    st.title("Menú de Navegación")

    # Crear el menú de navegación
    menu = ["Home", "Pedido", "OP"]
    choice = st.sidebar.selectbox("Selecciona una aplicación", menu)

    if choice == "Home":
        st.subheader("Bienvenido al Menú de Navegación")
        st.write("Selecciona una aplicación desde la barra lateral.")
    elif choice == "Pedido":
        st.experimental_set_query_params(app="pedido")
        st.write("Redirigiendo a Pedido...")
        st.experimental_rerun()
    elif choice == "OP":
        st.experimental_set_query_params(app="op")
        st.write("Redirigiendo a OP...")
        st.experimental_rerun()

if __name__ == '__main__':
    main()

# Manejar la redirección según los parámetros de consulta
query_params = st.experimental_get_query_params()
if "app" in query_params:
    app = query_params["app"][0]
    if app == "pedido":
        st.write("Redirigiendo a Pedido...")
        st.experimental_rerun("https://appgtpedido.streamlit.app")
    elif app == "op":
        st.write("Redirigiendo a OP...")
        st.experimental_rerun("https://appgtop.streamlit.app")


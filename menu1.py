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
        js_code = "window.location.href = 'https://appgtpedido.streamlit.app';"
        st.components.v1.html(f"<script>{js_code}</script>")
    elif choice == "OP":
        js_code = "window.location.href = 'https://appgtop.streamlit.app';"
        st.components.v1.html(f"<script>{js_code}</script>")

if __name__ == '__main__':
    main()

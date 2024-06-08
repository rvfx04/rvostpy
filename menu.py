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
        #st.subheader("Pedido")
        #st.write("Haga clic en el siguiente enlace para ir a la aplicación:")
        st.markdown("[Ir a Pedido](https://appgtpedido.streamlit.app)")
    elif choice == "OP":
        st.subheader("OP")
        st.write("Haga clic en el siguiente enlace para ir a la aplicación:")
        st.markdown("[Ir a OP](https://appgtop.streamlit.app)")

if __name__ == '__main__':
    main()


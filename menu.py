import streamlit as st

def main():
    st.title("Menú de Navegación")

    # Crear el menú de navegación
    menu = ["Home", "App 1: appgtpedido", "App 2: appgtop"]
    choice = st.sidebar.selectbox("Selecciona una aplicación", menu)

    if choice == "Home":
        st.subheader("Bienvenido al Menú de Navegación")
        st.write("Selecciona una aplicación desde la barra lateral.")
    elif choice == "App 1: appgtpedido":
        st.subheader("App 1: appgtpedido")
        st.write("Haga clic en el siguiente enlace para ir a la aplicación:")
        st.markdown("[Ir a appgtpedido](https://appgtpedido.streamlit.app)")
    elif choice == "App 2: appgtop":
        st.subheader("App 2: appgtop")
        st.write("Haga clic en el siguiente enlace para ir a la aplicación:")
        st.markdown("[Ir a appgtop](https://appgtop.streamlit.app)")

if __name__ == '__main__':
    main()

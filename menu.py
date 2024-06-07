import streamlit as st

def main():
    st.title("Menú de Navegación")

    # Crear el menú de navegación
    menu = ["Home", "App 1: prurvo", "App 2: rvo012"]
    choice = st.sidebar.selectbox("Selecciona una aplicación", menu)

    if choice == "Home":
        st.subheader("Bienvenido al Menú de Navegación")
        st.write("Selecciona una aplicación desde la barra lateral.")
    elif choice == "App 1: prurvo":
        st.subheader("App 1: prurvo")
        st.write("Haga clic en el siguiente enlace para ir a la aplicación:")
        st.markdown("[Ir a prurvo](https://prurvo.streamlit.app)")
    elif choice == "App 2: rvo012":
        st.subheader("App 2: rvo012")
        st.write("Haga clic en el siguiente enlace para ir a la aplicación:")
        st.markdown("[Ir a rvo012](https://rvo012.streamlit.app)")

if __name__ == '__main__':
    main()

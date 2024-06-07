import streamlit as st

def main():
    st.title("Menú de Navegación")

    # Instrucciones para usar el menú
    st.write("Haga clic en uno de los siguientes botones para ir a la aplicación correspondiente:")

    # Botón para acceder a la aplicación prurvo
    if st.button("Ir a App 1: prurvo"):
        js_code = """
        <script>
        window.open('https://prurvo.streamlit.app', '_blank').focus();
        </script>
        """
        st.markdown(js_code, unsafe_allow_html=True)
    
    # Botón para acceder a la aplicación rvo012
    if st.button("Ir a App 2: rvo012"):
        js_code = """
        <script>
        window.open('https://rvo012.streamlit.app', '_blank').focus();
        </script>
        """
        st.markdown(js_code, unsafe_allow_html=True)

if __name__ == '__main__':
    main()

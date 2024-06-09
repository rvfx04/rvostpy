import streamlit as st

def main():
    st.title("Menú de Navegación")

    # Botón para acceder a la aplicación prurvo
    if st.button("Ir a App 1: prurvo"):
        st.markdown('<meta http-equiv="refresh" content="0; url=https://prurvo.streamlit.app" />', unsafe_allow_html=True)
    
    # Botón para acceder a la aplicación rvo012
    if st.button("Ir a App 2: rvo012"):
        st.markdown('<meta http-equiv="refresh" content="0; url=https://rvo012.streamlit.app" />', unsafe_allow_html=True)

if __name__ == '__main__':
    main()

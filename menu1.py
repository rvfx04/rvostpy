import streamlit as st

def main():
    st.title("Menú 11")

    # Botón para acceder a la aplicación prurvo
    if st.button("Ir a App 1: prurvo"):
        st.markdown("[Ir a Pedido](https://appgtpedido.streamlit.app)")
    
    # Botón para acceder a la aplicación rvo012
    if st.button("Ir a App 2: rvo012"):
        st.markdown("[Ir a OP](https://appgtop.streamlit.app)")

if __name__ == '__main__':
    main()

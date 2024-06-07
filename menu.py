import streamlit as st
from streamlit_option_menu import option_menu

# Importa tus aplicaciones individuales
import app11.py
import app12.py

def main():
    st.title("Aplicación Principal")

    # Crea el menú de navegación
    with st.sidebar:
        selected = option_menu(
            "Menú",
            ["App 11", "App 12"],
            icons=["house", "gear"],
            menu_icon="cast",
            default_index=0,
        )

    # Muestra la aplicación seleccionada
    if selected == "App 11":
        app11.py.run()
    elif selected == "App 12":
        app12.py.run()
    

if __name__ == "__main__":
    main()

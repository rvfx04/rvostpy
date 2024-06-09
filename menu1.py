import streamlit as st
import webbrowser

# Crear las opciones del menú
menu_options = ["Home", "Google", "YouTube"]

# Seleccionar una opción del menú
choice = st.sidebar.selectbox("Selecciona una opción", menu_options)

# Diccionario de opciones y URLs correspondientes
url_dict = {
    "Google": "https://www.google.com",
    "YouTube": "https://www.youtube.com"
}

# Redirigir al usuario a la URL seleccionada
if choice in url_dict:
    st.write(f"Redirigiendo a {choice}...")
    webbrowser.open_new_tab(url_dict[choice])
else:
    st.write("Selecciona una opción del menú para abrir una URL.")

import streamlit as st
st.write("""
# Mi primera app
Hola *world!*
""")
number = st.slider("Elige un número", 0, 100)
date = st.date_input("Elige una fecha")

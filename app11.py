import streamlit as st

def run():
    st.title("App 11")
    st.write("""

import streamlit as st
st.write("""
# Mi primera app
Hola *MUNDO!*
""")
number = st.slider("Elige un número", 0, 100)
date = st.date_input("Elige una fecha")
file = st.file_uploader("Pick a file")
selected_countries = st.multiselect(
    'Which countries would you like to view?',
    ['CHI', 'PER', 'COL', 'ECU', 'BOL'])
""")

import streamlit as st

# Define the functions for each app page
def app_gtop():
    st.title('App GTOP')
    st.write('Contenido de la aplicación GTOP.')

def app_gtpedido():
    st.title('App GTPedido')
    st.write('Contenido de la aplicación GTPedido.')

# Create a sidebar navigation to switch between the app pages
app_selection = st.sidebar.radio("Selecciona la aplicación", ("GTOP", "GTPedido"))

# Show the selected app page based on user selection
if app_selection == "GTOP":
    app_gtop()
else:
    app_gtpedido()

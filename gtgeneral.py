import streamlit as st

# Define the functions for each app page
def app_gtop():
    # Código de la aplicación GTOP aquí
    pass

def app_gtpedido():
    # Código de la aplicación GTPedido aquí
    pass

# Create a sidebar navigation to switch between the app pages
app_selection = st.sidebar.radio("Selecciona la aplicación", ("GTOP", "GTPedido"))

# Show the selected app page based on user selection
if app_selection == "GTOP":
    app_gtop()
else:
    app_gtpedido()

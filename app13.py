import streamlit as st
import pyodbc
import pandas as pd

# Initialize connection.
# Uses st.cache_resource to only run once.
@st.cache_resource
def init_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER="
        + st.secrets["server"]
        + ";DATABASE="
        + st.secrets["database"]
        + ";UID="
        + st.secrets["username"]
        + ";PWD="
        + st.secrets["password"]
    )

conn = init_connection()

# Perform query.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        columns = [column[0] for column in cur.description]
        data = cur.fetchall()
    return columns, data

columns, rows = run_query("SELECT * from defecto;")

# Debugging output
st.write("Columns:", columns)
st.write("Number of columns:", len(columns))
st.write("First row (if available):", rows[0] if rows else "No rows returned")
st.write("Number of rows:", len(rows))

# Convert data to a pandas DataFrame
try:
    # Ensure rows are tuples and not single element tuples
    rows = [tuple(row) for row in rows]
    df = pd.DataFrame(rows, columns=columns)
    # Display the dataframe in Streamlit
    st.dataframe(df)
except ValueError as e:
    st.write(f"Error creating DataFrame: {e}")
    st.write("Rows data:", rows)

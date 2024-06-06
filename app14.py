import streamlit as st
import pyodbc
import pandas as pd

# Initialize connection
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

# Perform query
@st.cache_data(ttl=600)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        columns = [column[0] for column in cur.description]
        data = cur.fetchall()
    return columns, data

columns, rows = run_query("SELECT * from defecto;")

# Debugging output to verify the shape of data
st.write(f"Columns: {columns}")
st.write(f"Number of columns: {len(columns)}")
st.write(f"First row (if available): {rows[0] if rows else 'No rows returned'}")
st.write(f"Number of rows: {len(rows)}")

# Ensure rows are tuples
rows = [tuple(row) for row in rows]

# Convert data to a pandas DataFrame
try:
    df = pd.DataFrame(rows, columns=columns)
    st.dataframe(df)
except ValueError as e:
    st.error(f"Error creating DataFrame: {e}")
    st.write(f"Shape of passed values: {len(rows)} rows, {len(rows[0]) if rows else 0} columns")
    st.write(f"Columns: {columns}")
    st.write(f"Rows: {rows[:5]} (showing first 5 rows)")


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

# Ensure rows are tuples
rows = [tuple(row) for row in rows]

# Convert data to a pandas DataFrame
df = pd.DataFrame(rows, columns=columns)

# Custom CSS to inject smaller font sizes and padding for table
st.markdown(
    """
    <style>
    .dataframe th, .dataframe td {
        font-size: 11px;    /* Smaller font size */
        padding: 4px 4px;  /* Smaller padding */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Display the DataFrame as a table without the index column
st.table(df)

import os
import re
import tempfile
import csv

import streamlit as st
import pandas as pd
import duckdb
from groq import Groq

# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------
API_KEY = os.environ.get("GROQ_API_KEY")
if not API_KEY:
    st.error("Please set the GROQ_API_KEY environment variable before running.")
    st.stop()

client = Groq(api_key=API_KEY)

# -----------------------------------------------------------------------------
# UTILITY FUNCTIONS
# -----------------------------------------------------------------------------
def generate_sql_query(columns: list[str], user_question: str) -> str:
    cols = ", ".join(columns)
    prompt = (
        "You are a SQL expert. Given a DuckDB table `uploaded_data` with columns: "
        f"{cols}\n\n"
        f"Write a DuckDB-compatible SQL query that answers this question:\n\"{user_question}\"\n\n"
        "Return only the SQL query enclosed in triple backticks ```sql ... ```."
    )
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
    )
    content = response.choices[0].message.content
    match = re.search(r"```sql\s*(.*?)```", content, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else content.strip()

def preprocess_and_save(uploaded_file) -> tuple[str, list[str]]:
    name = uploaded_file.name.lower()
    # Define additional NA markers
    na_values = ["NA", "N/A", "missing", "NULL", "null", ""]
    try:
        if name.endswith('.csv'):
            df = pd.read_csv(
                uploaded_file,
                encoding='utf-8',
                na_values=na_values,
                keep_default_na=True
            )
        elif name.endswith(('.xls', '.xlsx')):
            try:
                import openpyxl  # noqa: F401
            except ImportError:
                st.error("Missing dependency 'openpyxl'. Please install it with `pip install openpyxl`.")
                st.stop()
            df = pd.read_excel(
                uploaded_file,
                engine='openpyxl',
                na_values=na_values,
                keep_default_na=True
            )
        else:
            st.error("Unsupported file type; please upload a .csv, .xls, or .xlsx file.")
            st.stop()
    except Exception as e:
        st.error(f"Failed to read file: {e}")
        st.stop()

    # Auto-detect and convert date columns
    for col in df.columns:
        if "date" in col.lower():
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # Auto-convert numeric strings
    for col in df.select_dtypes(include=['object']).columns:
        # Try to convert strings that look numeric
        df[col] = pd.to_numeric(df[col], errors='ignore')

    # --- MISSING DATA HANDLING ---
    # Numeric columns: fill NaN with median
    num_cols = df.select_dtypes(include=['number']).columns
    for col in num_cols:
        median = df[col].median()
        df[col] = df[col].fillna(median)

    # Object / categorical columns: fill NaN with 'Unknown'
    obj_cols = df.select_dtypes(include=['object']).columns
    for col in obj_cols:
        df[col] = df[col].fillna("Unknown")

    # Date columns: leave NaT as-is or could fill with a sentinel if desired
    # e.g. df[date_cols] = df[date_cols].fillna(pd.Timestamp("1900-01-01"))

    # Save to a temp CSV for DuckDB ingestion
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    df.to_csv(tmp.name, index=False, quoting=csv.QUOTE_ALL)
    return tmp.name, list(df.columns)

# -----------------------------------------------------------------------------
# STREAMLIT APP
# -----------------------------------------------------------------------------
st.set_page_config(layout="wide")
st.title("Data-Analyst Agent")

# Initialize history
if "history" not in st.session_state:
    st.session_state.history = []

uploaded = st.file_uploader(
    "Upload a CSV or Excel file",
    type=["csv", "xls", "xlsx"]
)
if not uploaded:
    st.info("Please upload a CSV or Excel file.")
    st.stop()

csv_path, cols = preprocess_and_save(uploaded)
date_cols = [c for c in cols if "date" in c.lower()]
df = pd.read_csv(csv_path, parse_dates=date_cols)
st.subheader("Data Preview")
st.dataframe(df)

# Load into DuckDB
con = duckdb.connect(':memory:')
con.execute(f"""
    CREATE TABLE uploaded_data AS 
    SELECT * FROM read_csv_auto('{csv_path}')
""")

# Query form
st.subheader("Ask a question about your data")
with st.form(key="form"):
    user_q = st.text_area("Question", height=100)
    submit = st.form_submit_button("Run Query")

if submit:
    if not user_q.strip():
        st.warning("Enter a question.")
    else:
        raw_sql = generate_sql_query(cols, user_q)
        sql = raw_sql.replace('`', '"')
        try:
            result_df = con.execute(sql).fetchdf()
            st.session_state.history.append(
                {"question": user_q, "sql": sql, "result": result_df}
            )
        except Exception as e:
            err = str(e)
            # Handle string conversion fallback
            if "Could not convert string" in err:
                m = re.search(r'WHERE\s+"(.+?)"\s+=\s+\'(.+?)\'', sql)
                if m:
                    col, val = m.group(1), m.group(2)
                    fallback_sql = re.sub(
                        rf'WHERE\s+"{col}"\s+=\s+\'{val}\'',
                        f'WHERE CAST("{col}" AS VARCHAR) = \'{val}\'',
                        sql
                    )
                    try:
                        result_df = con.execute(fallback_sql).fetchdf()
                        st.warning("Applied fallback: casting to string.")
                        st.session_state.history.append(
                            {"question": user_q, "sql": fallback_sql, "result": result_df}
                        )
                    except Exception as e2:
                        st.error(f"Fallback failed: {e2}")
                else:
                    st.error(f"Error: {err}")
            else:
                st.error(f"Error: {err}")

# Display history
if st.session_state.history:
    st.subheader("Query History")
    for idx, entry in enumerate(reversed(st.session_state.history), 1):
        with st.expander(f"Query {len(st.session_state.history) - idx + 1}: {entry['question']}"):
            st.markdown("**SQL:**")
            st.code(entry['sql'], language="sql")
            st.markdown("**Result:**")
            st.dataframe(entry['result'])

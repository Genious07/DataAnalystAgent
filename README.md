# 📊 Data-Analyst Agent

An interactive Streamlit application that leverages DuckDB for fast, in-memory data analysis and Groq’s AI-powered SQL generation. Upload your CSV or Excel files, ask natural language questions about your data, and get SQL-powered answers instantly.

---

## 🚀 Features

* **Automatic Data Preprocessing**: Handles CSV, XLS, and XLSX files with custom NA values, date parsing, and numeric conversion.
* **Missing Data Handling**:

  * Numeric columns: fills missing values with the median.
  * Categorical columns: fills missing values with `Unknown`.
  * Date columns: auto-detected and parsed (option to fill sentinel values if desired).
* **AI-Powered SQL Generation**: Uses Groq’s `llama-3.3-70b-versatile` model to convert plain English questions into DuckDB-compatible SQL queries.
* **Fast, In-Memory Analytics**: DuckDB powers lightning-fast analytical queries directly in memory.
* **Query History**: View past questions, SQL queries, and results in an expandable history panel.

---

## 📋 Prerequisites

* Python 3.8+
* A valid Groq API key (set `GROQ_API_KEY` environment variable)

---

## 🔧 Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/duckdb-groq-data-analyst.git
   cd duckdb-groq-data-analyst
   ```

2. **Create a virtual environment and install dependencies**

   ```bash
   python -m venv venv
   source venv/bin/activate   # macOS/Linux
   venv\Scripts\activate    # Windows

   pip install -r requirements.txt
   ```

3. **Set your Groq API key**

   ```bash
   export GROQ_API_KEY="your_api_key_here"   # macOS/Linux
   set GROQ_API_KEY="your_api_key_here"      # Windows
   ```

---

## ⚙️ Configuration

The script for the Streamlit app is `ai_data_analyst.py`. Main configuration:

* `GROQ_API_KEY`: Your Groq API key (must be set in environment).
* Supported file types: `.csv`, `.xls`, `.xlsx`.
* Default NA markers: `NA`, `N/A`, `missing`, `NULL`, `null`, and empty strings.

You can customize NA handling, date parsing logic, or median fill strategy directly in the utility functions.

---

## 🚀 Usage

1. **Run the Streamlit app**

   ```bash
   streamlit run ai_data_analyst.py
   ```

2. **Upload your data**

   * Supports CSV, XLS, XLSX files.
   * Preview your data in an interactive table.

3. **Ask questions**

   * Enter natural language questions about your dataset, e.g.:

     * "What is the average sales by region?"
     * "Show me total revenue per month for 2024."
   * Click **Run Query**.

4. **View results**

   * Generated SQL query is shown.
   * Query results are displayed as a DataFrame.
   * Fallback casting is applied automatically for string conversion issues.

---

## 🛠️ Code Structure

```text
├── ai_data_analyst.py      # Main Streamlit application
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

* **Utility Functions** (`preprocess_and_save`, `generate_sql_query`): handle data preprocessing and AI SQL generation.
* **Streamlit Layout**: manages file upload, preprocessing, DuckDB ingestion, question form, and history display.

---

## 🤝 Contributing

Contributions are welcome! Please open issues or pull requests on GitHub.

1. Fork the repo.
2. Create your feature branch (`git checkout -b feature/YourFeature`).
3. Commit your changes (`git commit -m 'Add YourFeature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a Pull Request.

---

## 📄 License

This project is licensed under the [MIT License](./LICENSE).

---

## 📧 Contact

For questions or feedback, reach out to `youremail@example.com`.

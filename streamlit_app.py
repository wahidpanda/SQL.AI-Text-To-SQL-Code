import streamlit as st
import os
import sqlite3
import google.generativeai as genai
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import re
import base64

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Predefined SQL commands
sql_commands = {
    "Retrieve all employees": "SELECT * FROM EMPLOYEE;",
    "Retrieve employees with a specific salary range": "SELECT * FROM EMPLOYEE WHERE SALARY BETWEEN 50000 AND 70000;",
    "High Salary Employees": "SELECT * FROM EMPLOYEE WHERE SALARY > 80000;",
    "Female Employees": "SELECT * FROM EMPLOYEE WHERE GENDER = 'Female';",
    "Young Employees (Age < 30)": "SELECT * FROM EMPLOYEE WHERE AGE < 30;",
    "Top 10 Working Hours": "SELECT * FROM EMPLOYEE ORDER BY WORKING_HOURS DESC LIMIT 10;",
    "Top 10 Monthly Lunch Bills": "SELECT * FROM EMPLOYEE ORDER BY MONTHLY_LUNCH_BILL DESC LIMIT 10;",
    "Employees in IT Department": "SELECT * FROM EMPLOYEE WHERE DEPARTMENT = 'IT';",
    "Senior Managers": "SELECT * FROM EMPLOYEE WHERE DESIGNATION = 'Senior Manager';",
    "Lowest Salary Employees": "SELECT * FROM EMPLOYEE ORDER BY SALARY ASC LIMIT 10;",
    "Employees with Bonus": "SELECT * FROM EMPLOYEE WHERE BONUS > 0;"
}

# Additional predefined SQL commands
additional_commands = {
    "All Employees": "SELECT * FROM EMPLOYEE;",
    "High Salary Employees": "SELECT * FROM EMPLOYEE WHERE SALARY > 80000;",
    "Female Employees": "SELECT * FROM EMPLOYEE WHERE GENDER = 'Female';",
    "Young Employees (Age < 30)": "SELECT * FROM EMPLOYEE WHERE AGE < 30;",
    "Top 10 Working Hours": "SELECT * FROM EMPLOYEE ORDER BY WORKING_HOURS DESC LIMIT 10;",
    "Top 10 Monthly Lunch Bills": "SELECT * FROM EMPLOYEE ORDER BY MONTHLY_LUNCH_BILL DESC LIMIT 10;",
    "Employees in IT Department": "SELECT * FROM EMPLOYEE WHERE DEPARTMENT = 'IT';",
    "Senior Managers": "SELECT * FROM EMPLOYEE WHERE DESIGNATION = 'Senior Manager';",
    "Lowest Salary Employees": "SELECT * FROM EMPLOYEE ORDER BY SALARY ASC LIMIT 10;",
    "Employees with Bonus": "SELECT * FROM EMPLOYEE WHERE BONUS > 0;"
}

prompt = [
    """
    You are an expert in converting English questions to SQL query!
    The SQL database has the name EMPLOYEE and has the following columns - 
    ID, NAME, SALARY, AGE, GENDER, DESIGNATION, WORKING_HOURS, MONTHLY_LUNCH_BILL, BONUS
    \n\nFor example,\nExample 1 - Retrieve all employees
    the SQL command will be something like this SELECT * FROM EMPLOYEE;
    \nExample 2 - Retrieve employees with a specific salary range
    the SQL command will be something like this SELECT * FROM EMPLOYEE
    WHERE SALARY BETWEEN 50000 AND 70000;
    """
]
# Combine the original and additional commands
sql_commands.update(additional_commands)

def get_gemini_response(question, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content([prompt[0], question])
    return response.text

def execute_sql_query(sql, db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    try:
        cur.execute(sql)
        rows = cur.fetchall()
        conn.commit()
        return rows
    except sqlite3.Error as e:
        return f"Error executing SQL query: {e}"
    finally:
        conn.close()

def download_link(df, filename="data.csv", text="Download CSV"):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

# Streamlit app
st.set_page_config(page_title=" I can Retrieve Any SQL query", layout="wide")

# Sidebar for input and predefined SQL commands
st.sidebar.title("Features")

# Ask question input
question = st.sidebar.text_input("Your Question:", key="input")
ask_question_button = st.sidebar.button("Ask SQL.AI")

# Dropdown menu for predefined SQL commands
selected_command = st.sidebar.selectbox("Select a predefined SQL command:", list(sql_commands.keys()))

# Button to execute the selected command
execute_command_button = st.sidebar.button("Execute Command")

# Widgets for custom search
st.sidebar.header("Custom Search Options")
selected_columns = st.sidebar.multiselect("Select Columns for Visualization:", ["SALARY", "AGE", "WORKING_HOURS", "BONUS"])
date_range = st.sidebar.date_input("Select Date Range:", [pd.to_datetime("2022-01-01"), pd.to_datetime("2022-12-31")])

st.sidebar.header("Download CSV")
def download_link(df, filename="data.csv", text="Download CSV"):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

# Main content area for data plot
st.title("SQL.AI- Retrieve SQL Data")

if ask_question_button:
    response = get_gemini_response(question, prompt)
    st.subheader("SQL.AI's Response:")
    st.info(response)

    if "Error executing SQL query" in response:
        st.error(response)
    else:
        try:
            data = execute_sql_query(response, "company.db")

            if "Error executing SQL query" in data:
                st.error(data)
            else:
                # Display the retrieved data in a table
                st.subheader("All Data:")
                st.table(data)

                # Additional plotting based on data
                if data:
                    columns = ["ID", "NAME", "SALARY", "AGE", "GENDER", "DESIGNATION", "WORKING_HOURS", "MONTHLY_LUNCH_BILL", "BONUS"]
                    df = pd.DataFrame(data, columns=columns)

                    # Print the DataFrame
                    st.write("DataFrame:", df)

                    # Convert numeric columns to appropriate types
                    numeric_columns = ["SALARY", "AGE", "WORKING_HOURS", "MONTHLY_LUNCH_BILL", "BONUS"]
                    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')

                    # Plot based on available columns
                    for column in numeric_columns:
                        st.subheader(f"Visualization for {column}")
                        if len(df[column].unique()) <= 10:
                            # Bar chart for categorical or limited unique values
                            sns.barplot(x=df["NAME"], y=df[column], palette="viridis")
                            plt.xlabel("Employee Name")
                            plt.ylabel(column)
                            st.pyplot(plt)
                        else:
                            # Histogram for numerical data
                            sns.histplot(df[column], bins=20, kde=True, color="orange", edgecolor='black')
                            plt.xlabel(column)
                            plt.ylabel("Frequency")
                            st.pyplot(plt)

                    # Pie chart for gender distribution
                    st.subheader("Gender Distribution")
                    gender_counts = df["GENDER"].value_counts()
                    plt.pie(gender_counts, labels=gender_counts.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette("Set3"))
                    st.pyplot(plt)

                    # Download link for CSV
                    st.markdown(download_link(df), unsafe_allow_html=True)
                else:
                    st.warning("No data to plot.")
        except Exception as e:
            st.error(f"Error processing data: {e}")

elif execute_command_button:
    if selected_command in sql_commands:
        sql_query = sql_commands[selected_command]
        response = f"Executing predefined SQL command: {selected_command}"
    else:
        response = get_gemini_response(question, prompt)
        sql_query = extract_sql_query(response)

    st.subheader("Gemini's Response:")
    st.info(response)

    if "Error executing SQL query" in response:
        st.error(response)
    else:
        try:
            data = execute_sql_query(sql_query, "company.db")

            if "Error executing SQL query" in data:
                st.error(data)
            else:
                # Display the retrieved data in a table
                st.subheader("All Data:")
                st.table(data)

                # Additional plotting based on data
                if data:
                    columns = ["ID", "NAME", "SALARY", "AGE", "GENDER", "DESIGNATION", "WORKING_HOURS", "MONTHLY_LUNCH_BILL", "BONUS"]
                    df = pd.DataFrame(data, columns=columns)

                    # Print the DataFrame
                    st.write("DataFrame:", df)

                    # Convert numeric columns to appropriate types
                    numeric_columns = ["SALARY", "AGE", "WORKING_HOURS", "MONTHLY_LUNCH_BILL", "BONUS"]
                    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')

                    # Plot based on available columns
                    for column in numeric_columns:
                        st.subheader(f"Visualization for {column}")
                        if len(df[column].unique()) <= 10:
                            # Bar chart for categorical or limited unique values
                            sns.barplot(x=df["NAME"], y=df[column], palette="viridis")
                            plt.xlabel("Employee Name")
                            plt.ylabel(column)
                            st.pyplot(plt)
                        else:
                            # Histogram for numerical data
                            sns.histplot(df[column], bins=20, kde=True, color="orange", edgecolor='black')
                            plt.xlabel(column)
                            plt.ylabel("Frequency")
                            st.pyplot(plt)

                    # Pie chart for gender distribution
                    st.subheader("Gender Distribution")
                    gender_counts = df["GENDER"].value_counts()
                    plt.pie(gender_counts, labels=gender_counts.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette("Set3"))
                    st.pyplot(plt)

                    # Download link for CSV
                    st.markdown(download_link(df), unsafe_allow_html=True)
                else:
                    st.warning("No data to plot.")
        except Exception as e:
            st.error(f"Error processing data: {e}")

# Display a default message when no command is executed
st.info("Enter a question or select a predefined SQL command to execute.")

import sqlite3

# Connect to SQLite
connection = sqlite3.connect("company.db")
cursor = connection.cursor()

# Create the Employee table
employee_table_info = """
CREATE TABLE EMPLOYEE (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    NAME VARCHAR(50),
    SALARY REAL,
    AGE INT,
    GENDER VARCHAR(10),
    DESIGNATION VARCHAR(50),
    WORKING_HOURS INT,
    MONTHLY_LUNCH_BILL REAL,
    BONUS REAL
);
"""
cursor.execute(employee_table_info)

# Insert 10 sample employee records
employees_data = [
    ('John', 60000, 28, 'Male', 'Software Engineer', 40, 100, 5000),
    ('Alice', 75000, 35, 'Female', 'Project Manager', 45, 150, 8000),
    ('Bob', 55000, 30, 'Male', 'QA Engineer', 40, 80, 3000),
    ('Eva', 80000, 40, 'Female', 'Technical Lead', 50, 200, 10000),
    ('Mike', 70000, 32, 'Male', 'DevOps Engineer', 42, 120, 6000),
    ('Sara', 62000, 28, 'Female', 'UI/UX Designer', 38, 90, 4000),
    ('David', 72000, 34, 'Male', 'Database Administrator', 43, 110, 5500),
    ('Emily', 68000, 31, 'Female', 'Systems Analyst', 41, 100, 4500),
    ('Tom', 58000, 29, 'Male', 'Network Engineer', 39, 85, 3500),
    ('Sophia', 78000, 36, 'Female', 'Software Architect', 48, 180, 9000),
]

cursor.executemany('INSERT INTO EMPLOYEE VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)', employees_data)

# Display all the records
print("The inserted records are:")
data = cursor.execute('SELECT * FROM EMPLOYEE')
for row in data:
    print(row)

# Commit changes and close the connection
connection.commit()
connection.close()

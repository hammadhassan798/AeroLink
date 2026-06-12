import bcrypt 
from config import get_db
from sqlite3 import IntegrityError

# Fetch all employees with their airport names
def get_employees():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(""" SELECT e.employee_id, e.name, e.cnic, e.phone, e.role, e.experience_years, e.current_airport, e.username, a.name AS airport_name
        FROM employee e LEFT JOIN airport a ON e.current_airport = a.airport_code ORDER BY e.employee_id""")
    employees = cursor.fetchall()
    conn.close()
    return employees

# Add a new employee
def add_employee(name, role, cnic, phone, experience_years, current_airport, username, password, employee_id=None):
    conn = get_db()
    cursor = conn.cursor()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8') if password else None
    if employee_id:
        cursor.execute(""" INSERT INTO employee (employee_id, name, role, cnic, phone, experience_years, current_airport, username, password_hash)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (employee_id, name, role, cnic, phone, experience_years, current_airport, username, password_hash))
    else:
        cursor.execute("""
            INSERT INTO employee (name, role, cnic, phone, experience_years, current_airport, username, password_hash)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (name, role, cnic, phone, experience_years, current_airport, username, password_hash))
    conn.commit()
    conn.close()

# Get employee by ID
def get_employee(employee_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""SELECT e.employee_id, e.name, e.cnic, e.phone, e.role, e.experience_years,
        e.current_airport, e.username, a.name AS airport_name FROM employee e
        LEFT JOIN airport a ON e.current_airport = a.airport_code WHERE e.employee_id = %s
    """, (employee_id,))
    employee = cursor.fetchone()
    conn.close()
    return employee

# Edit an existing employee
def edit_employee(employee_id, name, role, cnic, phone, experience_years, current_airport, username, password=None):
    conn = get_db()
    cursor = conn.cursor()
    if password:
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute("""UPDATE employee SET name=%s, role=%s, cnic=%s, phone=%s, experience_years=%s, current_airport=%s, username=%s, password_hash=%s
            WHERE employee_id=%s """, (name, role, cnic, phone, experience_years, current_airport, username, password_hash, employee_id))
    else:
        cursor.execute("""UPDATE employee SET name=%s, role=%s, cnic=%s, phone=%s, experience_years=%s, current_airport=%s, username=%s
            WHERE employee_id=%s """, (name, role, cnic, phone, experience_years, current_airport, username, employee_id))
    conn.commit()
    conn.close()

# Delete an employee
def delete_employee(employee_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM employee WHERE employee_id = %s", (employee_id,))
    conn.commit()
    conn.close()

# Get employee by username
def get_employee_by_username(username):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM employee WHERE username = %s", (username,))
    employee = cursor.fetchone()
    conn.close()
    return employee

# Build a hash map of employees by name for quick searching
def build_employee_hash(employees):
    emp_hash = {}
    for emp in employees:
        key = emp['name'].lower()
        emp_hash[key] = emp
    return emp_hash

# Merge sort employees by experience years in descending order
def merge_sort_employees(employees):
    if len(employees) <= 1:
        return employees
    mid = len(employees) // 2
    left = merge_sort_employees(employees[:mid])
    right = merge_sort_employees(employees[mid:])
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i]['experience_years'] >= right[j]['experience_years']:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
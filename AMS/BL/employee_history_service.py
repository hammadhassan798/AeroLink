from DL.history_repo import *
from BL.employees_service import *

# Adding Employee operations with history recording
def add_employee_with_history(name, role, cnic, phone, experience_years, current_airport, username, password):
    add_employee(name, role, cnic, phone, experience_years, current_airport, username, password)
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM employee ORDER BY employee_id DESC LIMIT 1")
    new_employee = cursor.fetchone()
    conn.close()
    # Record the addition in history
    try:
        record_action(
            action_type="ADD",
            affected_table="employee",
            affected_id=new_employee['employee_id'],
            old_data=None,
            new_data=new_employee
        )
    except Exception as e:
        print(f"Failed to record action: {e}")

# Editing Employee operations with history recording
def edit_employee_with_history(employee_id, name, role, cnic, phone, experience_years, current_airport, username, password=None):
    old_emp = get_employee(employee_id)
    new_emp = old_emp.copy()
    new_emp.update({
        "name": name,
        "role": role,
        "cnic": cnic,
        "phone": phone,
        "experience_years": experience_years,
        "current_airport": current_airport,
        "username": username
    })
    edit_employee(employee_id, name, role, cnic, phone, experience_years, current_airport, username, password)
    # Record the edit in history
    record_action(
        action_type="EDIT",
        affected_table="employee",
        affected_id=str(employee_id),
        old_data=old_emp,
        new_data=new_emp
    )

# Deleting Employee operations with history recording
def delete_employee_with_history(employee_id):
    old_employee = get_employee(employee_id)
    delete_employee(employee_id)
    # Record the deletion in history
    try:
        record_action(
            action_type="DELETE",
            affected_table="employee",
            affected_id=employee_id,
            old_data=old_employee,
            new_data=None
        )
    except Exception as e:
        print(f"Failed to record action: {e}")
from config import get_db

# Find manager by CNIC
def find_manager_by_cnic(cnic):
    #get database connection
    db = get_db()
    #create cursor
    cursor = db.cursor(dictionary=True)
    #execute query
    cursor.execute("SELECT * FROM employee WHERE cnic=%s", (cnic,))
    #fetch employee data
    employee = cursor.fetchone()
    #close connections
    cursor.close()
    #close database connection
    db.close()
    #check if employee is a manager
    if employee and employee["role"] == "Manager":
        return employee
    return None
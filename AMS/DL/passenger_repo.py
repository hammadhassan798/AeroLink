from config import get_db

# Checking if a passenger with given CNIC exists
def find_passenger_by_cnic(cnic):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM passenger WHERE cnic = %s", (cnic,))
    result = cursor.fetchone()
    cursor.close()
    db.close()
    return result

# Creating a new passenger
def create_passenger(name, password_hash, cnic, phone):
    # Inserting a new passenger into the database
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO passenger (name, password_hash, cnic, phone) VALUES (%s,%s,%s,%s)",
            (name, password_hash, cnic, phone)
        )
        db.commit()
        cursor.close()
        db.close()
        return True
    # Catching any database insertion errors
    except Exception as e:
        print("DB Insert Error:", e)
        return False
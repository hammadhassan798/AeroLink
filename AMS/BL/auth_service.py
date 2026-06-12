from hashlib import sha256  # for password hashing
from DL.employee_repo import find_manager_by_cnic
from DL.passenger_repo import create_passenger, find_passenger_by_cnic

# Utility function to hash(encode) passwords
def hash_password(password):
    return sha256(password.encode()).hexdigest()

# Signup function for passengers
def signup_passenger_service(name, password, cnic, phone=None):
    # check if passenger with the same cnic already exists
    if find_passenger_by_cnic(cnic):
        return False, "CNIC already registered"
    # create new passenger
    password_hash = hash_password(password)
    try:
        create_passenger(name, password_hash, cnic, phone)
        return True, "Signup successful"
    except Exception as e:
        return False, f"Database error: {str(e)}"

# Login function for passengers
def login_passenger_service(cnic, password):
    # Authenticate passenger
    passenger = find_passenger_by_cnic(cnic)
    if not passenger:
        return False, "Passenger not found"
    if hash_password(password) != passenger["password_hash"]:
        return False, "Incorrect password"
    return True, passenger

# Login function for managers
def login_manager_service(cnic, password):
    # Authenticate manager
    manager = find_manager_by_cnic(cnic)
    if not manager:
        return False, "Manager not found or unauthorized"
    if hash_password(password) != manager["password_hash"]:
        return False, "Incorrect password"
    return True, manager
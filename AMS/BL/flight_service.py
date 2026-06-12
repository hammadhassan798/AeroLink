from config import get_db
from datetime import datetime

# Retrieve all flights with related aircraft and airport info
def get_flights():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT f.flight_no, a.model,f.airline, f.departure, f.arrival, f.price, f.status,
        a.model AS aircraft_model, ap.name AS current_airport FROM flight f JOIN aircraft a ON f.aircraft_id = a.aircraft_id
        JOIN airport ap ON a.current_airport = ap.airport_code ORDER BY f.departure """)
    flights = cursor.fetchall()
    conn.close()
    return flights

# Retrieve all aircrafts
def get_aircrafts():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT aircraft_id, model FROM aircraft")
    aircrafts = cursor.fetchall()
    conn.close()
    return aircrafts

# Retrieve flight legs for a specific flight
def get_flight_legs(flight_no):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT fl.leg_no, r.route_id, a1.name AS from_airport, a2.name AS to_airport, r.distance_km, r.time_minutes, r.cost
        FROM flight_leg fl JOIN route r ON fl.route_id = r.route_id JOIN airport a1 ON r.from_airport = a1.airport_code
        JOIN airport a2 ON r.to_airport = a2.airport_code WHERE fl.flight_no = %s ORDER BY fl.leg_no """, (flight_no,))
    legs = cursor.fetchall()
    conn.close()
    return legs

# Delete a flight leg
def delete_flight_leg(flight_no, leg_no):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM flight_leg WHERE flight_no=%s AND leg_no=%s ", (flight_no, leg_no))
    conn.commit()
    conn.close()

# Add a flight leg
def add_flight_leg(flight_no, leg_no, route_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(" INSERT INTO flight_leg (flight_no, leg_no, route_id) VALUES (%s, %s, %s) ", (flight_no, leg_no, route_id))
    conn.commit()
    conn.close()
    
# Retrieve employees assigned to a specific flight
def get_flight_employees(flight_no):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""SELECT fe.employee_id, e.name, fe.role FROM flight_employee fe JOIN employee e ON fe.employee_id = e.employee_id 
        WHERE fe.flight_no = %s ORDER BY fe.role, e.name """, (flight_no,))
    employees = cursor.fetchall()
    conn.close()
    return employees

# Add a flight with legs and employees in a transaction
def add_flight_with_details(flight_no, airline, aircraft_id, departure, arrival, price, status,legs, employees):
    conn = get_db()
    cursor = conn.cursor()
    try:
        conn.start_transaction()
        cursor.execute("""
            INSERT INTO flight (flight_no, airline, aircraft_id, departure, arrival, price, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (flight_no, airline, aircraft_id, departure, arrival, price, status))
        for leg_no, route_id in legs:
            cursor.execute("""
                INSERT INTO flight_leg (flight_no, leg_no, route_id)
                VALUES (%s, %s, %s)
            """, (flight_no, leg_no, route_id))
        for emp_id, role in employees:
            cursor.execute("""
                INSERT INTO flight_employee (flight_no, employee_id, role)
                VALUES (%s, %s, %s)
            """, (flight_no, emp_id, role))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# Update a flight with legs and employees in a transaction
def update_flight_with_details(flight_no, airline, aircraft_id, departure, arrival, price, status,legs, employees):
    conn = get_db()
    cursor = conn.cursor()
    try:
        conn.start_transaction()
        cursor.execute("""
            UPDATE flight
            SET airline=%s,
                aircraft_id=%s,
                departure=%s,
                arrival=%s,
                price=%s,
                status=%s
            WHERE flight_no=%s
        """, (airline, aircraft_id, departure, arrival, price, status, flight_no))
        cursor.execute("DELETE FROM flight_leg WHERE flight_no=%s", (flight_no,))
        cursor.execute("DELETE FROM flight_employee WHERE flight_no=%s", (flight_no,))
        for leg_no, route_id in legs:
            cursor.execute("""
                INSERT INTO flight_leg (flight_no, leg_no, route_id)
                VALUES (%s, %s, %s)
            """, (flight_no, leg_no, route_id))
        for emp_id, role in employees:
            cursor.execute("""
                INSERT INTO flight_employee (flight_no, employee_id, role)
                VALUES (%s, %s, %s)
            """, (flight_no, emp_id, role))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# Delete a flight along with its legs and employees in a transaction
def delete_flight_transactional(flight_no):
    conn = get_db()
    cursor = conn.cursor()
    try:
        conn.start_transaction()
        cursor.execute("DELETE FROM flight_leg WHERE flight_no=%s", (flight_no,))
        cursor.execute("DELETE FROM flight_employee WHERE flight_no=%s", (flight_no,))
        cursor.execute("DELETE FROM flight WHERE flight_no=%s", (flight_no,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
from config import get_db

# Getting dashboard statistics
def get_dashboard_stats():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) AS total_airports FROM airport")
    total_airports = cursor.fetchone()['total_airports']
    cursor.execute("SELECT COUNT(*) AS total_routes FROM route")
    total_routes = cursor.fetchone()['total_routes']
    cursor.execute("SELECT COUNT(*) AS total_flights FROM flight")
    total_flights = cursor.fetchone()['total_flights']
    cursor.execute("SELECT COUNT(*) AS total_employees FROM employee")
    total_employees = cursor.fetchone()['total_employees']
    conn.close()
    return total_airports, total_routes, total_flights, total_employees

def get_priority_flights():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT pf.*, f.flight_no
        FROM priority_flight pf
        JOIN flight f ON pf.flight_id = f.flight_id
        ORDER BY pf.priority_id
    """)
    priority_flights = cursor.fetchall()
    conn.close()
    return priority_flights

def add_priority_flight(flight_id, reason):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO priority_flight (flight_id, reason)
        VALUES (%s, %s)
    """, (flight_id, reason))
    conn.commit()
    conn.close()

def delete_priority_flight(priority_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM priority_flight WHERE priority_id=%s", (priority_id,))
    conn.commit()
    conn.close()
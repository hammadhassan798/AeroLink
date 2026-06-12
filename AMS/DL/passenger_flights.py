from config import get_db
from mysql.connector import Error
from DL.heap_loader import FlightMinHeap

# Retrieve available flights for booking
def get_available_flights():
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                f.flight_no,
                f.price,
                dep_airport.name AS departure,
                arr_airport.name AS arrival,
                f.departure AS departure_time,
                f.arrival AS arrival_time
            FROM flight f
            JOIN flight_leg fl1 ON fl1.flight_no = f.flight_no
            JOIN route r1 ON r1.route_id = fl1.route_id
            JOIN airport dep_airport ON dep_airport.airport_code = r1.from_airport
            JOIN flight_leg fl2 ON fl2.flight_no = f.flight_no
            JOIN route r2 ON r2.route_id = fl2.route_id
            JOIN airport arr_airport ON arr_airport.airport_code = r2.to_airport
            WHERE fl1.leg_no = (
                SELECT MIN(leg_no) FROM flight_leg WHERE flight_no = f.flight_no
            )
            AND fl2.leg_no = (
                SELECT MAX(leg_no) FROM flight_leg WHERE flight_no = f.flight_no
            )
            AND f.status = 'Scheduled'
        """)
        flights = cursor.fetchall()
        # APPLY MIN HEAP
        heap = FlightMinHeap()
        for f in flights:
            heap.push(f)
        return heap.get_all_sorted()
    except Exception as e:
        print("DB Error:", e)
        return []
    finally:
        conn.close()

# Retrieve flight legs for a specific flight (for passengers)
def get_flight_legs_for_passenger(flight_no):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT
            fl.leg_no,
            a1.name AS from_airport,
            a2.name AS to_airport,
            r.distance_km,
            r.time_minutes
        FROM flight_leg fl
        JOIN route r ON r.route_id = fl.route_id
        JOIN airport a1 ON a1.airport_code = r.from_airport
        JOIN airport a2 ON a2.airport_code = r.to_airport
        WHERE fl.flight_no = %s
        ORDER BY fl.leg_no
    """, (flight_no,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# Book a flight for a passenger
def book_flight(passenger_id, flight_no, seat_no, flight_type):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 1 FROM flight
            WHERE flight_no=%s AND status='Scheduled'
        """, (flight_no,))
        if not cursor.fetchone():
            return False, "Flight not available"
        cursor.execute("""
            SELECT 1 FROM booking
            WHERE flight_no=%s AND seat_no=%s
        """, (flight_no, seat_no))
        if cursor.fetchone():
            return False, "Seat already booked"
        cursor.execute("""
            INSERT INTO booking (passenger_id, flight_no, seat_no, flight_type)
            VALUES (%s, %s, %s, %s)
        """, (passenger_id, flight_no, seat_no, flight_type))
        conn.commit()
        return True, "✅ Flight booked successfully"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

# Get all bookings for a passenger
def get_passenger_bookings(passenger_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            b.ticket_id,
            b.flight_no,
            b.seat_no,
            b.flight_type,
            f.departure,
            f.arrival,
            f.departure,
            f.arrival
        FROM booking b
        JOIN flight f ON f.flight_no = b.flight_no
        WHERE b.passenger_id = %s
        ORDER BY f.departure
    """, (passenger_id,))
    data = cursor.fetchall()
    conn.close()
    return data

# Cancel a booking for a passenger
def cancel_booking(booking_id, passenger_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM booking
            WHERE booking_id=%s AND passenger_id=%s
        """, (booking_id, passenger_id))
        if cursor.rowcount == 0:
            return False, "Booking not found"
        conn.commit()
        return True, "Booking cancelled"
    except Error as e:
        return False, str(e)
    finally:
        conn.close()
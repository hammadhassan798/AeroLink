from config import get_db

def get_routes():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            r.route_id,
            a1.name AS from_airport,
            a2.name AS to_airport,
            r.distance_km,
            r.time_minutes,
            r.cost
        FROM route r
        JOIN airport a1 ON r.from_airport = a1.airport_code
        JOIN airport a2 ON r.to_airport = a2.airport_code
        ORDER BY a1.name, a2.name
    """)
    routes = cursor.fetchall()
    conn.close()
    return routes

def add_route(from_airport, to_airport, distance_km, time_minutes, cost):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO route (from_airport, to_airport, distance_km, time_minutes, cost)
            VALUES (%s, %s, %s, %s, %s)
        """, (from_airport, to_airport, distance_km, time_minutes, cost))
        conn.commit()
    finally:
        conn.close()

def edit_route(route_id, from_airport, to_airport, distance_km, time_minutes, cost):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE route
            SET from_airport=%s,
                to_airport=%s,
                distance_km=%s,
                time_minutes=%s,
                cost=%s
            WHERE route_id=%s
        """, (from_airport, to_airport, distance_km, time_minutes, cost, route_id))
        conn.commit()
    finally:
        conn.close()

def delete_route(route_id):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM route WHERE route_id=%s", (route_id,))
        conn.commit()
    finally:
        conn.close()
from config import get_db

# Retrieve all airports
def get_airports():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT airport_code,name,city,country FROM airport ORDER BY airport_code")
    airports = cursor.fetchall()
    conn.close()
    return airports

# Fetch airport by code
def get_airport_by_code(airport_code):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT airport_code, name, city, country FROM airport WHERE airport_code = %s", (airport_code,))
    airport = cursor.fetchone()
    conn.close()
    return airport

# Adding a new airport
def add_airport(airport_code, name, city, country):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO airport (airport_code, name, city, country)VALUES (%s, %s, %s, %s)",
        (airport_code, name, city, country))
    conn.commit()
    conn.close()

# Updating an existing airport
def update_airport(airport_code, name, city, country):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE airport SET name=%s, city=%s, country=%s WHERE airport_code=%s", (name, city, country, airport_code))
    conn.commit()
    conn.close()

# Deleting an airport
def delete_airport(airport_code):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM airport WHERE airport_code = %s", (airport_code,))
    conn.commit()
    conn.close()
    
# Linear search for airports by name
def linear_search_airports(airports, key):
    key = key.lower()
    result = []
    for airport in airports:
        if key in airport['name'].lower():
            result.append(airport)
    return result

# Build a hash map of airports by name for quick searching
def build_airport_hash(airports):
    airport_hash = {}
    for airport in airports:
        airport_hash[airport['name'].lower()] = airport
    return airport_hash
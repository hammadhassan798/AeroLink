import mysql.connector

def get_db():
    # Establish and return a database connection
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="tayyab1075",
        database="airline_db",
        #Automatically save changes to the database
        autocommit=True
    )

import mysql.connector

# Database Configuration
DATABASE_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "newuser",
    "password": "hitesh12",
    "db": "leaderboard",
    "autocommit": True,
}


DISTINCT_COUNTRIES_QUERY = "SELECT DISTINCT Country FROM leaderboard"

try:
    # Connect to the database
    connection = mysql.connector.connect(**DATABASE_CONFIG)

    # Create a cursor object to execute queries
    cursor = connection.cursor()

    # Execute the DISTINCT_COUNTRIES_QUERY
    cursor.execute(DISTINCT_COUNTRIES_QUERY)

    # Fetch all results
    results = cursor.fetchall()
    new_res = []
    # Print the distinct countries
    for result in results:
        new_res.append(result[0])

    print(new_res)
except mysql.connector.Error as err:
    print(f"Error: {err}")

finally:
    # Close the cursor and connection
    if 'cursor' in locals():
        cursor.close()
    if 'connection' in locals() and connection.is_connected():
        connection.close()

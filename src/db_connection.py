import mysql.connector

def main():
    db_config = {
        'host' : 'localhost',
        'user' : 'projectUser',
        'password' : '56789abc321.',
        'database' : 'project'
    }
    try:
        connection = mysql.connector.connect(**db_config)

        if connection.is_connected():
            print("Connected to the database successfully.")

            cursor = connection.cursor()
            cursor.execute("SHOW TABLES;")

            tables = cursor.fetchall()
            print("Tables in the database:")
            for table in tables:
                print(table[0])
                # Print the rows in the table.
                cursor.execute(f"SELECT * FROM {table[0]}")
                rows = cursor.fetchall()
                for row in rows:
                    print(row)
                
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed.")

if __name__ == "__main__":
    main()
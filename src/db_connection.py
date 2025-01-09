import mysql.connector

def get_connection(): #returns a connection object
    db_config = {
        'host' : 'localhost',
        'user' : 'projectUser',
        'password' : '56789abc321.',
        'database' : 'project'
    }
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

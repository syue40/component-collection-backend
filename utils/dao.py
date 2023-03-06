import psycopg2.extras as extras

def get_command_data(conn, command_string):
    """
    Loads dvd rental data from the database.
    """
    try:
        with conn.cursor() as cur:
            cur.execute(command_string)
            return cur.fetchall()
    except Exception as ex:
        print("Exception: ", ex)
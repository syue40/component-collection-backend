import psycopg2.extras as extras
from twilio.rest import Client

def get_command_data(conn, command_string):
    """
    Loads sales amount and units data from database
    """
    try:
        with conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
            cur.execute(command_string)
            record = cur.fetchall()
            return record
    except Exception as ex:
        print("Exception: ", ex)
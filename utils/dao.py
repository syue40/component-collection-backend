import psycopg2.extras as extras

def get_user(email: str, conn):
    """
    Finds a record from a user table in DB using the email and returns it in a list.
    """
    sql_command = """
    SELECT * FROM public.users WHERE email = %s ;
    """
    try:
        with conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
            cur.execute(sql_command, [email])
            record = cur.fetchone()
            return record
    except Exception as ex:
        print("Exception: ", ex)

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
        
def add_user(data_arr, conn):
    """
    Adds a user to users table in DB
    """
    sql_command = """
    INSERT INTO public.users(email, password) VALUES (%s, %s);
    """
    try:
        is_user = get_user(data_arr[0], conn)
        # Checks if the user already exists in DB.
        if is_user:
            return False
        else:
            with conn.cursor() as cur:
                cur.execute(sql_command, data_arr)
                conn.commit()
                # Checks if user was successfully added
                is_user = get_user(data_arr[0], conn)
                if is_user:
                    print("Successfully Inserted Record.")
                    return True
                else:
                    return False
    except Exception as ex:
        print("Exception: ", ex)
        
def update_user_details(first_name, last_name, biography, account_number, conn):
    sql_command = """
    UPDATE public.users SET first_name = %s, last_name = %s, biography=%s
    WHERE email = %s
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql_command, [
                        first_name, last_name, biography, account_number])
            conn.commit()
    except Exception as ex:
        print("Exception: ", ex)
        

def update_password(password, email, conn):
    sql_command = """
    UPDATE public.users SET password = %s WHERE email = %s;
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql_command, [password, email])
            conn.commit()
            # Checks if user was successfully added
            # is_user = get_user(email, conn)
            # if is_user:
            #     print("Successfully Updated Record.")
            #     return True
            # else:
            #     return False
    except Exception as ex:
        print("Exception: ", ex)
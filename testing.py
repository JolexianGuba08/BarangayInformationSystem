import psycopg2



def check_resident_exists(first_name, last_name, middle_name, gender):
    conn = psycopg2.connect(
        host="localhost",
        database="bis",
        user="postgres",
        password="posgre"
    )

    cursor = conn.cursor()
    query = "SELECT * FROM RESIDENT WHERE RES_FNAME = %s AND RES_LNAME = %s AND RES_MNAME = %s AND RES_GENDER = %s"
    values = (first_name, last_name, middle_name, gender)

    cursor.execute(query, values)
    resident_data = cursor.fetchone()

    return bool(resident_data)

if check_resident_exists("Jolexian","Guba","R","Male"):
    print("Exisist")
else:
    print("Not")
import mysql.connector as sql
from dotenv import load_dotenv
import os

load_dotenv()

gardensort_db = sql.connect (
    host="localhost",
    user="root", 
    passwd=os.getenv("MYSQL_PASSWD"),
    database="gardensort_db",
)

db_cursor = gardensort_db.cursor()

# db_cursor.execute("CREATE TABLE plant_type (type_reference INT NOT NULL AUTO_INCREMENT, identifier CHAR(3), name VARCHAR(50), biological_name VARCHAR(50)), primary key (type_reference)")
# db_cursor.execute("CREATE TABLE plant_kind (kind_reference INT NOT NULL AUTO_INCREMENT, type_reference INT, id CHAR(3), name VARCHAR(50), biological_name VARCHAR(50), PRIMARY KEY (kind_reference), FOREIGN KEY (type_reference) REFERENCES plant_type(type_reference))")
# db_cursor.execute("CREATE TABLE plant_version (version_reference INT NOT NULL AUTO_INCREMENT, kind_reference INT, id CHAR(3), name VARCHAR(50), purchase_date DATE, store_reference INT, reproduction VARCHAR(50), price DECIMAL(5,2), PRIMARY KEY (version_reference), FOREIGN KEY (kind_reference) REFERENCES plant_kind(kind_reference), FOREIGN KEY (store_reference) REFERENCES stores(store_reference))")
# db_cursor.execute('CREATE TABLE stores (store_reference INT NOT NULL AUTO_INCREMENT, store VARCHAR(50), PRIMARY KEY (store_reference))')


class Database_CURB:
    def __init__(self):
        self.gardensort_db = sql.connect (
        host="localhost",
        user="root", 
        passwd=os.getenv("MYSQL_PASSWD"),
        database="gardensort_db",
        )   

        self.db_cursor = self.gardensort_db.cursor()

    def write_to_database(self, table, data_list):
        if table == "plant_type":
            self.db_input_command = "INSERT INTO plant_type (identifier, name, biological_name) VALUES (%s, %s, %s)"
        elif table == "plant_kind":
            self.db_input_command = "INSERT INTO plant_kind (type_reference, id, name, biological_name) VALUES (%s, %s, %s, %s)"
        elif table == "plant_version":
            self.db_input_command = "INSERT INTO plant_version (kind_reference, id, name, purchase_date, store_reference, reproduction, price) VALUES (%s, %s, %s, %s, %s, %s, %s)"        
        elif table == "stores":
            self.db_input_command = "INSERT INTO stores (store, plz) VALUES (%s, %s)"
        else:
            return "Error while table selection"     
    
        print("table succesfully selected:" + self.db_input_command) 

        try:
            self.db_cursor.executemany(self.db_input_command, data_list)
            print("executed")
            self.gardensort_db.commit()
            print("commited")
        except:
            print("Error while writing data")
        finally:
            self.gardensort_db.close()
            print("data input succesfull")

# database_instance = Database_CURB()

# database_instance.write_to_database("plant_type", [("TOM", "Tomate", "Solanum lycopersicum")])


# def insert_data_if_not_exists(db_connection, table, data_list):
#     cursor = db_connection.cursor()

#     # SQL-Befehl, um Spaltennamen und Anzahl der Spalten für die Tabelle zu ermitteln
#     cursor.execute(f"DESCRIBE {table}")
#     table_columns = cursor.fetchall()
#     column_count = len(table_columns) - 1
#     column_names = [col[0] for col in table_columns]

#     # Überprüfung: Anzahl der Daten in `data_list` muss der Anzahl der Spalten entsprechen
#     for data in data_list:
#         if len(data) != column_count:
#             print(f"Error: Data entry {data} does not match the column count ({column_count}) for table '{table}'.")
#             return

#     # Einfüge-Statement basierend auf der Anzahl der Spalten vorbereiten
#     placeholders = ", ".join(["%s"] * column_count)
#     insert_query = f"INSERT INTO {table} ({', '.join(column_names)}) VALUES ({placeholders})"
#     print(insert_query)

#     # Überprüfen, ob Daten bereits in der Tabelle vorhanden sind, und wenn nicht, Daten einfügen
#     for data in data_list:
#         # Check-Query: Prüfen, ob Daten in der Tabelle bereits existieren
#         check_query = f"SELECT * FROM {table} WHERE " + " AND ".join(
#             [f"{column} = %s" for column in column_names]
#         )
#         cursor.execute(check_query, data)
        
#         if cursor.fetchone() is None:  # Daten sind nicht vorhanden
#             cursor.execute(insert_query, data)
#             print(f"Data {data} inserted into {table}.")
#         else:
#             print(f"Data {data} already exists in {table}.")

#     # Änderungen speichern und Cursor schließen
#     db_connection.commit()
#     cursor.close()
#     print("Operation completed successfully.")





def insert_data_if_not_exists(db_connection, table, data_list):
    cursor = db_connection.cursor()

    # Abrufen der Tabellenspalten und Filtern nach Nicht-PRI-Spalten
    cursor.execute(f"DESCRIBE {table}")
    table_columns = cursor.fetchall()
    
    # Filtern von Spalten ohne 'PRI'-Typ
    non_primary_columns = [col[0] for col in table_columns if col[3] != "PRI"]
    column_count = len(non_primary_columns)

    # Überprüfung: Anzahl der Daten in `data_list` muss der Anzahl der Spalten ohne 'PRI' entsprechen
    for data in data_list:
        if len(data) != column_count:
            print(f"Error: Data entry {data} does not match the column count ({column_count}) for table '{table}'.")
            return

    # Einfüge-Statement basierend auf den Nicht-PRI-Spalten vorbereiten
    placeholders = ", ".join(["%s"] * column_count)
    insert_query = f"INSERT INTO {table} ({', '.join(non_primary_columns)}) VALUES ({placeholders})"
    print("Insert Query:", insert_query)

    # Überprüfen, ob Daten bereits in der Tabelle vorhanden sind, und wenn nicht, Daten einfügen
    for data in data_list:
        # Check-Query nur für Nicht-PRI-Spalten
        check_query = f"SELECT COUNT(*) FROM {table} WHERE " + " AND ".join(
            [f"{column} = %s" for column in non_primary_columns]
        )

        # Debug-Ausgabe zur Überprüfung der Abfrage
        print("Check Query:", check_query, "with Data:", data)

        cursor.execute(check_query, data)
        exists = cursor.fetchone()[0]

        if exists == 0:  # Falls Datensatz nicht existiert
            cursor.execute(insert_query, data)
            print(f"Data {data} inserted into {table}.")
        else:
            print(f"Data {data} already exists in {table}.")

    # Änderungen speichern und Cursor schließen
    db_connection.commit()
    cursor.close()
    print("Operation completed successfully.")






data_list = [
    ("TOM", "Tomate", "Solanum lycopersicum"),
    ("CAR", "Karotte", "Daucus carota")
]

# Aufruf der Funktion mit Tabellenname und Daten
insert_data_if_not_exists(gardensort_db, "plant_type", data_list)





















def write_to_database():
    db_cursor = gardensort_db.cursor()
    
    # db_input_command = '''("INSERT INTO stores " "(store)" "VALUES (%s)")'''
    db_input_command = "INSERT INTO stores (store) VALUES (%s)"
    # stores = [("Edeka",), ("Bauhaus",), ("Obi",), ("Hornbach",), ("Wortmann",)]
    # stores = [["Edeka"], ["Bauhaus"], ["Obi"], ["Hornbach"], ["Wortmann"]]
    store = [("Hornbach")]

    db_cursor.execute(db_input_command, store)
    # db_cursor.execute(db_input_command, store)

    gardensort_db.commit()


def delelte_from_database():
    db_cursor = gardensort_db.cursor()

class Delete:
    def func_DeleteData():
        # Get the SQL connection
        connection = gardensort_db

        id = input('Enter Employee Id = ')
    
        try:
           # Get record which needs to be deleted
           sql = "Select * From stores Where store_reference = {0}" .format(id)
           cursor = connection.cursor()
           cursor.execute(sql)
           item = cursor.fetchone()
           print('Data Fetched for Id = ', id)
           confirm = input('Are you sure to delete this record (Y/N)?')

           # Delete after confirmation
           if confirm == 'Y':
               deleteQuery = "Delete From stores Where store_reference = {0}" .format(id)
               cursor.execute(deleteQuery)
               connection.commit()
               print('Data deleted successfully!')
           else:
                print('Wrong Entry')
        except:
            print('Something wrong, please check')
        finally:
            connection.close()

# colums = db_cursor.execute("SELECT count(*) AS NUMBEROFCOLUMNS FROM information_schema.columns WHERE table_name ='plant_version'")
# print(colums)

# gardensort_db.close()

# SELECT count(*) AS NUMBEROFCOLUMNS FROM information_schema.columns WHERE table_name ='plant_version'
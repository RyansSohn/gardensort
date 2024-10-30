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

        # Abrufen der Tabellenspalten und Filtern nach Nicht-PRI-Spalten
        self.db_cursor.execute(f"DESCRIBE {table}")
        table_columns = self.db_cursor.fetchall()
        
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
        print("Insert Query created succesfully")

        # Überprüfen, ob Daten bereits in der Tabelle vorhanden sind, und wenn nicht, Daten einfügen
        for data in data_list:
            # Check-Query nur für Nicht-PRI-Spalten
            check_query = f"SELECT COUNT(*) FROM {table} WHERE " + " AND ".join(
                [f"{column} = %s" for column in non_primary_columns]
            )

            # Debug-Ausgabe zur Überprüfung der Abfrage
            # print("Check Query:", check_query, "with Data:", data)

            self.db_cursor.execute(check_query, data)
            exists = self.db_cursor.fetchone()[0]

            print("Check Query succesful")

            if exists == 0:  # Falls Datensatz nicht existiert
                self.db_cursor.execute(insert_query, data)
                print(f"Data {data} inserted into {table}.")
            else:
                print(f"Data {data} already exists in {table}.")

        # Änderungen speichern und Cursor schließen
        self.gardensort_db.commit()
        self.db_cursor.close()
        print("Operation completed successfully.")


database_instance = Database_CURB()
database_instance.write_to_database("plant_type",  [("CAR", "Karotte", "Daucus carota")])




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
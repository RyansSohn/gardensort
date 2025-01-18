import mysql.connector as sql
from dotenv import load_dotenv
import os

load_dotenv()

# db_cursor.execute("CREATE TABLE plant_type (type_reference INT NOT NULL AUTO_INCREMENT, identifier CHAR(3), name VARCHAR(50), biological_name VARCHAR(50)), primary key (type_reference)")
# db_cursor.execute("CREATE TABLE plant_kind (kind_reference INT NOT NULL AUTO_INCREMENT, type_reference INT, id CHAR(3), name VARCHAR(50), biological_name VARCHAR(50), PRIMARY KEY (kind_reference), FOREIGN KEY (type_reference) REFERENCES plant_type(type_reference))")
# db_cursor.execute("CREATE TABLE plant_version (version_reference INT NOT NULL AUTO_INCREMENT, kind_reference INT, id CHAR(3), name VARCHAR(50), purchase_date DATE, store_reference INT, reproduction VARCHAR(50), price DECIMAL(5,2), PRIMARY KEY (version_reference), FOREIGN KEY (kind_reference) REFERENCES plant_kind(kind_reference), FOREIGN KEY (store_reference) REFERENCES stores(store_reference))")
# db_cursor.execute('CREATE TABLE stores (store_reference INT NOT NULL AUTO_INCREMENT, store VARCHAR(50), PRIMARY KEY (store_reference))')


class Database_CRUD:
    def __init__(self):
        pass

    def connect_to_database(self):
        self.gardensort_db = sql.connect (
        host="localhost",
        user="root", 
        passwd=os.getenv("MYSQL_PASSWD"),
        database="gardensort_db",
        )   

        self.db_cursor = self.gardensort_db.cursor()

    def write_to_database(self, table, data_list):

        self.connect_to_database()

        try:
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

                if exists == 0:  # Falls Datensatz nicht existiert
                    self.db_cursor.execute(insert_query, data)
                    print(f"Data {data} inserted into {table}.")
                else:
                    print(f"Data {data} already exists in {table}.")

                self.gardensort_db.commit()

        except sql.Error as e:
            print(f"The following error occurred while inserting: {e}")

        finally:
            self.db_cursor.close()
            self.gardensort_db.close()
            print("Connection closed after inserting")

    def delete_from_database(self, table, reference_number):

        self.connect_to_database()

        try:
            # Ermitteln des Namens der ersten Spalte
            self.db_cursor.execute(f"DESCRIBE {table}")
            columns = self.db_cursor.fetchall()
            first_column_name = columns[0][0]

            # Überprüfen, ob die Referenznummer existiert
            check_query = f"SELECT 1 FROM {table} WHERE {first_column_name} = %s"
            self.db_cursor.execute(check_query, (reference_number,))
            result = self.db_cursor.fetchone()

            if not result:
                print(f"Referenznummer {reference_number} existiert nicht in der Tabelle {table}.")
                return

            # Prüfen, ob die Referenznummer in anderen Tabellen als Fremdschlüssel verwendet wird
            self.db_cursor.execute(f"""
                SELECT TABLE_NAME, COLUMN_NAME
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE REFERENCED_TABLE_NAME = %s
                AND REFERENCED_COLUMN_NAME = %s
            """, (table, first_column_name))
            foreign_key_entries = self.db_cursor.fetchall()

            for fk_table, fk_column in foreign_key_entries:
                fk_check_query = f"SELECT 1 FROM {fk_table} WHERE {fk_column} = %s"
                self.db_cursor.execute(fk_check_query, (reference_number,))
                if self.db_cursor.fetchone():
                    print(f"Die Referenznummer {reference_number} wird in der Tabelle {fk_table} in der Spalte {fk_column} verwendet.")
                    return

            # Wenn die Referenznummer nicht als Fremdschlüssel verwendet wird, löschen
            delete_query = f"DELETE FROM {table} WHERE {first_column_name} = %s"
            self.db_cursor.execute(delete_query, (reference_number,))
            self.gardensort_db.commit()
            print(f"Zeile mit Referenznummer {reference_number} erfolgreich gelöscht.")
        except sql.Error as e:
            print(f"The following error occurred while deleting: {e}")
        finally:
            self.db_cursor.close()
            self.gardensort_db.close()
            print("Connection closed after deleting")




database_instance = Database_CRUD()
# database_instance.write_to_database("plant_kind",  [("5", "100", "Buschtomate","Lycopersicon esculentum L")])
# database_instance.write_to_database("plant_version",  [("1", "104", "Buschtomate","10.09.24", "2", "F1", "999")])
# database_instance.delete_from_database("plant_version", 7)





# colums = db_cursor.execute("SELECT count(*) AS NUMBEROFCOLUMNS FROM information_schema.columns WHERE table_name ='plant_version'")
# print(colums)

# gardensort_db.close()

# SELECT count(*) AS NUMBEROFCOLUMNS FROM information_schema.columns WHERE table_name ='plant_version'
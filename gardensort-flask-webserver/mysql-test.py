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

    def get_table_columns(self, table):

        try:
            self.connect_to_database()

            self.db_cursor.execute(f"DESCRIBE {table}")
            columns = self.db_cursor.fetchall()

            first_column_name = columns[0][0]
        
        finally:
            self.db_cursor.close()
            self.gardensort_db.close()
            print("Connection closed after reading columns")

        return columns, first_column_name

    def write_to_database(self, table, data_list):

        try:
            columns, first_column_name = self.get_table_columns(table)

            self.connect_to_database()            

            # Filtern von Spalten ohne 'PRI'-Typ
            non_primary_columns = [col[0] for col in columns if col[3] != "PRI"]
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

        try:
            columns, first_column_name = self.get_table_columns(table)

            self.connect_to_database()

            # Check if reference number is existent
            self.db_cursor.execute(f"SELECT 1 FROM {table} WHERE {first_column_name} = %s", (reference_number,))
            if not self.db_cursor.fetchone():
                print(f"refrence number {reference_number} doesn't exist in {table}.")
                return None

            # Prüfen, ob die Referenznummer in anderen Tabellen als Fremdschlüssel verwendet wird
            self.db_cursor.execute(f"""
                SELECT TABLE_NAME, COLUMN_NAME
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE REFERENCED_TABLE_NAME = %s
                AND REFERENCED_COLUMN_NAME = %s
            """, (table, first_column_name))
            foreign_key_entries = self.db_cursor.fetchall()

            for fk_table, fk_column in foreign_key_entries:
                self.db_cursor.execute(f"SELECT 1 FROM {fk_table} WHERE {fk_column} = %s", (reference_number,))
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

    def read_reference_by_term(self, table, column, term):

        try:
            columns, first_column_name = self.get_table_columns(table)

            self.connect_to_database()

            # Prüfen, ob die angegebene Spalte existiert
            if column not in [col[0] for col in columns]:
                print(f"Spalte '{column}' existiert nicht in der Tabelle '{table}'.")
                return None

            # Query: Erste Zeile mit dem Begriff in der angegebenen Spalte abrufen
            query = f"SELECT {first_column_name}, {column} FROM {table} WHERE {column} = %s LIMIT 1"
            self.db_cursor.execute(query, (term,))
            result = self.db_cursor.fetchone()

            if result:
                reference_number, column_value = result
                print(f"Referenznummer: {reference_number}, {column}: {column_value}")
                return reference_number, column_value
            else:
                print(f"Kein Eintrag mit dem Begriff '{term}' in Spalte '{column}' gefunden.")
                return None
        except sql.Error as e:
            print(f"Ein Fehler ist aufgetreten: {e}")
            return None
        finally:
            self.db_cursor.close()
            self.gardensort_db.close()
            print("Connection closed after reading refrence number")

    def read_term_by_refrence(self, table, column, reference_number):

        try:
            columns, first_column_name = self.get_table_columns(table)

            self.connect_to_database()

            # Prüfen, ob die angegebene Spalte existiert
            if column not in [col[0] for col in columns]:
                print(f"Spalte '{column}' existiert nicht in der Tabelle '{table}'.")
                return None

            # Check if reference number is existent
            self.db_cursor.execute(f"SELECT 1 FROM {table} WHERE {first_column_name} = %s", (reference_number,))
            if not self.db_cursor.fetchone():
                print(f"refrence number {reference_number} doesn't exist in {table}.")
                return None

            # Wert aus der angegebenen Spalte basierend auf der Referenznummer abfragen
            query = f"SELECT {column} FROM {table} WHERE {first_column_name} = %s"
            self.db_cursor.execute(query, (reference_number,))
            result = self.db_cursor.fetchone()

            if result:
                print(f"Wert aus Spalte '{column}' für Referenznummer {reference_number}: {result[0]}")
                return result[0]
            else:
                print(f"Keine Daten für Referenznummer {reference_number} in der Tabelle {table} gefunden.")
                return None
        except sql.Error as e:
            print(f"Ein Fehler ist aufgetreten: {e}")
            return None
        finally:
            self.db_cursor.close()
            self.gardensort_db.close()
            print("Connection closed after reading term")

    def update_value_by_reference(self, table, column, reference_number, new_value):

        try:
            columns, first_column_name = self.get_table_columns(table)

            self.connect_to_database()

            # Prüfen, ob die angegebene Spalte existiert
            column_names = [col[0] for col in columns]
            if column not in column_names:
                print(f"Spalte '{column}' existiert nicht in der Tabelle '{table}'.")
                return None

            # Überprüfen, ob die Referenznummer existiert
            self.db_cursor.execute(f"SELECT 1 FROM {table} WHERE {first_column_name} = %s", (reference_number,))
            if not self.db_cursor.fetchone():
                print(f"Referenznummer {reference_number} existiert nicht in der Tabelle {table}.")
                return None

            # Wert in der angegebenen Spalte für die Referenznummer aktualisieren
            self.db_cursor.execute(f"UPDATE {table} SET {column} = %s WHERE {first_column_name} = %s", (new_value, reference_number))
            self.gardensort_db.commit()

            print(f"Spalte '{column}' für Referenznummer {reference_number} wurde auf '{new_value}' aktualisiert.")
        except sql.Error as e:
            print(f"Ein Fehler ist aufgetreten: {e}")
        finally:
            self.db_cursor.close()
            self.gardensort_db.close()
            print("Connection closed after updating value")

    def update_row_by_reference(self, table, reference_number, update_data):

        try:
            columns, first_column_name = self.get_table_columns(table)

            self.connect_to_database()

            # Überprüfen, ob die Referenznummer existiert
            self.db_cursor.execute(f"SELECT 1 FROM {table} WHERE {first_column_name} = %s", (reference_number,))
            if not self.db_cursor.fetchone():
                print(f"Referenznummer {reference_number} existiert nicht in der Tabelle {table}.")
                return None

            # Alle Spalten, die nicht der Primärschlüssel sind, extrahieren
            non_primary_columns = [col[0] for col in columns if col[3] != "PRI"]
            
            # Anzahl der zu aktualisierenden Spalten überprüfen
            if len(update_data) != len(non_primary_columns):
                print(f"Error: Data entry {update_data} with {len(update_data)} columns does not match the column count {len(non_primary_columns)} for table '{table}'.")
                return None
            
            # Erstellen der SET-Klausel für die UPDATE-Abfrage
            set_clause = ", ".join([f"{non_primary_columns[i]} = %s" for i in range(len(non_primary_columns))])

            # Ausführen der UPDATE-Abfrage
            update_query = f"UPDATE {table} SET {set_clause} WHERE {first_column_name} = %s"
            self.db_cursor.execute(update_query, update_data + [reference_number])
            self.gardensort_db.commit()

            print(f"Die Zeile mit Referenznummer {reference_number} wurde erfolgreich aktualisiert.")

        except sql.Error as e:
            print(f"Ein Fehler ist aufgetreten: {e}")

        finally:
            self.db_cursor.close()
            self.gardensort_db.close()
            print("Connection closed after updating row")


database_instance = Database_CRUD()
# database_instance.write_to_database("plant_kind",  [("5", "100", "Buschtomate","Lycopersicon esculentum L")])
# database_instance.write_to_database("plant_version",  [("1", "104", "Buschtomate","10.09.24", "2", "F1", "999")])
# database_instance.delete_from_database("plant_version", 7)
# database_instance.read_reference_by_term("stores", "store", "Bauhaus")
# database_instance.read_term_by_refrence("stores", "store", "100")
# database_instance.update_value_by_reference("plant_version", "name", "4", "Buschtomate")
# database_instance.update_row_by_reference("plant_version",4, ["1", "104", "Buschtomate","10.09.25", "3", "F133w", "99"])







# colums = db_cursor.execute("SELECT count(*) AS NUMBEROFCOLUMNS FROM information_schema.columns WHERE table_name ='plant_version'")
# print(colums)

# gardensort_db.close()

# SELECT count(*) AS NUMBEROFCOLUMNS FROM information_schema.columns WHERE table_name ='plant_version'
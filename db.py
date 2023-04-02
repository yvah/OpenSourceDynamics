import ibm_db
import json


def load_json(filename):
    with open(filename) as json_file:
        return json.load(json_file)


class DB2:
    def __init__(self, credentials_file):
        self.credentials = load_json(credentials_file)
        self.schema = self.credentials["username"].upper() + "."

        print("connecting")
        # establish connection to db2
        self.connection = ibm_db.pconnect(f"DATABASE={self.credentials['database']};"
                                          f"HOSTNAME={self.credentials['hostname']};"
                                          f"PORT={self.credentials['port']};"
                                          f"SECURITY=SSL;"
                                          f"PROTOCOL=TCPIP;"
                                          f"UID={self.credentials['username']};"
                                          f"PWD={self.credentials['password']};", '', '')
        print("connection successful")

    # creates a table with with the passed in name, returns true on success or if table already exists
    def create(self, table):
        sql_instruction = f"CREATE TABLE {self.schema + table} (" \
                          "Number int NOT NULL, " \
                          "Title varchar(255) NOT NULL, " \
                          "Author varchar(255), " \
                          "Gender varchar(255) NOT NULL, " \
                          "State varchar(255) NOT NULL, " \
                          "Created varchar(255) NOT NULL, " \
                          "Closed varchar(255) NOT NULL, " \
                          "Lifetime float NOT NULL, " \
                          "Comments int NOT NULL, " \
                          "Sentiment float NOT NULL, " \
                          "Sadness float NOT NULL, " \
                          "Joy float NOT NULL, " \
                          "Fear float NOT NULL, " \
                          "Disgust float NOT NULL, " \
                          "Anger float NOT NULL, " \
                          "PRIMARY KEY (Number));"

        try:
            ibm_db.exec_immediate(self.connection, sql_instruction)
            return True
        except Exception:
            return False

    # clears the table with the selected name, returns true on success
    def clear(self, table):
        sql_instruction = f"DELETE FROM {self.schema + table};"
        try:
            ibm_db.exec_immediate(self.connection, sql_instruction)
            return True
        except Exception:
            print("error clearing table")
            return False

    # adds the data to a table, creating the table if it doesn't already exist
    # returns true if successful, otherwise prints number of successful inserts and returns false
    def add_data(self, table, data):
        # creates table if it doesn't already exist
        self.create(table)
        insert_command = f"INSERT INTO {self.schema + table} VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
        insert_command = ibm_db.prepare(self.connection, insert_command)

        # adds this data to the table
        params = []
        if data is not None:
            for d in data:
                params.append((d.number, d.title, d.author, d.gender, d.state, d.createdAt, d.closedAt, d.lifetime,
                               d.number_of_comments, d.sentiment, d.emotion[0][1], d.emotion[1][1], d.emotion[2][1],
                               d.emotion[3][1], d.emotion[4][1]))

        success = ibm_db.execute_many(insert_command, tuple(params))
        if success is not False:
            return True
        row_count = ibm_db.num_rows(insert_command)
        print(f"inserted {row_count} rows")
        return False

    # copies the data from one table into another
    def copy_into(self, to_table, from_table):
        success = self.clear(to_table)
        if success:
            sql_instruction = f"INSERT INTO {self.schema + to_table} SELECT * FROM {self.schema + from_table};"
            success = ibm_db.exec_immediate(self.connection, sql_instruction)
            if success is not False:
                return True
        return False

    # close the connection
    def close(self):
        ibm_db.close(self.connection)

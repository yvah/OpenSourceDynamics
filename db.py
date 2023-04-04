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
                          "Title varchar(255), " \
                          "Author varchar(128), " \
                          "Gender varchar(7), " \
                          "State varchar(6), " \
                          "Created varchar(20), " \
                          "Closed varchar(20), " \
                          "Lifetime float, " \
                          "Comments int, " \
                          "Sentiment float, " \
                          "Sadness float, " \
                          "Joy float, " \
                          "Fear float, " \
                          "Disgust float, " \
                          "Anger float, " \
                          "Concept1 varchar(128)," \
                          "Concept2 varchar(128)," \
                          "Concept3 varchar(128)," \
                          "PRIMARY KEY (Number));"

        try:
            ibm_db.exec_immediate(self.connection, sql_instruction)
            return True
        except:
            return False

    # clears the table with the selected name, returns true on success
    def clear(self, table):
        sql_instruction = f"DELETE FROM {self.schema + table};"
        try:
            ibm_db.exec_immediate(self.connection, sql_instruction)
            return True
        except:
            print("error clearing table")
            return False

    # inserts the data into a table, creating the table if it doesn't already exist
    # returns true if successful, otherwise prints number of successful inserts and returns false
    def insert_data(self, table, data):
        # creates table if it doesn't already exist
        self.create(table)
        if data is None:
            return

        insert_command = f"INSERT INTO {self.schema + table} VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
        insert_command = ibm_db.prepare(self.connection, insert_command)

        # adds this data to the table
        params = []
        for d in data:
            # ensure title is less than max length and concepts has length at least 3
            title = (d.title[:252] + '...') if len(d.title) > 255 else d.title
            concepts = d.concepts
            while len(concepts) < 3:
                concepts.append(None)

            params.append((d.number, title, d.author, d.gender, d.state, d.createdAt, d.closedAt, d.lifetime,
                           d.number_of_comments, d.sentiment, d.emotion[0][1], d.emotion[1][1], d.emotion[2][1],
                           d.emotion[3][1], d.emotion[4][1], concepts[0], concepts[1], concepts[2]))

        ibm_db.execute_many(insert_command, tuple(params))

    # switch the data source to the passed in table
    def switch_view(self, view, table):
        sql_statement = f"CREATE OR REPLACE VIEW {self.schema + view} AS SELECT * FROM {self.schema + table};"
        ibm_db.exec_immediate(self.connection, sql_statement)

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


# function for testing connection
if __name__ == "__main__":
    conn = DB2("credentials/db2_credentials.json")
    conn.close()

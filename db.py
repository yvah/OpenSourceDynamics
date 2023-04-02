import ibm_db
import json


def load_json(filename):
    with open(filename) as json_file:
        return json.load(json_file)


# returns string containing question marks for sql statement
def get_question_marks(number):
    string = "?"
    for _ in range(number-1):
        string += ",?"


# function returns the parameters for the execute_many command
def populate_params(data, table_type):
    if data is None:
        return []

    # parameters vary based on type of table
    params = []
    if table_type == "source":
        for d in data:
            params.append((d.number, d.title, d.author, d.gender, d.state, d.createdAt, d.closedAt, d.lifetime,
                           d.number_of_comments, d.sentiment, d.emotion[0][1], d.emotion[1][1], d.emotion[2][1],
                           d.emotion[3][1], d.emotion[4][1]))
    elif table_type == "average":
        for d in data:
            params.append((d.sentiment, d.emotion[0][1], d.emotion[1][1], d.emotion[2][1], d.emotion[3][1],
                           d.emotion[4][1], d.lifetime))
    elif table_type == "state":
        for d in data:
            params.append((d.state, d.frequency, d.sentiment, d.emotion[0][1], d.emotion[1][1], d.emotion[2][1],
                           d.emotion[3][1], d.emotion[4][1], d.lifetime))
    elif table_type == "gender":
        for d in data:
            params.append((d.gender, d.frequency, d.sentiment, d.emotion[0][1], d.emotion[1][1], d.emotion[2][1],
                           d.emotion[3][1], d.emotion[4][1], d.lifetime))
    return tuple(params)


sql_dict = load_json("sql.json")
num_dict = {"source": 15, "average": 7, "state": 9, "gender": 9}


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
    def create(self, table, table_type):
        sql_instruction = f"CREATE TABLE {self.schema + table} (" + sql_dict[table_type]

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

    # creates all the different types of tables
    def create_all(self, table):
        self.create(table, "source")
        self.create(table + "_average", "average")
        self.create(table + "_state", "state")
        self.create(table + "_gender", "gender")

    # clears all the different types of tables
    def clear_all(self, table):
        if table != "sources":
            self.clear(table)
            self.clear(table + "_average")
            self.clear(table + "_state")
            self.clear(table + "_gender")
        else:
            self.clear("SOURCE")
            self.clear("AVERAGE")
            self.clear("STATE")
            self.clear("GENDER")

    # adds the data to a table, creating the table if it doesn't already exist
    # returns true if successful, otherwise prints number of successful inserts and returns false
    def add_data(self, table, data, table_type):
        # creates table if it doesn't already exist
        self.create(table, table_type)
        insert_command = f"INSERT INTO {self.schema + table} VALUES ({get_question_marks(num_dict[table_type])})"
        insert_command = ibm_db.prepare(self.connection, insert_command)

        # adds this data to the table
        params = populate_params(data, table_type)
        success = ibm_db.execute_many(insert_command, params)
        if success is not False:
            return True
        row_count = ibm_db.num_rows(insert_command)
        print(f"inserted {row_count} rows")
        return False

    # copies the data from one table into another
    def switch_sources(self, table):
        self.clear_all("sources")

        sql_statement = f"INSERT INTO ? SELECT * FROM ?;"
        sql_statement = ibm_db.prepare(self.connection, sql_statement)
        full_table_name = self.schema + table

        # populate parameters and run all
        params = ((f"{self.schema}SOURCE", full_table_name),
                  (f"{self.schema}AVERAGE", f"{full_table_name}_average"),
                  (f"{self.schema}STATE", f"{full_table_name}_state"),
                  (f"{self.schema}GENDER", f"{full_table_name}_gender"))
        ibm_db.execute_many(sql_statement, params)

    # close the connection
    def close(self):
        ibm_db.close(self.connection)

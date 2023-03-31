import ibm_db
from cloudant import load_json


class DB2:
    def __init__(self, credentials_file):
        self.credentials = load_json(credentials_file)

        self.connection = ibm_db.connect(f"DATABASE={self.credentials['database']};"
                                         f"HOSTNAME={self.credentials['hostname']};"
                                         f"PORT={self.credentials['port']};"
                                         f"PROTOCOL=TCPIP;"
                                         f"UID={self.credentials['username']};"
                                         f"PWD={self.credentials['password']}", '', '')

    # creates a database with with the passed in name, returns true on success or if database already exists
    def create(self, database):
        success = ibm_db.createdbNX(self.connection, database)
        if success is None:
            return False
        return True

    # clears the database with the selected name, returns true on success
    def clear(self, database):
        sql_instruction = f"DELETE * FROM {database};"
        success = ibm_db.exec_immediate(self.connection, sql_instruction)
        if success is False:
            return False
        return True

    # adds the data to a database, creating the database if it doesn't already exist
    # returns true if successful, otherwise prints number of successful inserts and returns false
    def add_data(self, database, data):
        # creates database if it doesn't already exist
        success = self.create(database)
        if success:
            insert_command = f"INSERT INTO {database} VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
            insert_command = ibm_db.prepare(self.connection, insert_command)

            params = []
            for d in data:
                params.append((d.number, d.title, d.author, d.gender, d.state, d.createdAt, d.closedAt,
                               d.sentiment, d.emotion[0][1], d.emotion[1][1], d.emotion[2][1], d.emotion[3][1],
                               d.emotion[4][1]))

            success = ibm_db.execute_many(insert_command, tuple(params))
            if success is not False:
                return True
            row_count = ibm_db.num_rows(insert_command)
            print(f"inserted {row_count} rows")
            return False

    # copies the data from one table into another
    def copy_into(self, to_database, from_database):
        success = self.clear(to_database)
        if success:
            sql_instruction = f"INSERT INTO {to_database} SELECT * FROM {from_database};"
            success = ibm_db.exec_immediate(self.connection, sql_instruction)
            if success is not False:
                return True
        return False

import ibm_db
from cloudant import load_json


class DB2:
    def __init__(self, credentials_file):
        self.credentials = load_json(credentials_file)

        print("connecting...")
        self.connection = ibm_db.connect(f"DATABASE={self.credentials['database']};"
                                         f"HOSTNAME={self.credentials['hostname']};"
                                         f"PORT={self.credentials['port']};"
                                         f"SECURITY=SSL;"
                                         f"SSLServerCertificate={self.credentials['cert_file']}"
                                         f"PROTOCOL=TCPIP;"
                                         f"UID={self.credentials['username']};"
                                         f"PWD={self.credentials['password']};", '', '')
        print("success")

    # creates a table with with the passed in name, returns true on success or if table already exists
    def create(self, table):
        success = ibm_db.createdbNX(self.connection, table)
        if success is None:
            return False
        return True

    # clears the table with the selected name, returns true on success
    def clear(self, table):
        sql_instruction = f"DELETE * FROM {table};"
        success = ibm_db.exec_immediate(self.connection, sql_instruction)
        if success is False:
            return False
        return True

    # adds the data to a table, creating the table if it doesn't already exist
    # returns true if successful, otherwise prints number of successful inserts and returns false
    def add_data(self, table, data):
        # creates table if it doesn't already exist
        success = self.create(table)
        if success:
            insert_command = f"INSERT INTO {table} VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
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
    def copy_into(self, to_table, from_table):
        success = self.clear(to_table)
        if success:
            sql_instruction = f"INSERT INTO {to_table} SELECT * FROM {from_table};"
            success = ibm_db.exec_immediate(self.connection, sql_instruction)
            if success is not False:
                return True
        return False

from src.database.DatabaseConnection import DatabaseConnection
import os
import sqlite3
import pickle

class DatabaseTable:
    def __init__(self, db_name: str, table_name: str, db_path: str, table_columns: dict):

        self.db_name = db_name
        self.db_path = db_path
        self.table_name = table_name
        self.table_columns = table_columns
        self.num_entries = 0

        os.makedirs(self.db_path, exist_ok=True)

    def insert(self, data, condition=None):

        if not isinstance(data, list):
            data = [[data]]
        elif len(data) > 0 and not isinstance(data[0], list):
            data = [data]

        with self.connect() as conn:
            mask = '?,' * (len(self.table_columns) - 1) + '?'
            query = f'INSERT INTO "{self.table_name}" {self.get_table_columns_as_tuple(self.table_columns)} VALUES ({mask})'
            if condition:
                query += f" WHERE {condition}"

            return conn.execute_multi_query(query, data)

    def select(self, table_columns="*", condition=None):
        with self.connect() as conn:
            query = f"SELECT {table_columns} FROM {self.table_name}"
            if condition:
                query += f" WHERE {condition}"
            return conn.execute_query(query)

    def update(self, data, condition=None):
        with self.connect() as conn:
            set_values = ", ".join([f"{key} = ?" for key in data.keys()])
            query = f"UPDATE {self.table_name} SET {set_values}"
            if condition:
                query += f" WHERE {condition}"

            return conn.execute_query(query, tuple(data.values()))

    def delete(self, condition):
        with self.connect() as conn:
            query = f"DELETE FROM {self.table_name} WHERE {condition}"
            return conn.execute_query(query)

    def value_in_table(self, column, value):
        with self.connect() as conn:
            query = f"SELECT 1 FROM {self.table_name} WHERE {column} = '{value}' LIMIT 1;"
            result = conn.execute_query(query)
            return bool(result)

    def insert_data_list(self, data):
        with self.connect() as conn:
            mask = '?,' * (len(self.table_columns) - 1) + '?'
            query = f'INSERT INTO "{self.table_name}" {self.get_table_columns_as_tuple(self.table_columns)} VALUES ({mask})'
            return conn.execute_multi_query(query, data)

    def insert_binary_data(self, table_name, table_columns, data):
        with self.connect() as conn:
            columns = self.get_table_columns_as_tuple(table_columns)
            mask = '?,' * (len(columns) - 1) + '?'

            query = f'INSERT INTO "{table_name}" {columns} VALUES ({mask})'
            binary = []
            no_binary = []

            for value in data.values():
                if isinstance(value, bytes):
                    binary.append(value)
                else:
                    no_binary.append(value)

            #self.cursor.execute(query, (*[sqlite3.Binary(value,) for value in binary], *no_binary))
            conn.cursor.execute(query, (*[DatabaseTable.convert_binary_data(value) for value in binary], *no_binary))
            conn.conn.commit()

    def create_table(self, table_name, columns, clear_table=True):
        with self.connect() as conn:
            column_definitions = ", ".join([f"{name} {data_type}" for name, data_type in columns.items()])
            query = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({column_definitions});'
            conn.execute_query(query)

            if clear_table:
                self.clear_table(table_name)

    def clear_table(self, table_name):
        with self.connect() as conn:
            if self.table_exists(table_name):
                conn.execute_query(f'DELETE FROM "{table_name}";')

                if self.table_exists('SQLITE_SEQUENCE'):
                    conn.execute_query(f'DELETE FROM SQLITE_SEQUENCE WHERE name="{table_name}";')

    def delete_table(self, table_name):
        with self.connect() as conn:
            if self.table_exists(table_name):
                conn.execute_query(f'DROP TABLE IF EXISTS "{table_name}";')

    def get_table_length(self):
        with self.connect() as conn:
            query = f'SELECT max(rowid) FROM {self.table_name}'
            return conn.execute_query(query)[0][0]

    def create_index(self, table_name, column):
        with self.connect() as conn:
            query = f"CREATE INDEX IF NOT EXISTS {column}_idx ON {table_name}({column});"
            conn.execute_query(query)

    def table_exists(self, table_name):
        with self.connect() as conn:

            db_table_exists = conn.execute_query(
                f'SELECT * FROM sqlite_master WHERE type="table" and name="{table_name}";')
            if len(db_table_exists) > 0:
                return True
            return False

    def connect(self) -> DatabaseConnection:
        return DatabaseConnection(self.db_path + 'sqlite.db')

    @staticmethod
    def convert_binary_data(data):
        return sqlite3.Binary(pickle.dumps(data))

    @staticmethod
    def get_table_columns_as_tuple(table_columns: dict) -> tuple:

        if len(table_columns) == 1:
            key, = table_columns.keys()
            columns = '(\'' + key + '\')'
        else:
            columns = tuple([i for i in table_columns.keys() if i != 'id'])

        return columns
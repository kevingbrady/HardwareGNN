import sqlite3


class DatabaseConnection:
    def __init__(self, db_full_path):
        self.db_full_path = db_full_path
        self.conn = None
        self.cursor = None
        self.connect()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.conn.rollback()
        else:
            self.conn.commit()

        self.disconnect()

    def connect(self) -> None:
        try:
            self.conn = sqlite3.connect(self.db_full_path)
            self.conn.execute('PRAGMA journal_mode=WAL')
            self.cursor = self.conn.cursor()

        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")

    def disconnect(self) -> None:
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def execute_query(self, query, params=()):
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")
            print(query, end='\n\n')
            return None

    def execute_multi_query(self, query, data_list, params=()):
        try:
            self.execute_query("BEGIN IMMEDIATE")  # ACQUIRE DB LOCK
            self.cursor.executemany(query, data_list)
            self.conn.commit()
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            if str(e).__contains__('BEGIN IMMEDIATE'):
                pass
            else:
                print(f"Error executing query: {e}")
                return None

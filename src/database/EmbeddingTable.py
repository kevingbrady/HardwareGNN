from src.database.DatabaseTable import DatabaseTable


class EmbeddingTable(DatabaseTable):

    table_columns = {'name': 'TEXT'}

    def __init__(self, db_name: str, table_name: str, db_path: str, clear_table: bool=True):
        super().__init__(db_name, table_name, db_path, self.table_columns)

        self.create_table(self.table_name, self.table_columns, clear_table=clear_table)
        self.create_index(self.table_name, 'name')

    def enter_value(self, value):
        if not self.value_in_table('name', value):
            self.insert(value)

    def get_rowid(self, value):
        with self.connect() as conn:
            query = f"SELECT rowid FROM {self.table_name} WHERE name = '{value}';"
            results = conn.execute_query(query)
            return results[0][0]

    def get_rowids_for_values(self, values: list) -> list:

        if not values:  return []

        with self.connect() as conn:
            mask = ', '.join(['?'] * len(values))
            query = f'SELECT rowid FROM {self.table_name} WHERE name in ({mask});'
            results = conn.execute_query(query, tuple(values))

            return [row[0] for row in results]

    def remove_duplicates(self):
        with self.connect() as conn:
            query = f'DELETE FROM {self.table_name} WHERE rowid NOT IN (SELECT MIN(rowid) FROM {self.table_name} GROUP BY name);'
            conn.execute_query(query)






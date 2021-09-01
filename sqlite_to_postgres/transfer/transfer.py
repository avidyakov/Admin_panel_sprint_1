DELIMITER = '|'


class SQLitePostgresTransfer:

    def __init__(self, sqlite_conn, pg_conn):
        self.sqlite_conn = sqlite_conn
        self.pg_conn = pg_conn

    def load_data(self, model) -> set:
        result = set()
        for table_name in model.Meta.tables_to_import:
            selected = self.sqlite_conn.execute(f'SELECT * FROM {table_name}').fetchall()
            result.update(model.load_data(table_name, selected))
        return result

    def process_data(self, models):
        for model in models:
            model.process_all(self)

    def save_data(self, model, models_set):
        cursor = self.pg_conn.cursor()
        data, columns = model.export_csv(models_set)
        data.seek(0)
        cursor.copy_from(data, model.Meta.table_to_export, sep=DELIMITER, columns=columns)

    def transfer(self):
        for model in self.models:
            loaded_data = self.load_data(model)
            self.process_data(loaded_data)
            self.save_data(model, loaded_data)

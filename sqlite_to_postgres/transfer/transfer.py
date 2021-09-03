DELIMITER = '|'


class SQLitePostgresTransfer:

    def __init__(self, sqlite_conn, pg_conn):
        self.sqlite_conn = sqlite_conn
        self.pg_conn = pg_conn

    def load_data(self, model) -> set:
        result = set()
        for table_name in model.Meta.tables_to_import:
            cursor = self.sqlite_conn.cursor()
            for row in cursor.execute(f'SELECT * FROM {table_name}'):
                # Костыль 📛
                if table_name == 'actors':
                    model_instance = model(raw_actor_id=row[0], name=row[1])
                elif table_name == 'writers':
                    model_instance = model(raw_writer_id=row[0], name=row[1])
                else:
                    model_instance = model(*row)
                model_instance.process_all(self)
                result.add(model_instance)
            cursor.close()
        return result

    def save_data(self, model, models_set) -> None:
        with self.pg_conn.cursor() as cursor:
            data, columns = model.export_csv(models_set)
            data.seek(0)
            cursor.copy_from(data, model.Meta.table_to_export, sep=DELIMITER, columns=columns)

    def transfer(self) -> None:
        for model in self.models:
            loaded_data = self.load_data(model)
            self.save_data(model, loaded_data)

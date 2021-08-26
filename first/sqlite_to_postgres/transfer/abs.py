import csv
import io
from dataclasses import is_dataclass, fields, asdict

DELIMITER = '|'


class AbstractDataclass:

    def process_all(self, transfer):
        for raw_field in self._get_raw_fields():
            try:
                self.__getattribute__(f'process_{raw_field}')(transfer)
            except AttributeError:
                continue

    @classmethod
    def _get_raw_fields(cls):
        return [f.name for f in fields(cls) if f.name.startswith('raw_')]

    @classmethod
    def _get_columns(cls):
        return [f.name for f in fields(cls) if not f.name.startswith('raw_')]

    @classmethod
    def export_csv(cls, values):
        file = io.StringIO()
        columns = cls._get_columns()
        writer = csv.DictWriter(file, columns, delimiter=DELIMITER)
        for value in values:
            filtered_dict = {key: value for key, value in asdict(value).items() if not key.startswith('raw_')}
            writer.writerow(filtered_dict)

        return file, columns

    @classmethod
    def load_data(cls, table_name, rows):
        return (cls(*row) for row in rows)


class AbstractTransfer:

    def __init__(self, sqlite_conn, pg_conn):
        self.sqlite_conn = sqlite_conn
        self.pg_conn = pg_conn

        for dataclass_name in self.get_dataclasses():
            self.__setattr__(f'{dataclass_name}_set', set())

    def get_dataclasses(self):
        return filter(lambda attr_name: is_dataclass(self.__getattribute__(attr_name)), dir(self))

    def load_data(self):
        for dataclass_name in self.get_dataclasses():
            dataclass = self.__getattribute__(dataclass_name)
            dataclass_set = self.__getattribute__(f'{dataclass_name}_set')

            for table in dataclass.Meta.tables_to_import:
                selected = self.sqlite_conn.execute(f'SELECT * FROM {table}').fetchall()
                dataclass_set.update(dataclass.load_data(table, selected))

    def process_data(self):
        for dataclass_name in self.get_dataclasses():
            dataclass_set = self.__getattribute__(f'{dataclass_name}_set')

            for dataclass in dataclass_set:
                dataclass.process_all(self)

    def save_data(self):
        for dataclass_name in self.EXPORT_QUEUE:
            cursor = self.pg_conn.cursor()
            dataclass = self.__getattribute__(dataclass_name)
            dataclass_set = self.__getattribute__(f'{dataclass_name}_set')
            data, columns = dataclass.export_csv(dataclass_set)
            data.seek(0)
            cursor.copy_from(data, dataclass.Meta.table_to_export, sep=DELIMITER, columns=columns)

    def transfer(self):
        self.load_data()
        self.process_data()
        self.save_data()

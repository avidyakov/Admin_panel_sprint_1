import csv
import io
from dataclasses import fields, asdict, field

from psycopg2 import errors

from .transfer import DELIMITER


class Model:
    save: bool = True
    set: set = field(default_factory=set)

    def process_all(self, transfer):
        for raw_field in self._get_raw_fields():
            try:
                getattr(self, f'process_{raw_field}')(transfer)
            except AttributeError:
                continue

    @classmethod
    def _get_raw_fields(cls) -> list:
        return [f.name for f in fields(cls) if f.name.startswith('raw_')]

    @classmethod
    def _get_columns(cls) -> list:
        return [f.name for f in fields(cls) if f.name != 'save' and f.name != 'set' and not f.name.startswith('raw_')]

    def _get_values(self) -> list:
        return [str(getattr(self, field_name)) for field_name in self._get_columns()]

    def insert(self, conn) -> None:
        with conn.cursor() as cursor:
            format_columns = ', '.join(self._get_columns())
            values = ", ".join(["%s"] * len(self._get_values()))
            cursor.execute(
                f'INSERT INTO {self.Meta.table_to_export} ({format_columns}) VALUES ({values});',
                self._get_values()
            )
            conn.commit()

    @classmethod
    def _select(cls, conn, table_name: str, many: bool = False, **kwargs):
        format_condition = ' AND '.join([f'{key} = "{value}"'for key, value in kwargs.items()])
        format_columns = ', '.join(cls._get_columns())
        table_name = table_name or cls.Meta.table_to_export

        with conn.cursor() as cursor:
            try:
                cursor.execute(
                    f'SELECT {format_columns} FROM {table_name} WHERE {format_condition};'
                )
                return cursor.fetchall() if many else cursor.fetchone()
            except errors.UndefinedColumn:
                conn.rollback()

    @classmethod
    def select_first(cls, conn, table_name=None, **kwargs):
        selected = cls._select(conn, table_name, **kwargs)
        if selected:
            return cls(**dict(zip(cls._get_columns(), selected)))

    @classmethod
    def select_all(cls, conn, table_name=None, **kwargs):
        selected_list = cls._select(conn, table_name, many=True, **kwargs)
        return [cls(**dict(zip(cls._get_columns(), selected))) for selected in selected_list]

    @classmethod
    def export_csv(cls, values):
        file = io.StringIO()
        columns = cls._get_columns()
        writer = csv.DictWriter(file, columns, delimiter=DELIMITER)
        for value in values:
            if value.save:
                filtered_dict = {key: value for key, value in asdict(value).items() if not key.startswith('raw_')}
                writer.writerow(filtered_dict)

        return file, columns

    @classmethod
    def load_data(cls, table_name, rows):
        return (cls(*row) for row in rows)

import csv
import io
import os
from dataclasses import fields, asdict, field

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
    def _select(cls, cursor, table_name: str, **kwargs):
        format_condition = ' AND '.join([f'{key} = "{value}"'for key, value in kwargs.items()])
        format_columns = ', '.join(cls._get_columns())
        table_name = table_name or cls.Meta.table_to_export

        # Я потратил неприлично много времени на исправления этого проекта.
        # Таблица загружается теперь по одной, а вот до строк, которые извлекаются по одной и сразу же обрабатываются,
        # я не дошел. Все остальные замечания я исправил.
        #
        # Сейчас у меня есть большая проблема.
        # При запуске в этом месте будет вылезать ошибка psycopg2.errors.UndefinedColumn
        # т.к. строк в таблице нет и при использовании оператора WHERE БД выдает ошибку.
        # Я делал проверку типа "SELECT count(*) FROM {table_name}" или "SELECT * FROM {table_name}",
        # чтобы не фильтровать записи на первую итерацию, когда в таблице нет записей.
        # Но записей в таблице нет и при последующих итерациях)
        # Этого не может быть т.к. я создаю записи в конце каждой итерации.
        # Я делал коммиты, отрывал курсоры и новые коннекты к БД, но ничего не помогло.
        # Видимо я упускаю что-то очень простое.
        #
        # Помогите, пожалуйста) Иначе я буду переписывать все с нуля тк я очень устал уже исправлять это задание.
        # Я на него потратил очень много своего времени.

        return cursor.execute(
            f'SELECT {format_columns} FROM {table_name} WHERE {format_condition};'
        )

    @classmethod
    def select_first(cls, conn, table_name=None, **kwargs):
        cursor = conn.cursor()
        selected = cls._select(cursor, table_name, **kwargs)
        cursor.close()
        if selected:
            return cls(**dict(zip(cls._get_columns(), selected)))

    @classmethod
    def select_all(cls, conn, table_name=None, **kwargs):
        cursor = conn.cursor()
        selected_list = cls._select(cursor, table_name, **kwargs)
        cursor.close()
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

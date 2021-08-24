import sqlite3

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection) -> None:
    """Основной метод загрузки данных из SQLite в Postgres"""
    # postgres_saver = PostgresSaver(pg_conn)
    # sqlite_loader = SQLiteLoader(connection)

    # data = sqlite_loader.load_movies()
    # postgres_saver.save_all_data(data)
    print('hi!')


if __name__ == '__main__':
    dsl = {
        'dbname': 'movies',
        'user': 'postgres',
        'password': 'password',
        'host': '0.0.0.0',
        'port': 5433
    }

    with sqlite3.connect('db.sqlite') as sqlite_conn, psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn:
        load_from_sqlite(sqlite_conn, pg_conn)

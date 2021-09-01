import sqlite3

import psycopg2
from dataclasses_ import Genre, GenresMovies, Movie, Person
from loguru import logger
from psycopg2.extras import DictCursor
from transfer.abs import SQLitePostgresTransfer


class Transfer(SQLitePostgresTransfer):
    models = (Genre, Person, Movie, GenresMovies, )


if __name__ == '__main__':
    dsl = {
        'dbname': os.environ['POSTGRES_NAME'],
        'user': os.environ['POSTGRES_USER'],
        'password': os.environ['POSTGRES_PASSWORD'],
        'host': os.environ['POSTGRES_HOST'],
        'port': os.environ['POSTGRES_PORT'],
        'options': os.environ['POSTGRES_OPTIONS'],
    }

    sqlite_path = os.environ['SQLITE_PATH']

    with sqlite3.connect(sqlite_path) as sqlite_conn, \
            psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn:
        cursor = pg_conn.cursor()
        cursor.execute('SELECT * FROM content.genres')

        if not cursor.fetchone():
            transfer = Transfer(sqlite_conn, pg_conn)
            transfer.transfer()
            logger.info('Перенос данных успешно выполнен')
        else:
            logger.warning('Данные в базе уже есть')

    pg_conn.close()
    sqlite_conn.close()

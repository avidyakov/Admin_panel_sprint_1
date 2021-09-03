import os
import sqlite3
import sys

import psycopg2
from models import Genre, GenresMovies, Movie, Person
from loguru import logger
from psycopg2.extras import DictCursor
from transfer import SQLitePostgresTransfer


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

    logger.remove()
    logger.add(sys.stderr, format="{message}")
    with sqlite3.connect(sqlite_path) as sqlite_conn, \
            psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn:
        with pg_conn.cursor() as cursor:
            cursor.execute('SELECT * FROM content.genres')


            if not cursor.fetchone():
                transfer = Transfer(sqlite_conn, pg_conn)
                transfer.transfer()
                logger.info('Перенос данных успешно выполнен')
            else:
                logger.warning('Данные в базе уже есть')

    pg_conn.close()
    sqlite_conn.close()

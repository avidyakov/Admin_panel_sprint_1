import sqlite3

import psycopg2
from dataclasses_ import (ActorsMovies, DirectorsMovies, Genre, GenresMovies,
                          Movie, Person, WritersMovies)
from loguru import logger
from psycopg2.extras import DictCursor
from transfer.abs import AbstractTransfer


class Transfer(AbstractTransfer):
    actors_movies = ActorsMovies
    directors_movies = DirectorsMovies
    writers_movies = WritersMovies
    genres_movies = GenresMovies
    movie = Movie
    person = Person
    genre = Genre

    EXPORT_QUEUE = (
        'genre', 'person', 'movie', 'genres_movies',
        'writers_movies', 'directors_movies', 'actors_movies'
    )


if __name__ == '__main__':
    dsl = {
        'dbname': 'movies',
        'user': 'postgres',
        'password': 'password',
        'host': '0.0.0.0',
        'port': 5433,
        'options': '-c search_path=content',
    }

    with sqlite3.connect('db.sqlite') as sqlite_conn, \
            psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn:
        cursor = pg_conn.cursor()
        cursor.execute('SELECT * FROM content.genres')

        if not cursor.fetchone():
            transfer = Transfer(sqlite_conn, pg_conn)
            transfer.transfer()
            logger.info('Перенос данных успешно выполнен')
        else:
            logger.warning('Данные в базе уже есть')

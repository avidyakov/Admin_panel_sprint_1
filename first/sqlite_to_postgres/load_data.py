import sqlite3
import uuid
from dataclasses import dataclass, field

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor


@dataclass(frozen=True)
class Genre:
    uuid: uuid.UUID = field(default_factory=uuid.uuid4)
    name: str = ''


@dataclass(frozen=True)
class Person:
    raw_actor_id: int = None
    raw_writer_id: uuid.UUID = None
    name: str = ''
    uuid: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class Movie:
    raw_id: str
    raw_genres: str
    raw_director: str
    raw_writer: str
    title: str
    plot: str
    raw_ratings: None
    imdb_rating: float
    raw_writers: list
    uuid: uuid.UUID = field(default_factory=uuid.uuid4)

    def process_genres(self, all_genres: list[Genre], genres_movies) -> None:
        for raw_genre in self.raw_genres.split(', '):
            try:
                genre = list(filter(lambda g: g.name == raw_genre, all_genres))[0]
            except IndexError:
                genre = Genre(name=raw_genre)
                all_genres.append(genre)

            new_genres_movies = GenresMovies(genre_id=genre.uuid, movie_id=self.uuid)
            genres_movies.append(new_genres_movies)

    def process_directors(self, persons: list[Person], directors_movies) -> None:
        for raw_director in self.raw_director.split(', '):
            try:
                person = list(filter(lambda p: p.raw_writer_id == raw_director, persons))[0]
            except IndexError:
                person = Person(name=raw_director)
                persons.append(person)

            new_directors_movies = DirectorsMovies(person_id=person.uuid, movie_id=self.uuid)
            directors_movies.append(new_directors_movies)

    def process_writer(self, persons: list[Person], writers_movies) -> None:
        if self.raw_writer:
            writer = list(filter(lambda person: person.raw_writer_id == self.raw_writer, persons))[0]
            new_persons_movie = WritersMovies(person_id=writer.uuid, movie_id=self.uuid)
            writers_movies.append(new_persons_movie)

    def process_writers(self, persons: list[Person], writers_movies) -> None:
        for raw_writer in self.raw_writers:
            writer = list(filter(lambda person: person.raw_writer_id == raw_writer['id'], persons))[0]
            new_persons_movie = WritersMovies(person_id=writer.uuid, movie_id=self.uuid)
            writers_movies.append(new_persons_movie)


@dataclass(frozen=True)
class GenresMovies:
    genre_id: uuid.UUID
    movie_id: uuid.UUID


@dataclass(frozen=True)
class WritersMovies:
    person_id: uuid.UUID
    movie_id: uuid.UUID


@dataclass(frozen=True)
class DirectorsMovies:
    person_id: uuid.UUID
    movie_id: uuid.UUID


@dataclass
class ActorsMovies:
    person_id: uuid.UUID = None
    movie_id: uuid.UUID = None
    raw_actor_id: int = None
    raw_movie_id: str = None

    def process_actor_id(self, persons: list[Person]) -> None:
        person = list(filter(lambda p: p.raw_actor_id == self.raw_actor_id, persons))[0]
        self.person_id = person.uuid

    def process_movie_id(self, movies: list[Movie]) -> None:
        movie = list(filter(lambda m: m.raw_id == self.raw_movie_id, movies))[0]
        self.movie_id = movie.uuid


class Transfer:

    def __init__(self, sqlite_conn: sqlite3.Connection, pg_conn: _connection):
        self.sqlite_conn = sqlite_conn
        self.pg_conn = pg_conn
        self.movies = []
        self.persons = []
        self.movie_actors = []
        self.writers_movies = []
        self.actors_movies = []
        self.directors_movies = []

    def load_data(self):
        self.movies.extend([Movie(*row) for row in self.sqlite_conn.execute('SELECT * FROM movies').fetchall()])

        self.persons.extend([Person(raw_actor_id=id, name=name)
                             for id, name in self.sqlite_conn.execute('SELECT * FROM actors')])

        self.persons.extend([Person(raw_writer_id=id, name=name)
                             for id, name in self.sqlite_conn.execute('SELECT * FROM writers')])

        self.movie_actors.extend([ActorsMovies(raw_actor_id=actor_id, raw_movie_id=movie_id)
                                  for movie_id, actor_id in self.sqlite_conn.execute('SELECT * FROM movie_actors')])

    def process_data(self):
        pass


if __name__ == '__main__':
    dsl = {
        'dbname': 'movies',
        'user': 'postgres',
        'password': 'password',
        'host': '0.0.0.0',
        'port': 5433
    }

    with sqlite3.connect('db.sqlite') as sqlite_conn, psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn:
        instance = Transfer(sqlite_conn, pg_conn)
        instance.load_data()
        instance.save_data()

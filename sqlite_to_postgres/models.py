import json
import uuid
from dataclasses import dataclass, field

from transfer import Model


@dataclass(unsafe_hash=True)
class Genre(Model):
    id: uuid.UUID = field(default_factory=uuid.uuid4, hash=True)
    name: str = ''

    class Meta:
        tables_to_import = ()
        table_to_export = 'genres'


@dataclass(unsafe_hash=True)
class Person(Model):
    raw_actor_id: int = None
    raw_writer_id: str = None

    id: uuid.UUID = field(default_factory=uuid.uuid4, hash=True)
    name: str = ''

    class Meta:
        tables_to_import = 'actors', 'writers'
        table_to_export = 'persons'


@dataclass(unsafe_hash=True)
class Movie(Model):
    raw_id: str = ''
    raw_genres: str = ''
    raw_director: str = ''
    raw_writer: str = ''
    title: str = ''
    plot: str = ''
    raw_ratings: float = ''
    raw_imdb_rating: float = ''
    raw_writers: str = ''
    imdb_rating: float = 0.0
    id: uuid.UUID = field(default_factory=uuid.uuid4, hash=True)

    def process_all(self, transfer):
        self.save = False
        if self.raw_imdb_rating == 'N/A':
            self.imdb_rating = 0.0
        else:
            self.imdb_rating = self.raw_imdb_rating

        self.insert(transfer.pg_conn)
        super().process_all(transfer)

    def process_raw_genres(self, transfer) -> None:
        for raw_genre in self.raw_genres.split(', '):
            genre = Genre.select_first(transfer.pg_conn, name=raw_genre)
            if not genre:
                genre = Genre(name=raw_genre)
                genre.insert(transfer.pg_conn)

            genre_movie = GenresMovies.select_first(transfer.pg_conn, genre_id=genre.id, movie_id=self.id)
            if not genre_movie:
                genre_movie = GenresMovies(genre_id=genre.id, movie_id=self.id)
                genre_movie.insert(transfer.pg_conn)

    def process_raw_director(self, transfer) -> None:
        for raw_director in self.raw_director.split(', '):
            if raw_director == 'N/A':
                continue

            person = Person.select_first(transfer.pg_conn, name=raw_director)
            if not person:
                person = Person(name=raw_director)
                person.insert(transfer.pg_conn)

            person_movie = PersonsMovies.select_first(transfer.pg_conn, person_id=person.id, movie_id=self.id)
            if not person_movie:
                person_movie = PersonsMovies(person_id=person.id, movie_id=self.id, part='d')
                person_movie.insert(transfer.pg_conn)

    def process_raw_writer(self, transfer) -> None:
        if self.raw_writer:
            raw_writer_id, raw_writer_name = \
                transfer.sqlite_conn.execute(f'SELECT id, name FROM writers WHERE id == "{self.raw_writer}"').fetchone()
            person = Person.select_first(transfer.pg_conn, name=raw_writer_name)
            person_movie = PersonsMovies.select_first(transfer.pg_conn, person_id=person.id, movie_id=self.id)
            if not person_movie:
                new_persons_movie = PersonsMovies(person_id=person.id, movie_id=self.id, part='w')
                new_persons_movie.insert(transfer.pg_conn)

    def process_raw_writers(self, transfer) -> None:
        if self.raw_writers:
            for raw_writer in json.loads(self.raw_writers):
                _, raw_writer_name = \
                    transfer.sqlite_conn.execute(
                        f'''SELECT id, name FROM writers WHERE id == "{raw_writer['id']}"'''
                    ).fetchone()
                person = Person.select_first(transfer.pg_conn, name=raw_writer_name)
                if not PersonsMovies.select_first(transfer.cursor, person_id=person.id, movie_id=self.id):
                    new_persons_movie = PersonsMovies(person_id=person.id, movie_id=self.id, part='w')
                    new_persons_movie.insert(transfer.pg_conn)

    class Meta:
        tables_to_import = 'movies',
        table_to_export = 'movies'


@dataclass(unsafe_hash=True)
class GenresMovies(Model):
    genre_id: uuid.UUID
    movie_id: uuid.UUID
    id: uuid.UUID = field(default_factory=uuid.uuid4, hash=True)

    class Meta:
        tables_to_import = ()
        table_to_export = 'genres_movies'


@dataclass(unsafe_hash=True)
class PersonsMovies(Model):
    raw_movie_id: str = ''
    raw_actor_id: int = ''

    id: uuid.UUID = field(default_factory=uuid.uuid4, hash=True)
    person_id: uuid.UUID = None
    movie_id: uuid.UUID = None
    part: str = ''

    def process_raw_actor_id(self, transfer) -> None:
        if self.raw_actor_id:
            self.part = 'a'
            cursor = transfer.sqlite_conn.cursor()
            cursor.execute(
                f"""SELECT * FROM actors WHERE id = '{self.raw_actor_id}'"""
            )
            person = Person.select_first(transfer.pg_conn, name=cursor.fetchone()[1])
            self.person_id = person.id
            cursor.close()

    def process_raw_movie_id(self, transfer) -> None:
        if self.raw_movie_id:
            cursor = transfer.sqlite_conn.cursor()
            cursor.execute(
                f"""SELECT * FROM movies WHERE id = '{self.raw_movie_id}'"""
            )
            movie = Movie.select_first(transfer.pg_conn, title=cursor.fetchone()[4])
            self.movie_id = movie.id
            cursor.close()

    def process_all(self, transfer):
        super().process_all(transfer)
        cursor = transfer.sqlite_conn.cursor()
        cursor.execute(
            f"""SELECT count(*) FROM movie_actors WHERE movie_id = '{self.raw_movie_id}' AND actor_id = '{self.raw_actor_id}'"""
        )
        with transfer.pg_conn.cursor() as pg_cursor:
            pg_cursor.execute(
                f'SELECT count(*) FROM persons_movies WHERE part = %s AND person_id = %s AND movie_id = %s',
                (self.part, str(self.person_id), str(self.movie_id))
            )
            count = pg_cursor.fetchone()['count']
            if not any((cursor.fetchone()[0] == 2, count == 1)):
                self.insert(transfer.pg_conn)

        cursor.close()
        self.save = False

    class Meta:
        tables_to_import = 'movie_actors',
        table_to_export = 'persons_movies'

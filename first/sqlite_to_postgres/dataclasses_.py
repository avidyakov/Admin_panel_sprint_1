import json
import uuid
from dataclasses import dataclass, field

from transfer.abs import AbstractDataclass


@dataclass(unsafe_hash=True)
class Genre(AbstractDataclass):
    id: uuid.UUID = field(default_factory=uuid.uuid4, hash=True)
    name: str = ''

    class Meta:
        tables_to_import = ()
        table_to_export = 'genres'


@dataclass(unsafe_hash=True)
class Person(AbstractDataclass):
    raw_actor_id: int = None
    raw_writer_id: str = None
    name: str = ''
    id: uuid.UUID = field(default_factory=uuid.uuid4, hash=True)

    @classmethod
    def load_data(cls, table_name, rows):
        if table_name == 'actors':
            return (cls(raw_actor_id=row[0], name=row[1]) for row in rows)
        return (cls(raw_writer_id=row[0], name=row[1]) for row in rows)

    class Meta:
        tables_to_import = 'actors', 'writers'
        table_to_export = 'persons'


@dataclass(unsafe_hash=True)
class Movie(AbstractDataclass):
    raw_id: str
    raw_genres: str
    raw_director: str
    raw_writer: str
    title: str
    plot: str
    raw_ratings: None
    raw_imdb_rating: float
    raw_writers: str
    imdb_rating: float = 0.0
    id: uuid.UUID = field(default_factory=uuid.uuid4, hash=True)

    def process_raw_imdb_rating(self, transfer):
        if self.raw_imdb_rating == 'N/A':
            self.imdb_rating = 0.0
        else:
            self.imdb_rating = self.raw_imdb_rating

    def process_raw_genres(self, transfer) -> None:
        for raw_genre in self.raw_genres.split(', '):
            try:
                genre = list(filter(lambda g: g.name == raw_genre, transfer.genre_set))[0]
            except IndexError:
                genre = Genre(name=raw_genre)
                transfer.genre_set.add(genre)

            new_genres_movies = GenresMovies(genre_id=genre.id, movie_id=self.id)
            transfer.genres_movies_set.add(new_genres_movies)

    def process_raw_director(self, transfer) -> None:
        for raw_director in self.raw_director.split(', '):
            try:
                person = list(filter(lambda p: p.raw_writer_id == raw_director, transfer.person_set))[0]
            except IndexError:
                person = Person(name=raw_director)
                transfer.person_set.add(person)

            new_directors_movies = DirectorsMovies(person_id=person.id, movie_id=self.id)
            transfer.directors_movies_set.add(new_directors_movies)

    def process_raw_writer(self, transfer) -> None:
        if self.raw_writer:
            writer = list(filter(lambda person: person.raw_writer_id == self.raw_writer, transfer.person_set))[0]
            new_persons_movie = WritersMovies(person_id=writer.id, movie_id=self.id)
            transfer.writers_movies_set.add(new_persons_movie)

    def process_raw_writers(self, transfer) -> None:
        if self.raw_writers:
            for raw_writer in json.loads(self.raw_writers):
                writer = list(filter(lambda p: p.raw_writer_id == raw_writer['id'], transfer.person_set))[0]
                new_persons_movie = WritersMovies(person_id=writer.id, movie_id=self.id)
                transfer.writers_movies_set.add(new_persons_movie)

    class Meta:
        tables_to_import = 'movies',
        table_to_export = 'movies'


@dataclass
class GenresMovies(AbstractDataclass):
    genre_id: uuid.UUID
    movie_id: uuid.UUID

    class Meta:
        tables_to_import = ()
        table_to_export = 'genres_movies'

    def __hash__(self):
        return hash(f'{self.genre_id}{self.movie_id}')


@dataclass
class WritersMovies(AbstractDataclass):
    person_id: uuid.UUID
    movie_id: uuid.UUID

    class Meta:
        tables_to_import = ()
        table_to_export = 'writers_movies'

    def __hash__(self):
        return hash(f'{self.person_id}{self.movie_id}')


@dataclass
class DirectorsMovies(AbstractDataclass):
    person_id: uuid.UUID
    movie_id: uuid.UUID

    class Meta:
        tables_to_import = ()
        table_to_export = 'directors_movies'

    def __hash__(self):
        return hash(f'{self.person_id}{self.movie_id}')


@dataclass
class ActorsMovies(AbstractDataclass):
    raw_movie_id: str = None
    raw_actor_id: int = None
    person_id: uuid.UUID = None
    movie_id: uuid.UUID = None

    def process_raw_actor_id(self, transfer) -> None:
        if self.raw_actor_id:
            person = list(filter(lambda p: str(p.raw_actor_id) == self.raw_actor_id, transfer.person_set))[0]
            self.person_id = person.id

    def process_raw_movie_id(self, transfer) -> None:
        if self.raw_movie_id:
            movie = list(filter(lambda m: m.raw_id == self.raw_movie_id, transfer.movie_set))[0]
            self.movie_id = movie.id

    class Meta:
        tables_to_import = 'movie_actors',
        table_to_export = 'actors_movies'

    def __hash__(self):
        return hash(f'{self.person_id}{self.movie_id}')

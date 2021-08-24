CREATE DATABASE movies;

CREATE SCHEMA IF NOT EXISTS content;

CREATE TABLE IF NOT EXISTS content.person (
    id uuid PRIMARY KEY,
    first_name VARCHAR(128) NOT NULL,
    last_name VARCHAR(128) NOT NULL
);

CREATE TABLE IF NOT EXISTS content.genre (
    id uuid PRIMARY KEY,
    name VARCHAR(64) NOT NULL
);

CREATE TABLE IF NOT EXISTS content.movies (
    id uuid PRIMARY KEY,
    title VARCHAR(128) NOT NULL,
    plot TEXT,
    imdb_rating FLOAT
);

CREATE TABLE IF NOT EXISTS content.genres_movies (
  genre_id uuid NOT NULL,
  movie_id uuid NOT NULL,
  PRIMARY KEY (genre_id, movie_id),
  FOREIGN KEY (genre_id) REFERENCES content.person(id) ON UPDATE CASCADE,
  FOREIGN KEY (movie_id) REFERENCES content.movies(id) ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS content.writers_movies (
  writer_id uuid NOT NULL,
  movie_id uuid NOT NULL,
  PRIMARY KEY (writer_id, movie_id),
  FOREIGN KEY (writer_id) REFERENCES content.person(id) ON UPDATE CASCADE,
  FOREIGN KEY (movie_id) REFERENCES content.movies(id) ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS content.actors_movies (
  actor_id uuid NOT NULL,
  movie_id uuid NOT NULL,
  PRIMARY KEY (actor_id, movie_id),
  FOREIGN KEY (actor_id) REFERENCES content.person(id) ON UPDATE CASCADE,
  FOREIGN KEY (movie_id) REFERENCES content.movies(id) ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS content.directors_movies (
  director_id uuid NOT NULL,
  movie_id uuid NOT NULL,
  PRIMARY KEY (director_id, movie_id),
  FOREIGN KEY (director_id) REFERENCES content.person(id) ON UPDATE CASCADE,
  FOREIGN KEY (movie_id) REFERENCES content.movies(id) ON UPDATE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS genres_movies_index ON content.genres_movies (genre_id, movie_id);

CREATE UNIQUE INDEX IF NOT EXISTS writers_movies_index ON content.writers_movies (writer_id, movie_id);

CREATE UNIQUE INDEX IF NOT EXISTS actors_movies_index ON content.actors_movies (actor_id, movie_id);

CREATE UNIQUE INDEX IF NOT EXISTS directors_movies_index ON content.directors_movies (director_id, movie_id);

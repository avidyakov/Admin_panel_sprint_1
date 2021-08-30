CREATE DATABASE movies;

\c movies;

CREATE SCHEMA IF NOT EXISTS content;

CREATE TABLE IF NOT EXISTS content.persons (
    id uuid PRIMARY KEY,
    name VARCHAR(128) NOT NULL
);

CREATE TABLE IF NOT EXISTS content.genres (
    id uuid PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS content.movies (
    id uuid PRIMARY KEY,
    title VARCHAR(128) NOT NULL,
    plot TEXT,
    imdb_rating FLOAT,
    creation_date DATE,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    file_path VARCHAR(256),
    type VARCHAR(2),
    rating FLOAT,
    certificate TEXT
);

CREATE TABLE IF NOT EXISTS content.genres_movies (
    id uuid PRIMARY KEY,
    genre_id uuid NOT NULL,
    movie_id uuid NOT NULL,
    FOREIGN KEY (genre_id) REFERENCES content.genres(id) ON UPDATE CASCADE,
    FOREIGN KEY (movie_id) REFERENCES content.movies(id) ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS content.writers_movies (
    id uuid PRIMARY KEY,
    person_id uuid NOT NULL,
    movie_id uuid NOT NULL,
    FOREIGN KEY (person_id) REFERENCES content.persons(id) ON UPDATE CASCADE,
    FOREIGN KEY (movie_id) REFERENCES content.movies(id) ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS content.actors_movies (
    id uuid PRIMARY KEY,
    person_id uuid NOT NULL,
    movie_id uuid NOT NULL,
    FOREIGN KEY (person_id) REFERENCES content.persons(id) ON UPDATE CASCADE,
    FOREIGN KEY (movie_id) REFERENCES content.movies(id) ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS content.directors_movies (
    id uuid PRIMARY KEY,
    person_id uuid NOT NULL,
    movie_id uuid NOT NULL,
    FOREIGN KEY (person_id) REFERENCES content.persons(id) ON UPDATE CASCADE,
    FOREIGN KEY (movie_id) REFERENCES content.movies(id) ON UPDATE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS genres_movies_index ON content.genres_movies (genre_id, movie_id);

CREATE UNIQUE INDEX IF NOT EXISTS writers_movies_index ON content.writers_movies (person_id, movie_id);

CREATE UNIQUE INDEX IF NOT EXISTS actors_movies_index ON content.actors_movies (person_id, movie_id);

CREATE UNIQUE INDEX IF NOT EXISTS directors_movies_index ON content.directors_movies (person_id, movie_id);

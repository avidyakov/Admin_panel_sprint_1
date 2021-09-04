import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class TimeStampedMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Genre(TimeStampedMixin):
    id = models.UUIDField('UUID', primary_key=True, default=uuid.uuid4)
    name = models.CharField('Название', max_length=255)
    description = models.TextField('Описание', blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        # Я не указываю отдельную схему тк в настройках подключения я указал -с search_path=public,content.
        # Таблицы создаются в правильных схемах и это решения изящнее, чем делать много кривых записей с кавычками
        db_table = 'genres'


class Film(TimeStampedMixin):

    class FilmType(models.TextChoices):
        MOVIE = 'movie', 'Фильм'
        TV_SHOW = 'series', 'Сериал'

    id = models.UUIDField('UUID', primary_key=True, default=uuid.uuid4)
    title = models.CharField('Заголовок', max_length=255)
    plot = models.TextField('Описание', blank=True)
    creation_date = models.DateField('Год выпуска', blank=True)
    certificate = models.TextField('Сертификат', blank=True)
    file_path = models.FileField('Файл', upload_to='films/', blank=True)
    rating = models.FloatField('Рейтинг', validators=[MinValueValidator(0), MaxValueValidator(10)], blank=True)
    type = models.CharField('Тип', max_length=7, choices=FilmType.choices, default=FilmType.MOVIE)
    genres = models.ManyToManyField(Genre, through='GenresFilms', blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Кинопроизведение'
        verbose_name_plural = 'Кинопроизведения'
        db_table = 'movies'


class Person(TimeStampedMixin):
    id = models.UUIDField('UUID', primary_key=True, default=uuid.uuid4)
    name = models.CharField('Имя', max_length=127)
    films = models.ManyToManyField(Film, verbose_name='Фильмы', related_name='persons', through='PersonsFilms')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Персона'
        verbose_name_plural = 'Персоны'
        db_table = 'persons'


class GenresFilms(models.Model):
    id = models.UUIDField('UUID', primary_key=True, default=uuid.uuid4)
    movie = models.ForeignKey(Film, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    class Meta:
        db_table = 'genres_movies'


class PersonsFilms(models.Model):

    class PersonRole(models.TextChoices):
        ACTOR = 'a', 'Актер'
        WRITER = 'w', 'Сценарист'
        DIRECTOR = 'd', 'Режиссер'

    id = models.UUIDField('UUID', primary_key=True, default=uuid.uuid4)
    movie = models.ForeignKey(Film, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    part = models.CharField('Роль', max_length=1, choices=PersonRole.choices)

    class Meta:
        db_table = 'persons_movies'

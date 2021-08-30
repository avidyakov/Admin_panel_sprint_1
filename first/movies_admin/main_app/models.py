from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class TimeStampedMixin:
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Genre(TimeStampedMixin, models.Model):
    name = models.CharField('Название', max_length=255)
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        db_table = 'genres'


class Film(TimeStampedMixin, models.Model):

    class FilmType(models.TextChoices):
        MOVIE = 'mo', 'Фильм'
        TV_SHOW = 'tv', 'Сериал'

    title = models.CharField('Заголовок', max_length=255)
    plo = models.TextField('Описание', blank=True)
    creation_date = models.DateField('Год выпуска', blank=True)
    certificate = models.TextField('Сертификат', blank=True)
    file_path = models.FileField('Файл', upload_to='films/', blank=True)
    rating = models.FloatField('Рейтинг', validators=[MinValueValidator(0), MaxValueValidator(10)], blank=True)
    type = models.CharField('Тип', max_length=2, choices=FilmType.choices, default=FilmType.MOVIE)

    genres = models.ManyToManyField(Genre, through='GenresFilms')

    class Meta:
        verbose_name = 'Кинопроизведение'
        verbose_name_plural = 'Кинопроизведения'
        db_table = 'movies'


class Person(TimeStampedMixin, models.Model):
    first_name = models.CharField('Имя', max_length=127)
    last_name = models.CharField('Фамилия', max_length=127)

    actor = models.ManyToManyField(Film, verbose_name='Актер', related_name='actors')
    writer = models.ManyToManyField(Film, verbose_name='Сценарист', related_name='writers')
    director = models.ManyToManyField(Film, verbose_name='Режиссер', related_name='directors')

    class Meta:
        verbose_name = 'Персона'
        verbose_name_plural = 'Персоны'
        db_table = 'persons'


class GenresFilms(models.Model):
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'genres_movies'


class ActorsFilms(models.Model):
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'actors_movies'


class WritersFilms(models.Model):
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'writers_movies'


class DirectorsFilms(models.Model):
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'directors_movies'

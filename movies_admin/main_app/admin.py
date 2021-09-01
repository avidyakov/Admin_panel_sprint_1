from django.contrib import admin

from .models import Film, Genre, Person, PersonsFilms


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    exclude = 'id',


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    pass


class PersonsInline(admin.TabularInline):
    model = PersonsFilms
    verbose_name = 'Персона'
    verbose_name_plural = 'Персоны'
    extra = 0


class GenresInline(admin.TabularInline):
    model = Film.genres.through
    verbose_name = 'Жанр'
    verbose_name_plural = 'Жанры'
    extra = 0


@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    search_fields = 'title',
    inlines = GenresInline, PersonsInline

from django.contrib import admin

from .models import Film, Genre, Person


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    exclude = 'id',


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    pass


class ActorsInline(admin.TabularInline):
    model = Person.actor.through
    verbose_name = 'Актер'
    verbose_name_plural = 'Актеры'
    extra = 0


class DirectorsInline(admin.TabularInline):
    model = Person.director.through
    verbose_name = 'Режиссер'
    verbose_name_plural = 'Режиссеры'
    extra = 0


class WritersInline(admin.TabularInline):
    model = Person.writer.through
    verbose_name = 'Сценарист'
    verbose_name_plural = 'Сценаристы'
    extra = 0


class GenresInline(admin.TabularInline):
    model = Film.genres.through
    verbose_name = 'Жанр'
    verbose_name_plural = 'Жанры'
    extra = 0


@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    search_fields = 'title',
    inlines = GenresInline, ActorsInline, DirectorsInline, WritersInline

from django.contrib import admin

from .models import Genre, Film, Person


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass


@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    pass


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    pass

from django.contrib import admin

from project.genre import models


class GenreAdmin(admin.ModelAdmin):
    ordering = ("genre",)
    search_fields = ("genre",)
    list_display = (
        "id",
        "genre",
        "rank",
    )


admin.site.register(models.Genre, GenreAdmin)

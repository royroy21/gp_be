from django.contrib import admin

from project.gig import models


class GenreAdmin(admin.ModelAdmin):
    ordering = ("genre",)
    search_fields = ("genre",)
    list_display = (
        "id",
        "genre",
        "rank",
    )


class GigAdmin(admin.ModelAdmin):
    ordering = ("start_date",)
    list_display = (
        "id",
        "user",
        "title",
        "artist",
        "has_spare_ticket",
        "start_date",
        "active",
    )
    search_fields = (
        "title",
        "user__username",
        "user__email",
        "user_id",
    )


admin.site.register(models.Genre, GenreAdmin)
admin.site.register(models.Gig, GigAdmin)

from django.contrib import admin

from project.gig import models


class GenreAdmin(admin.ModelAdmin):
    ordering = ("genre",)
    search_fields = ("genre",)


class GigAdmin(admin.ModelAdmin):
    ordering = ("-date_created",)
    search_fields = (
        "title",
        "user__username",
        "user__email",
        "user_id",
    )


admin.site.register(models.Genre, GenreAdmin)
admin.site.register(models.Gig, GigAdmin)

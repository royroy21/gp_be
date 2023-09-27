from django.contrib import admin

from project.audio import models


class AlbumAdmin(admin.ModelAdmin):
    ordering = ("date_created",)
    list_display = (
        "id",
        "title",
        "description",
        "image",
        "profile",
        "gig",
        "user",
    )
    search_fields = (
        "id",
        "gig__id",
        "title",
        "description",
        "profile__id",
        "profile__email",
        "profile__username",
        "gig__id",
        "gig__title",
        "gig__location",
        "user__id",
        "user__email",
        "user__username",
    )


class AudioAdmin(admin.ModelAdmin):
    ordering = ("date_created",)
    list_display = (
        "id",
        "title",
        "position",
        "album",
        "image",
        "file",
        "user",
    )
    search_fields = (
        "id",
        "title",
        "user__id",
        "user__email",
        "user__username",
        "album__id",
    )


admin.site.register(models.Album, AlbumAdmin)
admin.site.register(models.Audio, AudioAdmin)

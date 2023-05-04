from django.contrib import admin

from project.chat import models


class RoomAdmin(admin.ModelAdmin):
    ordering = ("date_created",)
    list_display = (
        "id",
        "user",
        "type",
        "gig",
        "active",
    )
    search_fields = (
        "gig__id",
        "gig__title",
        "gig__location",
        "user__username",
        "user__email",
        "user__id",
    )


class MessageAdmin(admin.ModelAdmin):
    ordering = ("date_created",)
    list_display = (
        "id",
        "room",
        "user",
    )
    search_fields = (
        "user__username",
        "user__email",
        "user__id",
    )


admin.site.register(models.Room, RoomAdmin)
admin.site.register(models.Message, MessageAdmin)

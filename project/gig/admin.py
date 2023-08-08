from django.contrib import admin

from project.gig import models


class GigAdmin(admin.ModelAdmin):
    ordering = ("-date_created",)
    list_display = (
        "id",
        "user",
        "title",
        "location",
        "has_spare_ticket",
        "date_created",
        "start_date",
        "active",
    )
    search_fields = (
        "title",
        "description",
        "location",
        "user__username",
        "user__email",
        "user__id",
    )


admin.site.register(models.Gig, GigAdmin)

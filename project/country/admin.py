from django.contrib import admin

from project.country import models


class CountryCodeAdmin(admin.ModelAdmin):
    ordering = (
        "country",
        "code",
    )
    search_fields = (
        "country",
        "code",
    )
    list_display = ("id", "country", "code", "rank")


admin.site.register(models.CountryCode, CountryCodeAdmin)

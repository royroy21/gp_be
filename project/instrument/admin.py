from django.contrib import admin

from project.instrument import models


class InstrumentAdmin(admin.ModelAdmin):
    ordering = ("instrument",)
    search_fields = ("instrument",)
    list_display = (
        "id",
        "instrument",
        "rank",
    )


admin.site.register(models.Instrument, InstrumentAdmin)

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from project.custom_user import models

User = get_user_model()


class NotificationTokenAdmin(admin.ModelAdmin):
    ordering = ("date_created",)
    list_filter = ("active",)
    list_display = (
        "id",
        "user",
        "token",
        "active",
    )
    search_fields = (
        "user__username",
        "user__email",
        "user__id",
    )


class ResetPasswordAdmin(admin.ModelAdmin):
    ordering = ("date_created",)
    list_filter = ("active",)
    list_display = (
        "id",
        "user",
        "token",
        "active",
    )
    search_fields = (
        "user__username",
        "user__email",
        "user__id",
    )


class UserAdmin(BaseUserAdmin):
    fieldsets = tuple(
        list(BaseUserAdmin.fieldsets)  # type: ignore
        + [
            (
                "Extra",
                {
                    "fields": (
                        "subscribed_to_emails",
                        "point",
                        "location",
                        "country",
                        "bio",
                        "genres",
                        "instruments",
                        "instruments_needed",
                        "is_band",
                        "is_musician",
                        "is_looking_for_musicians",
                        "is_looking_for_band",
                        "theme",
                        "units",
                        "preferred_units",
                        "image",
                        "thumbnail",
                    )
                },
            ),
        ]
    )
    readonly_fields = ("date_joined",)


admin.site.register(models.NotificationToken, NotificationTokenAdmin)
admin.site.register(models.ResetPasswordToken, ResetPasswordAdmin)
admin.site.register(User, UserAdmin)

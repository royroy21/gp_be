from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

User = get_user_model()


class UserAdmin(BaseUserAdmin):
    fieldsets = tuple(
        list(BaseUserAdmin.fieldsets)  # type: ignore
        + [
            (
                "Extra",
                {
                    "fields": (
                        "subscribed_to_emails",
                        "location",
                        "country",
                        "theme",
                        "units",
                        "preferred_units",
                    )
                },
            ),
        ]
    )
    readonly_fields = ("date_joined",)


admin.site.register(User, UserAdmin)

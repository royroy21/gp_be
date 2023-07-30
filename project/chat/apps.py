from django.apps import AppConfig


class ChatConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "project.chat"

    def ready(self):
        import project.chat.signals  # noqa

from django.contrib.auth import get_user_model
from rest_framework import exceptions

User = get_user_model()


def is_authenticated(request):
    if request.user not in User.objects.all():
        raise exceptions.PermissionDenied

    return True

def is_owner(request, obj):
    if not request.user == obj:
        raise exceptions.PermissionDenied

    return True

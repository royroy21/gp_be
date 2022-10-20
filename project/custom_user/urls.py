from django.urls import path

from project.custom_user.api import UserDetail, UserList

urlpatterns = [
    path(
        "api/user/<pk>/",
        UserDetail.as_view(),
        name="user_detail",
    ),
    path(
        "api/user/",
        UserList.as_view(),
        name="user_list",
    ),
]

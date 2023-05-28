"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt import views

from project.chat import api as chat_api
from project.country import api as country_api
from project.custom_user.api import UserViewSet
from project.genre import api as genre_api
from project.gig import api as gig_api

api_router = DefaultRouter()
api_router.register(r"user", UserViewSet, basename="user")
api_router.register(
    r"message", chat_api.MessageViewSet, basename="message-api"
)
api_router.register(r"room", chat_api.RoomViewSet, basename="room-api")
api_router.register(r"gig", gig_api.GigViewSet, basename="gig-api")

search_router = DefaultRouter()
search_router.register(
    r"gig",
    gig_api.GigDocumentViewSet,
    basename="gig-search",
)

urlpatterns = [
    path("api/", include(api_router.urls)),
    path("api/country/", country_api.get_country),
    path("search/", include(search_router.urls)),
    path("search/country/suggest/", country_api.suggest_country),
    path("search/genre/suggest/", genre_api.suggest_genre),
    path("admin/", admin.site.urls),
    path(
        "api/token/",
        views.TokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        "api/token/refresh/",
        views.TokenRefreshView.as_view(),
        name="token_refresh",
    ),
]

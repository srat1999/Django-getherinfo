from . import views
from django.urls import path


urlpatterns = [
    path(r'getdomain/',views.getdomain),
]
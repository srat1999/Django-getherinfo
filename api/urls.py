from . import views
from django.urls import path


urlpatterns = [
    path(r'getdomain/',views.getdomain),
    path(r'article/',views.getarticle),
    path(r'article/catcharticle',views.catcharticle),
]
from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from . import views

app_name = "home"  # Namespace for this application

urlpatterns = [
    path("Administration/", login_required(views.index), name="dashboard"),
    path("stats/", views.statistiques_view, name="stat"),
    path("e-presence/", views.liste_presence_view, name="abs"),
    path("archives/", views.archives_view, name="archives"),
    path("import/", views.import_data_view, name="import"),
]

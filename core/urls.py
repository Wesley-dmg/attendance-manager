"""
core URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from rest_framework.authtoken.views import obtain_auth_token

from core import settings  # <-- NEW
from django.conf.urls.static import static

urlpatterns = [
    path("", include("apps.home.urls")),
    path("admin/", admin.site.urls),
    # path('', include('admin_datta.urls')),
    path("", include("apps.users.urls")),  # Inclure les URLs de l'application users
    path(
        "courses/", include(("apps.courses.urls", "courses"), namespace="courses")
    ),  # Inclure les URLs de l'app 'courses'
    path(
        "subjects/", include(("apps.subjects.urls", "subjects"), namespace="subjects")
    ),  # Inclure les URLs de l'app 'subjects'
    path(
        "common/", include(("apps.common.urls", "common"), namespace="common")
    ),  # Inclure les URLs de l'app 'common'
    path(
        "rooms/", include(("apps.rooms.urls", "rooms"), namespace="rooms")
    ),  # Inclure les URLs de l'app 'rooms'
    path(
        "availability/",
        include(("apps.availability.urls", "availability"), namespace="availability"),
    ),  # Inclure les URLs de l'app 'availability'
    path(
        "timetables/",
        include(("apps.timetable.urls", "timetable"), namespace="timetable"),
    ),  # Inclure les URLs de l'app 'timetable'
]

# Servir les fichiers médias en mode développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

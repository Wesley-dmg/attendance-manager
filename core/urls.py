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
    
    path("courses/", include(("apps.courses.urls", "courses"), namespace="courses")),  # Inclure les URLs de l'app 'courses'
    
    path("subjects/", include(("apps.subjects.urls", "subjects"), namespace="subjects")),  # Inclure les URLs de l'app 'subjects'
    
    path("common/", include(("apps.common.urls", "common"), namespace="common")),  # Inclure les URLs de l'app 'common'
    
    path("api/", include("attendance_api.urls")),

]

# Servir les fichiers médias en mode développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

"""core URL Configuration

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
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django_custom_error_views.views import handler400 as ui_handler400
from django_custom_error_views.views import handler403 as ui_handler403
from django_custom_error_views.views import handler404 as ui_handler404
from django_custom_error_views.views import handler500 as ui_handler500
urlpatterns = [
    path('', include('home.urls')),
    path("admin/", admin.site.urls),
    path("", include('admin_corporate.urls')),
    path(
        "400/",
        ui_handler400,
        kwargs={"exception": Exception("Bad Request!")},
    ),
    path(
        "403/",
        ui_handler403,
        kwargs={"exception": Exception("Permission Denied")},
    ),
    path(
        "404/",
        ui_handler404,
        kwargs={"exception": Exception("Page not Found")},
    ),
    path("500/", ui_handler500),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#if settings.DEBUG:
#    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
#    urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_URL)

handler400 = "django_custom_error_views.views.handler400"
handler403 = "django_custom_error_views.views.handler403"
handler404 = "django_custom_error_views.views.handler404"
handler500 = "django_custom_error_views.views.handler500"


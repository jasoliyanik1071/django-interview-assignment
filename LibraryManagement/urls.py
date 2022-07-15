"""
	LibraryManagement URL Configuration

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
from django.urls import path, include

from django.conf.urls import url

# from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework_swagger.views import get_swagger_view


from authusers.views import index

schema_view = get_swagger_view(title="Library Management API")


urlpatterns = [
    path('admin/', admin.site.urls),

    path("", index, name="index"),

    url("swagger/", schema_view),


    # URL's :: REST for Authentication, Login, Sign-Up, Logout
    path("api/v1/authusers/", include(("authusers.urls", "authusers"), namespace="rest_authusers")),

    # URL's :: REST for Book Management
    # i.e:
    # As Librarian - Add, View, Update, Delete books
    # As Member - View, Borrow, Return Book
    path("api/v1/managebook/", include(("book_management.urls", "book_management"), namespace="rest_book_management")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
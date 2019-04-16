"""movie URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path

from api.views import CommentView, MovieView, TopView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('movies', MovieView.as_view(), name='movies'),
    path('movies/<int:pk>/', MovieView.as_view(), name='movie-by-id'),
    path('comments', CommentView.as_view(), name='comments'),
    path('top', TopView.as_view(), name='top-movies'),
]

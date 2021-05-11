from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from movie import views


urlpatterns = [
    path('', views.main_page, name='main'),
    path('result/<path:movie_1>/<path:movie_2>/<path:movie_3>', views.result_page, name='res'),
]

urlpatterns += staticfiles_urlpatterns()

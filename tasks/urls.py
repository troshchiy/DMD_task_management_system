from django.urls import path

from tasks.views import home_page

urlpatterns = [
    path('', home_page, name='home'),
]
from django.urls import path

from cap_app.views import home


urlpatterns = [
    path('', home, name='home')
]

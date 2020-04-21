from django.urls import path

from cap_app.views import home

app_name='cap_app'

urlpatterns = [
    path('', home, name='home')
]

from django.urls import path

from cap_app.views import home,check_the_reason_validity


urlpatterns = [
    path('', home, name='home'),
    path('check/', check_the_reason_validity, name='check_the_reason_validity')
]

from django.urls import path

from cap_app.views import home,check_the_reason_validity, clean_csv_to_db, randomize_clean_csv_to_db


urlpatterns = [
    path('', home, name='home'),
    path('check/', check_the_reason_validity, name='check_the_reason_validity'),
    path('clean_csv_to_db/', clean_csv_to_db, name='clean_csv_to_db'),
    path('randomize_clean_csv_to_db/', randomize_clean_csv_to_db, name='randomize_clean_csv_to_db'),
]

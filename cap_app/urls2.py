from django.urls import path

from cap_app.views2 import home, check_the_reason_validity, clean_csv_question, randomize_correct_options_and_clean_csv, \
    insert_options_and_randomize_clean_csv


urlpatterns = [
    path('', home),
    path('check/', check_the_reason_validity),
    path('clean_csv_question/', clean_csv_question),
    path('randomize_correct_options_and_clean_csv/', randomize_correct_options_and_clean_csv),
    path('insert_options_and_randomize_clean_csv/', insert_options_and_randomize_clean_csv),
]
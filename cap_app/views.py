from rest_framework.decorators import api_view
from rest_framework.response import Response

import mysql.connector


def nonalpha_strip(raw_data):
    question = raw_data[0]
    while not question[0].isalpha() or not question[-1].isalpha():
        if not question[0].isalpha():
            question = question.replace(question[0],'', 1)
        if not question[-1].isalpha():
            question = question[::-1].replace(question[::-1][0], '', 1)[::-1]
    raw_data = list(raw_data)
    raw_data[0] = question
    return tuple(raw_data)


def clean_add_punctuation(raw_data):
    question = raw_data[0]
    wh_list = ['what', 'who', 'whom', 'whose','how', 'where', 'when','why','which']
    question_list = question.lower().split(' ')
    question_filt = [True for q in question_list if q in wh_list]
    question_joined = ' '.join(question_list)
    if any(question_filt):
        question_joined = question_joined + '?'
    else:
        question_joined = question_joined + '....'    
        
    raw_data = list(raw_data)
    raw_data[0] = question_joined.capitalize()
    return tuple(raw_data)


def update_db(cleaned_question, db_name, table_name):
    mycursor.execute('UPDATE questions SET Question = "sth";')
    db_name = request.query_params['db_name']
    table_name = request.query_params['table_name']
    mydb = mysql.connector.connect(
        host='localhost',
        user='root',
        passwd='',
        database=db_name
    )
    mycursor = mydb.cursor()
    cmd = f'UPDATE {table_name} SET Question = "{cleaned_question}";'
    mycursor.execute('UPDATE questions SET Question = "sth";')
    # UPDATE table_users
    #     SET cod_user = (case when user_role = 'student' then '622057'
    #                      when user_role = 'assistant' then '2913659'
    #                      when user_role = 'admin' then '6160230'
    #                 end)




@api_view(['GET'])
def home(request):
    print(request.query_params)
    db_name = request.query_params['db_name']
    table_name = request.query_params['table_name']
    mydb = mysql.connector.connect(
        host='localhost',
        user='root',
        passwd='',
        database=db_name
    )
    mycursor = mydb.cursor()
    mycursor.execute(f'select * from {table_name};')
    raw_data = list(mycursor)
    print(type(raw_data))

    nonalpha_strip_data = list(map(nonalpha_strip, raw_data))
    print(nonalpha_strip_data[0:3])
    cleaned_data = list(map(clean_add_punctuation, nonalpha_strip_data))

    mycursor.execute('show columns from questions;')
    print(list(mycursor))

    mycursor.execute('select * from questions where Option_A="Amperes law";')
    print(list(mycursor))
    
    # mycursor.execute('UPDATE questions SET Question = "sth";')

    # mycursor.execute(f'drop table {table_name};')


    print(mycursor.lastrowid)

    return Response({'context': 'context'})


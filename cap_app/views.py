from rest_framework.decorators import api_view
from rest_framework.response import Response

import warnings
warnings.filterwarnings("ignore")


from profanity_check import predict, predict_prob




first_cleaner = ['{', '[', '(','$', '#', '<', '-', '+', '±', '∠', '|', 'π','~', '∆' ,'∑', '∏', 'e', 'μ', 'σ', 'n', 'ε', '∞', '' ]
last_cleaner = ['=','}', ']', ')', '°', '|', 'π', '!', '∆', 'γ', 'μ', 'ε', '∞', ]
greek_alphabets = ['Α', 'α', 'Β', 'β', 'Γ', 'γ', 'Δ', 'δ', 'Ε', 'ε', 'Ζ', 'ζ', 'Η', 'η', 'Θ', 'θ', 'Ι', 'ι', 'Κ', 'κ', 'Λ', 'λ', 'Μ', 'μ', 'Ν', 'ν','Ξ', 'ξ', 'Ο', 'ο', 'Π', 'π', 'Ρ', 'ρ', 'Σ', 'σ', 'ς', 'Τ', 'τ', 'Υ', 'υ', 'Φ', 'φ', 'Χ', 'χ', 'Ψ', 'ψ','Ω','ω', '∆' ,'∑', '∏', 'e', 'μ', 'σ', 'n', 'ε', '∞']
wh_list = ['what', 'who', 'whom', 'whose','how', 'where', 'when','why','which']

def clean_garbage(question):
    while ((not question[0].isalnum()) and (question[0] not in first_cleaner) and (question[0] not in greek_alphabets)) or ((not question[-1].isalnum()) and (question[-1] not in last_cleaner) and (question[-1] not in greek_alphabets)):
        if (not question[0].isalnum()) and (question[0] not in first_cleaner) and (question[0] not in greek_alphabets):
            question = question.replace(question[0],'', 1)
        if (not question[-1].isalnum()) and (question[-1] not in last_cleaner) and (question[-1] not in greek_alphabets):
            question = question[::-1].replace(question[::-1][0], '', 1)[::-1]
    return question

def add_punctuation_dots(question):
    unnecessary_in_wh = ['=', '?']
    question_list = question.lower().split(' ')
    question_filt = [True for q in question_list if q in wh_list]
    question_joined = ' '.join(question_list)
    if any(question_filt):
        while question_joined[-1] in unnecessary_in_wh:
            question_joined = question_joined[::-1].replace(question_joined[::-1][0], '', 1)[::-1]
        question_joined = (question_joined).rstrip() + '?'
    else:
        # this while field should be customized later based on other inputs
        while question_joined[-1] == '=':
            question_joined = question_joined[::-1].replace(question_joined[::-1][0], '', 1)[::-1]
        question_joined = question_joined + '=....'
    
    return question_joined.capitalize()

import re



@api_view(['GET'])
def home(request):

    try:
        try:
            if request.data:
                question = request.data['question']
            elif request.query_params:
                question = request.query_params['question']
            print(question)
        except:
            return Response({'error': 'Unable to get the question from URL'})
        profanity_status, profanity_probability = predict([question]), predict_prob([question])
        
        print(profanity_status, profanity_probability, (int(profanity_status)))

        if int(profanity_status):
            return Response({'profanity': bool(profanity_status), 'profanity_probability': round((profanity_probability[0]),4), 'question': question})

        cleaned_garbage_data = clean_garbage(question)
        
        
        print(cleaned_garbage_data)
        
        ''' if any([True for i in question.split(' ') if i in wh_list]):
            temp_question = question[::-1].replace('?','',1)[::-1]
        else:
            temp_question = re.sub('=.*', '', question)
        '''

#        status = temp_question == cleaned_garbage_data
        final_data = add_punctuation_dots(cleaned_garbage_data)



        return Response({'profanity': bool(profanity_status), 'profanity_probability': round((profanity_probability[0]),4), 'cleaned_question':final_data})
    except:
        return Response({'error': 'error'})

import requests
import spacy
from nltk.sentiment.vader import SentimentIntensityAnalyzer

nlp = spacy.load('en_core_web_sm')
stopwords = nlp.Defaults.stop_words


def tokenize_and_remove_stopwords(question):
    cleaned_question = clean_garbage(question)
    tokenized_question = cleaned_question.split(' ')
    removed_stopwords = [i for i in tokenized_question if i not in stopwords]
    return removed_stopwords


def sentiment_analyser(data):
    sid = SentimentIntensityAnalyzer()
    scores = sid.polarity_scores(data)
    return scores




@api_view(['GET', 'POST'])
def check_the_reason_validity(request):
    try:
        correct_choice = request.data['correct_choice']
        question = request.data['question']
        
        cleaned_choice = tokenize_and_remove_stopwords(correct_choice)
        cleaned_question = tokenize_and_remove_stopwords(question)
        cleaned_question += cleaned_choice

        sentiment_question = sentiment_analyser(question)
        reason = request.data.get('reason')
        profanity_status, profanity_probability = predict([reason]), predict_prob([reason])
        print(profanity_probability, profanity_status)
        if reason.__contains__('https://') or reason.__contains__('http://') or reason.__contains__('www.') or reason.__contains__('.com/'):
            link = reason

            with open('profane_link_111.txt', 'r') as rf:
                for i in rf.readlines():
                    if str(i).strip() in link:
                        return Response({'status': 'to be banned', 'site': link})
            
            try:
                res = requests.get(link)
            except:
                return Response({'err':'Error to get the link'})

            if res.status_code != 200:
                return Response({'status_code': res.status_code, 'link':link, 'remarks': 'Unable to connect to link'})
            
            else:
                matched_number = [i for i in cleaned_question if i in res.text]
                found_weight = len(matched_number)*100/len(cleaned_question)
                return Response({
                    'status_code': res.status_code, 
                    'link':link, 
                    'matched_percentage':round(found_weight,2), 
                    'sentiment_question': sentiment_question,
                    'profanity_link':{
                        'profanity_status': profanity_status,
                        'profanity_probability': round(profanity_probability[0],4)*100
                    },
                })
        else:
            cleaned_reason = tokenize_and_remove_stopwords(reason)
            sentiment_reason = sentiment_analyser(reason)
            matched = [i for i in cleaned_reason if i in cleaned_question]
            found_weight = len(matched)*100/len(cleaned_reason)
            return Response({
                'question': question,
                'reason': reason,
                'matched_percentage':round(found_weight, 2),
                'sentiment_reason':sentiment_reason,
                'sentiment_question': sentiment_question,
                'profanity_reason':{
                    'profanity_status': profanity_status,
                    'profanity_probability': round(profanity_probability[0],4)*100
                },
            })
    except:
        return Response({'err': 'err'})




# clean csv to db

import pandas as pd
from sqlalchemy import create_engine




def prepare_csv_to_process(csv_file):
    df = pd.read_csv(csv_file)
    while df.columns[0] != 'S.N.':
        remove_column = df.columns[0]
        df.drop(columns=remove_column, inplace=True)
    
    df.columns = ['S.N.','QUESTION', 'OPTION A', 'OPTION B', 'OPTION C', 'OPTION D','CORRECT ANSWER' ]
    return df


def save_to_database(df,table_name):
    engine = create_engine('mysql+mysqlconnector://root:@localhost:3306/playground', echo=False)
    df.to_sql(table_name, con=engine, if_exists='replace', index=False)




@api_view(['GET', 'POST'])
def clean_csv_to_db(request):

    try:
        if request.data:
            file_name = request.data['file_name']
        elif request.query_params:
            file_name = request.query_params['file_name']
    except:
        return Response({'error': 'Unable to get file from url or request data'})


    try:
        df = prepare_csv_to_process(file_name)
    except:
        return Response({'error': 'Unable to read the given file'})
    
    try:
        df['QUESTION'] = df['QUESTION'].map(clean_garbage)
        df['QUESTION'] = df['QUESTION'].map(add_punctuation_dots)
    except:
        return Response({'error': 'No QUESTION field in the db for cleaning'})

    splitted_names = file_name.split('/')
    required_name = splitted_names[-1].split('.')[0]
    db_table_to_save = f'cleaned_csv_{required_name}'

    try:
        save_to_database(df, db_table_to_save)
        return Response({'response':f'Written to table {db_table_to_save} of db playground'})
    except:
        return Response({'error': 'Failed during saving to database'})



import math
import numpy as np



def randomize_clean_csv(df):

    df['QUESTION'] = df['QUESTION'].map(clean_garbage)
    df['QUESTION'] = df['QUESTION'].map(add_punctuation_dots)

    if df.shape[0]%4 == 0:
        divide_point = int(df.shape[0]/4)
    else:
        divide_point = math.floor(df.shape[0]/4)
        remaining_point = int(df.shape[0]) - (divide_point*4)

    a = ["A"]*divide_point
    b = ["B"]*divide_point
    c = ["C"]*divide_point
    d = ["D"]*(divide_point+remaining_point)

    a.extend(b)
    a.extend(c)
    a.extend(d)
    correct_ans = a

    df["CORRECT ANSWER"] = correct_ans

    dfa = np.split(df, [divide_point], axis=0)
    dfb = np.split(dfa[1], [divide_point], axis=0)
    dfc = np.split(dfb[1], [divide_point], axis=0)
    df1 = dfa[0]
    df2 = dfb[0]
    df3 = dfc[0]
    df4 = dfc[1]

    col_list = list(df2)
    col_list[2], col_list[3] = col_list[3], col_list[2]
    df2 = df2.loc[:,col_list]

    col_list = list(df3)
    col_list[2], col_list[4] = col_list[4], col_list[2]
    df3 = df3.loc[:,col_list]

    col_list = list(df4)
    col_list[2], col_list[5] = col_list[5], col_list[2]
    df4 = df4.loc[:,col_list]

    final_df = pd.DataFrame(np.concatenate( (df1.values, df2.values, df3.values, df4.values), axis=0 ))
    final_df.columns = ['S.N.','QUESTION', 'OPTION A', 'OPTION B', 'OPTION C', 'OPTION D','CORRECT ANSWER']

    df = final_df.sample(frac = 1)
    df['S.N.'] = range(1,df.shape[0]+1)

    return df




@api_view(['GET', 'POST'])
def randomize_clean_csv_to_db(request):



    try:
        if request.data:
            file_name = request.data['file_name']
        elif request.query_params:
            file_name = request.query_params['file_name']
    except:
        return Response({'error': 'Unable to get file from url or request data'})

    try:
        df = prepare_csv_to_process(file_name)
    except:
        return Response({'error': 'Unable to read the given file'})



    df = randomize_clean_csv(df)

    splitted_names = file_name.split('/')
    required_name = splitted_names[-1].split('.')[0]
    db_table_to_save = f'randomize_cleaned_{required_name}'
    
    try:
        save_to_database(df, db_table_to_save)
        return Response({'response':f'Saved to the table: {db_table_to_save}'})
    except:
        return Response({'error': 'Failed during saving to datase'})


import random
import numpy as np


@api_view(['GET', 'POST'])
def insert_options_and_randomize_clean_csv_to_db(request):
    try:
        if request.data:
            file_name = request.data['file_name']
        elif request.query_params:
            file_name = request.query_params['file_name']
    except:
        return Response({'error': 'Unable to get file from url or request data'})
    
    try:
        df = prepare_csv_to_process(file_name)
    except:
        return Response({'error': 'Unable to read the given file'})

    df.drop(columns=df.columns[3:], inplace=True)

    correct_answers = list(df['OPTION A'])
    

    wrong_options = []
    for i in range(df.shape[0]):
        sampling = random.choices(correct_answers, k=4)
        wrong_options.append(sampling)

    final_wrong_options = []
    for n, person in enumerate(correct_answers):
        if person in wrong_options[n]:
            wrong_options[n].remove(person)
            final_wrong_options.append(wrong_options[n])
        else:
            final_wrong_options.append(wrong_options[n][:-1])


    optionB = []
    optionC = []
    optionD = []
    for each in final_wrong_options:
        optionB.append(each[0])
        optionC.append(each[1])
        optionD.append(each[-1])


    df['OPTION B'] = optionB
    df['OPTION C'] = optionC
    df['OPTION D'] = optionD


    df['CORRECT ANSWER'] = np.nan

    df = randomize_clean_csv(df)

    splitted_names = file_name.split('/')
    required_name = splitted_names[-1].split('.')[0]
    db_table_to_save = f'insert_options_randomize_cleaned_{required_name}'
    
    try:
        save_to_database(df, db_table_to_save)
        return Response({'response':f'Saved to the table: {db_table_to_save}'})
    except:
        return Response({'error': 'Failed during saving to datase'})
    









    
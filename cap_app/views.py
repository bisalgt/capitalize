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
        question = request.data['question']
        
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




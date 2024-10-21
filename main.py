import json
import random

import streamlit as st
import streamlit_antd_components as sac
from streamlit_extras.bottom_container import bottom

from choices import choices 
from puzzle import puzzle
import utils 

def on_check(answer=None):
    st.session_state.answer = answer
    st.session_state.checked = True 
    st.session_state.finished = False

def on_next():
    st.session_state.answer = None
    st.session_state.checked = False 
    st.session_state.finished = True 

if __name__ == '__main__':

    st.set_page_config(page_title='Euskolingo', page_icon='🦉', layout='wide')

    if 'lesson' not in st.session_state:
        with open('lesson.json', encoding='utf-8') as f:
            st.session_state.lesson = json.load(f)

            # TODO Shuffle exercise order.
            random.shuffle(st.session_state.lesson['exercises'])
    
    if not 'exercise_index' in st.session_state:
        st.session_state.exercise_index = 0

    if not 'score' in st.session_state:
        st.session_state.score = 0.0

    pro = st.session_state.exercise_index /len(st.session_state.lesson['exercises'])

    # HEADER
    with st.container():

        # TODO Add a cancel button.

        st.progress(value=pro)

    # ACTIVITY
    if pro >= 1.0:
        st.title('¡Lección terminada!')

        st.metric(label='Puntuación', value='{0} %'.format(int(100 * st.session_state.score)))

        if st.button(label='¿Otra vez?', use_container_width=True, type='primary'):

            # Randomise exercise order.
            random.shuffle(st.session_state.lesson['exercises'])

            st.session_state.exercise_index = 0
            st.session_state.score = 0.0
            st.rerun()
    
    else:
        # SETUP
        if not 'answer' in st.session_state:
            st.session_state.answer = None 

        if not 'checked' in st.session_state:
            st.session_state.checked = False

        if not 'result' in st.session_state:
            st.session_state.result = None

        if not 'finished' in st.session_state:
            st.session_state.finished = False        

        # GUI
        st.title(':owl:')

        exercise = st.session_state.lesson['exercises'][st.session_state.exercise_index]

        if not 'choices' in st.session_state:
            if exercise['type'] == 'blankfill':
                st.session_state.choices = None 
            if exercise['type'] == 'choices':
                st.session_state.choices = list(exercise['target'])  # Ensure copy, not reference
                random.shuffle(st.session_state.choices)  # Works in place, no return.
            elif exercise['type'] == 'puzzle':
                st.session_state.choices = utils.to_list(exercise['target'])
                random.shuffle(st.session_state.choices)  # Works in place, no return.

        if exercise['type'] == 'blankfill':
            st.header('Completa la oración')
            t = exercise['text'].split(sep='_', maxsplit=1)
            st.subheader(t[0] + '...')
            answer = st.text_input(label='...', label_visibility='collapsed', disabled=st.session_state.checked)
            st.subheader('...' + t[1])
            answer = answer.strip()  # Remove trailing and ending whitespaces.

        elif exercise['type'] == 'choices':
                st.header('¿Cómo se dice...')
                st.subheader('...«{0}»?'.format(exercise['text']), anchor=False)
                answer = sac.segmented(items=st.session_state.choices, index=None,
                           label='',
                           align='center', direction='vertical', use_container_width=True,
                           color='#82c91e', bg_color=None)
                
        elif exercise['type'] == 'puzzle':
                st.header('Traduce esta oración:')
                # TODO Add distractors.
                st.subheader(exercise['text'], anchor=False)
                answer_list = sac.chip(items=st.session_state.choices, index=None,
                                       label='',
                                       align='start', radius='md', variant='outline', multiple=True,
                                       color='#82c91e')
                answer = ' '.join(answer_list)
                st.subheader(answer, anchor=False)

        with bottom():
            st.button(label='Comprobar', use_container_width=True, type='primary',
                disabled = st.session_state.checked, on_click=on_check, kwargs={'answer': answer})

            if st.session_state.checked:

                if isinstance(exercise['target'], list):
                    target = exercise['target'][0]
                elif isinstance(exercise['target'], str):
                    target = exercise['target']

                try:
                    st.session_state.result = utils.match(text=st.session_state.answer, target=target)
                except AttributeError:
                    st.session_state.result = False

                if st.session_state.result:
                    st.success('**¡Correcto!**')
                else:
                    st.error('''
                            **¡Incorrecto!**  
                            {0}'''.format(utils.to_canon(target)))

                cols = st.columns((2,1), vertical_alignment='bottom')

                with cols[0]:
                    st.empty()    
                
                with cols[1]:
                    st.button(label='Siguiente...', use_container_width=True, type='primary', on_click=on_next)

        if st.session_state.finished:
            # Update score
            if st.session_state.result == True:
                st.session_state.score += 1.0/len(st.session_state.lesson['exercises'])

            # Next exercise...
            st.session_state.exercise_index = st.session_state.exercise_index + 1

            st.session_state.answer = None 
            st.session_state.checked = False 
            st.session_state.result = None 
            st.session_state.finished = False

            del st.session_state.choices

            st.rerun()

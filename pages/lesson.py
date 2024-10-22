import json
import random

import streamlit as st
import streamlit_antd_components as sac
from streamlit_extras.bottom_container import bottom

import utils 

def on_check(answer=None):
    st.session_state.answer = answer
    st.session_state.checked = True 
    st.session_state.finished = False

def on_next():
    st.session_state.answer = None
    st.session_state.checked = False 
    st.session_state.choices = None
    st.session_state.finished = True 

def on_reset():
    st.session_state.answer = None
    st.session_state.checked = False 
    st.session_state.choices = None
    st.session_state.finished = False  

    st.session_state.lesson = None
    st.session_state.exercise_index = 0
    st.session_state.exercise_score = 0.0

if __name__ == '__main__':

    st.set_page_config(page_title='Euskolingo', page_icon='🦉', layout='wide')

    # SETUP
    if not 'answer' in st.session_state:
        st.session_state.answer = None 

    if not 'checked' in st.session_state:
        st.session_state.checked = False

    if not 'choices' in st.session_state:
        st.session_state.choices = None 

    if not 'result' in st.session_state:
        st.session_state.result = None

    if not 'finished' in st.session_state:
        st.session_state.finished = False        

    # if 'lesson' not in st.session_state or st.session_state.lesson == True:
    #     with open('lesson.json', encoding='utf-8') as f:
    #         st.session_state.lesson = json.load(f)
    #     on_reset()

    if not 'exercise_index' in st.session_state:
        st.session_state.exercise_index = 0
    
    if not 'exercise_score' in st.session_state:
        st.session_state.exercise_score = 0.0
    
    if st.session_state.lesson is not None:
        st.session_state.exercise_progress = st.session_state.exercise_index /len(st.session_state.lesson['exercises'])
    else:
        st.session_state.exercise_progress = 1.0

    # HEADER
    cols = st.columns([0.05, 0.95], vertical_alignment='center')
    with cols[0]:
        if st.button(label=':material/close:', on_click=on_reset, disabled=st.session_state.finished):
            # TODO Add a warning!
            # TODO Insert advertisment.
            st.switch_page('pages/course.py')
    with cols[1]:
        st.progress(value=st.session_state.exercise_progress)

    # ACTIVITY
    if st.session_state.exercise_progress >= 1.0:
        st.title('¡Lección terminada!')

        st.metric(label='Puntuación', value='{0} %'.format(int(100 * st.session_state.exercise_score)))

        if st.button(label='Continuar...', use_container_width=True, type='primary', on_click=on_reset):
            # st.rerun(
            # TODO Insert advertisment.
            st.switch_page('pages/course.py')
    
    else:
        # GUI
        st.title(':owl:')

        exercise = st.session_state.lesson['exercises'][st.session_state.exercise_index]

        # Set choices, if needed.
        if st.session_state.choices is None:
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
                st.session_state.exercise_score += 1.0/len(st.session_state.lesson['exercises'])

            # Next exercise...
            st.session_state.exercise_index = st.session_state.exercise_index + 1

            st.session_state.answer = None 
            st.session_state.checked = False 
            st.session_state.choices = None
            st.session_state.result = None 
            st.session_state.finished = False

            st.rerun()

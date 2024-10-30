import json
import random
import time 

from sqlalchemy import text as text
import streamlit as st
import streamlit_antd_components as sac
from streamlit_extras.bottom_container import bottom

import os
import sys
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..', 'src'))
import euskalingo.utils as utils 

def on_exercise_check(answer=None):
    st.session_state.exercise['answer'] = answer
    st.session_state.exercise['state'] = 'checked'

def on_exercise_next():
    st.session_state.exercise['answer'] = None
    st.session_state.exercise['choices'] = None
    st.session_state.exercise['state'] = 'finished'

def on_attempt_cancel():
    st.session_state.lesson['state'] = 'cancelled'

def on_attempt_finish():
    conn = st.connection(name='turso', type='sql')

    rec = conn.query('SELECT user_xp, user_gp FROM users WHERE user_name = :u LIMIT 1',
                     params={'u': st.session_state['username']}, ttl=0)
    userdata = rec.iloc[0].to_dict()

    with conn.session as session:
        session.execute(text('UPDATE users SET user_xp = :x, user_gp = :g WHERE user_name = :u'),
                        params={'x': userdata['user_xp'] + st.session_state.attempt['xp'],
                                'g': userdata['user_xp'] + st.session_state.attempt['gp'],
                                'u': st.session_state['username']})
        session.commit()

    st.session_state.lesson['state'] = 'finished'


if __name__ == '__main__':

    if not 'attempt' in st.session_state:
        st.session_state.attempt = {
            'state': 'started',  # 'completed' or 'finished'
            'exercise_index': 0,
            'progress': 0.0,
            'accuracy': 0.0,
            'time_begin': time.monotonic(),
            'time_end': None,
            'xp': 0,
            'gp': 0
        }

    # REDIRECTIONS
    if st.session_state.lesson['state'] in ['cancelled', 'finished']:
        if 'exercise' in st.session_state: del st.session_state.exercise
        # if 'attempt' in st.session_state: del st.session_state.attempt
        # if 'lesson' in st.session_state: del st.session_state.lesson

        # TODO Insert ad here
        st.switch_page('pages/course.py')

    # GUI

    # TODO Change the app name!
    st.set_page_config(page_title='Euskolingo', page_icon='🦉', layout='wide')

    # SETUP
    st.session_state.attempt['progress'] = st.session_state.attempt['exercise_index'] / len(st.session_state.lesson['exercises'])

    # ACTIVITY
    if st.session_state.attempt['progress'] >= 1.0:
        st.session_state.attempt['time_end'] = time.monotonic()
        
        # TODO Replace values with the maximum XP and GP per lesson.
        st.session_state.attempt['xp'] = int(12 * st.session_state.attempt['accuracy'])
        st.session_state.attempt['gp'] = int(3 * st.session_state.attempt['accuracy'])

        st.title('¡Lección terminada!')
        st.balloons()

        cols = st.columns(3)

        with cols[0]:
            st.metric(label='Aciertos', value='{0} %'.format(100.0 * st.session_state.attempt['accuracy']))

        with cols[1]:
            st.metric(label='Puntuación', value=st.session_state.attempt['xp'])

        with cols[2]:
            lesson_time = st.session_state.attempt['time_end'] - st.session_state.attempt['time_begin']
            st.metric(label='Tiempo', value='{0:02d}:{1:02d}'.format(int(lesson_time / 60.0), int(lesson_time % 60.0)))
        
        st.session_state.attempt['gp'] = 1
        st.info(':coin: +{0}'.format(st.session_state.attempt['gp']))

        st.button(label='Continuar...', use_container_width=True, type='primary', on_click=on_attempt_finish)
    
    else:

        if not 'exercise' in st.session_state:
            st.session_state.exercise = {
                'state': 'started',  # 'checked' or 'finished'
                'answer': None,
                'choices': None,
                'result': None
            }

        if st.session_state.exercise['state'] == 'finished':
            # Update score
            if st.session_state.exercise['result'] == True:
                st.session_state.attempt['accuracy'] += 1.0 / len(st.session_state.lesson['exercises'])

            # Next exercise...
            st.session_state.attempt['exercise_index'] += 1
            st.session_state.exercise = {
                'state': 'started',  # 'checked' or 'finished'
                'answer': None,
                'choices': None,
                'result': None
            }
            st.rerun()            

        # HEADER
        # st.info(st.session_state['username'])

        cols = st.columns([0.05, 0.95], vertical_alignment='center')
        with cols[0]:
            st.button(label=':material/close:', on_click=on_attempt_cancel)
        with cols[1]:
            st.progress(value=st.session_state.attempt['progress'])

        # GUI
        exercise = st.session_state.lesson['exercises'][st.session_state.attempt['exercise_index']]

        # Set choices, if needed.
        if st.session_state.exercise['choices'] is None:
            if exercise['type'] == 'blankfill':
                st.session_state.exercise['choices'] = None 
            if exercise['type'] == 'choices':
                st.session_state.exercise['choices'] = list(exercise['target'])  # Ensure copy, not reference
                random.shuffle(st.session_state.exercise['choices'])  # Works in place, no return.
            elif exercise['type'] == 'translation':
                st.session_state.exercise['choices'] = utils.to_list(exercise['target'])
                random.shuffle(st.session_state.exercise['choices'])  # Works in place, no return.

        if exercise['type'] == 'blankfill':
            st.header('Completa la oración')
            t = exercise['text'].split(sep='_', maxsplit=1)
            st.subheader(t[0] + '...')
            answer = st.text_input(label='...', label_visibility='collapsed', disabled=st.session_state.exercise['state'] == 'checked')
            st.subheader('...' + t[1])
            answer = answer.strip()  # Remove trailing and ending whitespaces.

        elif exercise['type'] == 'choices':
            if exercise['variant'] == 'to_target':
                st.header('¿Cómo se dice «{0}»?'.format(exercise['text']), anchor=False)
            else:
                st.header('¿Qué significa «{0}»?'.format(exercise['text']), anchor=False)

            answer = sac.segmented(items=st.session_state.exercise['choices'], index=None,
                        label='',
                        align='center', direction='vertical', use_container_width=True,
                        color='#82c91e', bg_color=None)
                
        elif exercise['type'] == 'translation':
            st.header('Traduce esta oración:')
            # TODO Add distractors.
            st.subheader(exercise['text'], anchor=False)
            answer_list = sac.chip(items=st.session_state.exercise['choices'], index=None,
                                    label='',
                                    align='start', radius='md', variant='outline', multiple=True,
                                    color='#82c91e')
            answer = ' '.join(answer_list)
            st.subheader(answer, anchor=False)
            # st.info(exercise['target'])

        # TODO Add matches exercises.

        with bottom():
            st.button(label='Comprobar', use_container_width=True, type='primary',
                disabled = st.session_state.exercise['state'] == 'checked', on_click=on_exercise_check, kwargs={'answer': answer})

            if st.session_state.exercise['state'] == 'checked':

                if isinstance(exercise['target'], list):
                    target = exercise['target'][0]
                elif isinstance(exercise['target'], str):
                    target = exercise['target']

                try:
                    st.session_state.exercise['result'] = utils.match(text=st.session_state.exercise['answer'], target=target)
                except AttributeError:
                    st.session_state.exercise['result'] = False

                if st.session_state.exercise['result']:
                    st.success('**¡Correcto!**')
                else:
                    st.error('''
                            **¡Incorrecto!**  
                            {0}'''.format(utils.to_canon(target)))

                cols = st.columns((2,1), vertical_alignment='bottom')

                with cols[0]:
                    st.empty()    
                
                with cols[1]:
                    st.button(label='Siguiente...', use_container_width=True, type='primary', on_click=on_exercise_next)

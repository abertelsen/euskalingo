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
import hitzon.exercises as exercises
import hitzon.utils as utils 

def on_exercise_check(answer=None):
    st.session_state['exercise']['answer'] = answer
    st.session_state['exercise']['state'] = 'checked'

def on_exercise_next():
    st.session_state['exercise']['answer'] = None
    st.session_state['exercise']['choices'] = None
    st.session_state['exercise']['state'] = 'finished'

def on_attempt_cancel():
    st.session_state['lesson']['state'] = 'cancelled'

def on_attempt_finish():
    conn = st.connection(name='turso', type='sql')

    rec = conn.query('SELECT xp, gp FROM users WHERE name = :u LIMIT 1',
                     params={'u': st.session_state["userdata"]["name"]}, ttl=0)
    userdata = rec.iloc[0].to_dict()

    with conn.session as session:
        session.execute(text('UPDATE users SET xp = :x, gp = :g WHERE name = :u'),
                        params={'x': userdata['xp'] + st.session_state['lesson']['attempt']['xp'],
                                'g': userdata['gp'] + st.session_state['lesson']['attempt']['gp'],
                                'u': st.session_state["userdata"]["name"]})
        session.commit()

    st.session_state['lesson']['state'] = 'finished'


# No lesson? We cannot proceed.
if not 'lesson' in st.session_state:
    st.switch_page('course.py')

if not 'attempt' in st.session_state['lesson'].keys():
    st.session_state['lesson']['attempt'] = {
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
if st.session_state['lesson']['state'] in ['cancelled', 'finished']:
    if 'exercise' in st.session_state: st.session_state['exercise'] = {}

    # TODO Insert ad here
    st.switch_page('app/course.py')

# GUI

# SETUP
st.session_state['lesson']['attempt']['progress'] = st.session_state['lesson']['attempt']['exercise_index'] / len(st.session_state['lesson']['exercises'])

# ACTIVITY
if st.session_state['lesson']['attempt']['progress'] >= 1.0:
    st.session_state['lesson']['attempt']['time_end'] = time.monotonic()
    
    # TODO Replace values with the maximum XP and GP per lesson.
    st.session_state['lesson']['attempt']['xp'] = int(st.session_state['lesson']['xp'] * st.session_state['lesson']['attempt']['accuracy'])
    st.session_state['lesson']['attempt']['gp'] = int(st.session_state['lesson']['gp'] * st.session_state['lesson']['attempt']['accuracy'])

    st.title('¡Lección terminada!')
    st.balloons()

    cols = st.columns(2)

    with cols[0]:
        st.metric(label='Aciertos', value='{0} %'.format(int(100.0 * st.session_state['lesson']['attempt']['accuracy'])))

    # with cols[1]:
    #     st.metric(label='Puntuación', value=st.session_state['lesson']['attempt']['xp'])

    with cols[1]:
        lesson_time = st.session_state['lesson']['attempt']['time_end'] - st.session_state['lesson']['attempt']['time_begin']
        st.metric(label='Tiempo', value='{0:02d}:{1:02d}'.format(int(lesson_time / 60.0), int(lesson_time % 60.0)))
    
    st.info(':dart: +{0} **xp**    :coin: +{1} **gp**'.format(st.session_state['lesson']['attempt']['xp'],
                                                                st.session_state['lesson']['attempt']['gp']))

    st.button(label='Continuar...', use_container_width=True, type='primary', on_click=on_attempt_finish)

else:

    if not 'exercise' in st.session_state:
        st.session_state['exercise'] = {
            'state': 'started',  # 'checked' or 'finished'
            'answer': None,
            'choices': None,
            'result': None
        }

    if 'state' in st.session_state['exercise'].keys() and st.session_state['exercise']['state'] == 'finished':
        # Update score
        if st.session_state['exercise']['result'] == True:
            st.session_state['lesson']['attempt']['accuracy'] += 1.0 / len(st.session_state['lesson']['exercises'])

        # Next exercise...
        st.session_state['lesson']['attempt']['exercise_index'] += 1
        st.session_state['exercise'] = {
            'state': 'started',  # 'checked' or 'finished'
            'answer': None,
            'choices': None,
            'result': None
        }
        st.rerun()            

    # HEADER
    # st.info(st.session_state["userdata"]["name"])

    cols = st.columns([0.1, 0.9], vertical_alignment='center')
    with cols[0]:
        st.button(label=':material/close:', on_click=on_attempt_cancel)
    with cols[1]:
        st.progress(value=st.session_state['lesson']['attempt']['progress'])

    # GUI
    exercise = st.session_state['lesson']['exercises'][st.session_state['lesson']['attempt']['exercise_index']]

    # Render the exercise
    if exercise['type'] == 'blankfill': 
        answer = exercises.blankfill(text=exercise['text'])

    elif exercise['type'] == 'choices': 
        answer = exercises.choices(text=exercise['text'], target=exercise['target'], variant=exercise['variant'])

    # TODO Add matches exercises.                
    # elif exercise['type'] == 'matching':
    #     answer = exercises.matching(words_left=exercise['text'], words_right=exercise['target'])

    elif exercise['type'] == 'translation':
        answer = exercises.translation(text=exercise['text'], target=exercise['target'])

    with bottom():
        st.button(label='Comprobar', use_container_width=True, type='primary',
            disabled = st.session_state['exercise']['state'] == 'checked', 
            on_click=on_exercise_check, kwargs={'answer': answer})

        if st.session_state['exercise']['state'] == 'checked':

            if isinstance(exercise['target'], list):
                target = exercise['target'][0]
            elif isinstance(exercise['target'], str):
                target = exercise['target']

            try:
                st.session_state['exercise']['result'] = utils.match(text=st.session_state['exercise']['answer'], target=target)
            except AttributeError:
                st.session_state['exercise']['result'] = False

            if st.session_state['exercise']['result']:
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

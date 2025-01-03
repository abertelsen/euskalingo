import datetime
import json
import os
import random
import time
import sys

import sqlalchemy
from sqlalchemy import text as text 
import pandas as pd
import streamlit as st
import streamlit_antd_components as sac

sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..', 'src'))
import hitzon.exercises as exercises 
import hitzon.ui as hui
import hitzon.utils as utils

def on_attempt_cancel():
    st.session_state['lesson']['state'] = 'cancelled'
    del st.session_state["exercise"]

def on_attempt_finish():
    conn = st.connection(name='turso', type='sql', ttl=30)

    rec = conn.query('SELECT xp, gp FROM users WHERE name = :u LIMIT 1',
                     params={'u': st.session_state["userdata"]["name"]}, ttl=0)
    userdata = rec.iloc[0].to_dict()

    with conn.session as session:
        session.execute(sqlalchemy.text("UPDATE users SET xp = :x, gp = :g WHERE name = :u"),
                        params={'x': userdata['xp'] + st.session_state['lesson']['attempt']['xp'],
                                'g': userdata['gp'] + st.session_state['lesson']['attempt']['gp'],
                                'u': st.session_state["userdata"]["name"]})
        session.commit()

    st.session_state['lesson']['state'] = 'finished'

def begin_lesson(unit, subunit, lesson, xp=12, gp=3):
    su = st.session_state['course']['units'][unit]['subunits'][subunit]
    types = su['types'] if 'types' in su.keys() else None 
    
    st.session_state['lesson'] = create_lesson(unit=st.session_state['course']['units'][unit],
                                                n=12,
                                                types=types,
                                                index='A1.{0:02d}.{1:02d}.{2:02d}'.format(unit, subunit, lesson),
                                                xp=xp, gp=gp)

def create_lesson(unit: dict, n: int=12, types=None, index=None, xp=12, gp=3):
    if types is None:
        types = ['blankfill', 'choices', 'translation']
    
    lesson = {
        'index': index,
        'xp': xp,
        'gp': gp,
        'exercises': [{'type': None} for x in range(n)],
        'state': 'started'
        }

    for ex in lesson['exercises']:
        ex['type'] = random.choice(types)  # TODO Add matching.

        if ex['type'] == 'blankfill':
            keyphrase = random.choice(unit['keyphrases'])  # TODO Chance probability distribution according to number of occurences and number of mistakes.

            # TODO Check that the keyphrase is well formed (i.e. has a word between "<"" and ">") AND a valid audio file is available. If not, go to translation.

            ex['text'], ex['target'] = utils.to_blankfill(keyphrase['eus'])

        elif ex['type'] == 'choices':
            keywords = random.sample(unit['keywords'], 3)
            ex['variant'] = random.choice(('to_target', 'to_source'))
            if ex['variant'] == 'to_target':
                ex['text'] = keywords[0]['spa']
                ex['target'] = [x['eus'] for x in keywords]
            else:
                ex['text'] = keywords[0]['eus']
                ex['target'] = [x['spa'] for x in keywords]

        elif ex['type'] == 'translation':
            keyphrase = random.choice(unit['keyphrases'])
            ex['variant'] = random.choice(('to_target', 'to_source'))
            
            n_distractors = random.randint(2, 4)
            distractors = random.sample(unit['keywords'], n_distractors)  # Fixed number of distractors
            
            if ex['variant'] == 'to_target':
                ex['text'] = utils.to_canon(keyphrase['spa'])
                ex['target'] = keyphrase['eus']
                ex["distractors"] = [x["eus"] for x in distractors]
            else:
                ex['text'] = utils.to_canon(keyphrase['eus'])
                ex['target'] = keyphrase['spa']
                ex["distractors"] = [x["spa"] for x in distractors]

    return lesson 

# LESSON

if 'lesson' not in st.session_state:
    st.session_state['lesson'] = {}
elif 'state' in st.session_state['lesson'].keys() and st.session_state['lesson']['state'] not in ['cancelled', 'finished']:
    
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

    # # REDIRECTIONS
    # if st.session_state['lesson']['state'] in ['cancelled', 'finished']:
    #     if 'exercise' in st.session_state: st.session_state['exercise'] = {}
    #     # TODO Insert ad here
    #     st.switch_page('app/course.py')

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

        # Debugging info can be printed here...
        # st.info(st.session_state["userdata"]["name"])

        st.markdown(":id: {0} | :dart: {1} **xp** | :coin: {2} **gp** | :adhesive_bandage: {3} **hp**".format(
            st.session_state["userdata"]["name"], st.session_state["userdata"]["xp"], st.session_state["userdata"]["gp"], st.session_state["userdata"]["hp"]))

        buttons_index = sac.buttons(items=[
            sac.ButtonsItem(label="Cancelar", icon="x-circle", color="red"),
            sac.ButtonsItem(label="Progreso: {0}%".format(int(100 * st.session_state['lesson']['attempt']['progress'])), disabled=True)
        ], use_container_width=True, index=1, variant="filled", key='progress_buttons',return_index=True)
        if buttons_index == 0:
            on_attempt_cancel()
            st.rerun()

        # GUI
        exercise = st.session_state['lesson']['exercises'][st.session_state['lesson']['attempt']['exercise_index']]
        exercises.exercise_widget(exercise)

    st.stop()

# COURSE

# Load user's progress.
if "userdata" not in st.session_state:
    conn = st.connection("turso", "sql", ttl=30)
    records = conn.query("SELECT id, name, nextlesson, xp, gp, hp, nextbandaids FROM users WHERE name = :u LIMIT 1",
                         params={"u": st.session_state["userdata"]["name"]}, ttl=30)
    st.session_state["userdata"] = records.iloc[0].to_dict()

# Are we entitled to our next package of bandaids?
if st.session_state["userdata"]["nextbandaids"] is not None and st.session_state["userdata"]["nextbandaids"] != "NULL":
    if datetime.datetime.now() >= datetime.datetime.fromisoformat(st.session_state["userdata"]["nextbandaids"]) and (st.session_state["userdata"]["hp"] < 5):
        st.session_state["userdata"]["hp"] = 5
        st.session_state["userdata"]["nextbandaids"] = None

        conn = st.connection('turso', 'sql', ttl=30)
        with conn.session as session:
            session.execute(sqlalchemy.text("UPDATE users SET hp={0}, nextbandaids=NULL WHERE name='{1}';"
                                            .format(st.session_state["userdata"]["hp"],
                                                    st.session_state["userdata"]["name"])))
            session.commit()

        st.toast(body="Vuelves a tener **5** tiritas para hacer lecciones.", icon="🩹")
        

# No band-aids? Give one for free.
if st.session_state["userdata"]["hp"] <= 0:
    st.session_state["userdata"]["hp"] = 1
    conn = st.connection('turso', 'sql', ttl=30)
    with conn.session as session:
        session.execute(sqlalchemy.text('UPDATE users SET hp= :h WHERE name= :u ;'),
                                        params={'h': st.session_state["userdata"]["hp"],
                                                'u': st.session_state["userdata"]["name"]})
        session.commit()

    st.toast(body="Has recibido 1 tirita gratis para continuar haciendo lecciones.", icon="🩹")

# Load course
if not 'course' in st.session_state or st.session_state['course'] is None:
    with open(os.path.join('data', 'course_spa-eus_A1.json'), encoding='utf-8') as f:
        st.session_state['course'] = json.load(f)

# RENDERING

if 'attempt' in st.session_state['lesson'].keys():
    
    if 'progress' in st.session_state['lesson']['attempt'].keys() \
        and st.session_state['lesson']['attempt']['progress'] >= 1.0:

        # Only update if the last exercise was completed.
        if st.session_state['lesson']['index'] >= st.session_state['userdata']['nextlesson']:

            lesson_index = st.session_state['lesson']['index'].split(sep='.', maxsplit=3)
            lesson_index[1:4] = list(map(int, lesson_index[1:4]))

            # TODO Please improve this horrible block.
            if isinstance(st.session_state['course']['units'][lesson_index[1]]['subunits'][lesson_index[2]]['lessons'], int):
                n_lessons = st.session_state['course']['units'][lesson_index[1]]['subunits'][lesson_index[2]]['lessons']
            elif isinstance(st.session_state['course']['units'][lesson_index[1]]['subunits'][lesson_index[2]]['lessons'], list):
                n_lessons = len(st.session_state['course']['units'][lesson_index[1]]['subunits'][lesson_index[2]]['lessons'])

            n_subunits = len(st.session_state['course']['units'][lesson_index[1]]['subunits'])
            n_units = len(st.session_state['course']['units'])

            next_lesson = list(lesson_index)
            next_lesson[3] = (next_lesson[3] + 1) % n_lessons
            if next_lesson[3] == 0:
                next_lesson[2] = (next_lesson[2] + 1) % n_subunits
                if next_lesson[2] == 0:
                    next_lesson[1] = (next_lesson[1] + 1) % n_units
                    if next_lesson[1] == 0:
                        # TODO Advance to the next level
                        next_lesson[0] = 'A2'

            next_lesson[1:4] = list(map(lambda x: f'{x:02d}', next_lesson[1:4]))
            st.session_state['userdata']['nextlesson'] = '.'.join(next_lesson)

            # Save to database
            conn = st.connection('turso', 'sql', ttl=30)
            with conn.session as session:
                session.execute(sqlalchemy.text('UPDATE users SET nextlesson= :n WHERE name= :u ;'),
                                params={'n': st.session_state['userdata']['nextlesson'],
                                        'u': st.session_state["userdata"]["name"]})
                session.commit()

    st.session_state['lesson']['attempt'] = {}

# GUI
next_lesson = st.session_state['userdata']['nextlesson'].split(sep='.', maxsplit=3)
next_lesson[1:4] = list(map(int, next_lesson[1:4]))

for (k_unit, u) in enumerate(st.session_state['course']['units']):

    expd = k_unit == next_lesson[1]

    with st.expander(label="{0} {1}".format(k_unit + 1, u['unit_title']), expanded=expd):

        if 'subunits' not in u.keys() or len(u['subunits']) <= 0:
            st.empty()
            continue

        for (k_subunit, su) in enumerate(u['subunits']):

            past = (k_unit < next_lesson[1]) or (k_unit == next_lesson[1] and k_subunit < next_lesson[2])
            present = k_unit == next_lesson[1] and k_subunit == next_lesson[2]
            future = (k_unit > next_lesson[1]) or (k_unit == next_lesson[1] and k_subunit > next_lesson[2])

            n_lessons = su['lessons'] if isinstance(su['lessons'], int) else len(su['lessons'])
            label = '{0}: Clase {1} de {2}'.format(su['subunit_title'], 1 + next_lesson[3], n_lessons) if present else su['subunit_title']
            bttype = 'primary' if present else 'secondary'
            disabled = future
            k_lesson = -1 if (past or future) else next_lesson[3]

            key = 'spa-eus_A1-{0:02d}-{1:02d}'.format(k_unit, k_subunit)
            kwargs={'unit': k_unit, 'subunit': k_subunit, 'lesson': k_lesson}
            # If this is an past lesson, give 3 times less xp and gp
            if k_lesson == -1:
                kwargs['xp'] = 4
                kwargs['gp'] = 1
            st.button(label=label, type=bttype, use_container_width=True, key=key, disabled=disabled, 
                        on_click=begin_lesson, kwargs=kwargs)

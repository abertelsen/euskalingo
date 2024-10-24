import json
import os
import random
import sqlalchemy

import pandas as pd
import streamlit as st

import data

def begin_lesson(unit, subunit, lesson):
    st.session_state.lesson_index = 'A1.{0:02d}.{1:02d}.{2:02d}'.format(unit, subunit, lesson)

    # TODO Generate exercises on the fly, based on the section's keywords and keyphrases.
    st.session_state.lesson = st.session_state.course['units'][unit]['subunits'][subunit]['lessons'][lesson]
    
    random.shuffle(st.session_state.lesson['exercises'])

if __name__ == '__main__':

    # REDIRECTIONS
    if not 'username' in st.session_state or st.session_state.username is None:
        st.switch_page('pages/login.py')

    if 'lesson' in st.session_state and st.session_state.lesson is not None:
        st.switch_page('pages/lesson.py')
    else:
        st.session_state.lesson = None

    # RENDERING
    st.set_page_config(page_title='Euskolingo', page_icon='🦉', layout='wide')

    # Load course
    if not 'course' in st.session_state or st.session_state.course is None:
        with open(os.path.join('data', 'course.json'), encoding='utf-8') as f:
            st.session_state.course = json.load(f)

    # Load user's progress.
    if 'userdata' not in st.session_state:
        conn = st.connection('turso', 'sql')
        records = conn.query("SELECT user_name, user_nextlesson FROM users WHERE user_name = :u LIMIT 1", 
                             params={"u": st.session_state['username']})
        st.session_state.userdata = records.iloc[0].to_dict()

    if 'exercise_progress' in st.session_state and st.session_state.exercise_progress >= 1.0:

        # Only update if the last exercise was completed.
        if st.session_state.lesson_index >= st.session_state.userdata['user_nextlesson']:

            lesson_index = st.session_state.lesson_index.split(sep='.', maxsplit=3)
            lesson_index[1:4] = list(map(int, lesson_index[1:4]))

            n_lessons = len(st.session_state.course['units'][lesson_index[1]]['subunits'][lesson_index[2]]['lessons'])
            n_subunits = len(st.session_state.course['units'][lesson_index[1]]['subunits'])
            n_units = len(st.session_state.course['units'])

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
            st.session_state.userdata['user_nextlesson'] = '.'.join(next_lesson)

            # Save to database
            conn = st.connection('turso', 'sql')
            with conn.session as session:
                session.execute(sqlalchemy.text(r"UPDATE users SET user_nextlesson='\:n' WHERE user_name='\:u';"),
                                params={'n': st.session_state.userdata['user_nextlesson'], 'u': st.session_state.userdata['user_name']})
                session.commit()

    st.session_state.exercise_progress = 0.0

    # GUI
    next_lesson = st.session_state.userdata['user_nextlesson'].split(sep='.', maxsplit=3)
    next_lesson[1:4] = list(map(int, next_lesson[1:4]))

    for (k_unit, u) in enumerate(st.session_state.course['units']):

        expd = k_unit == next_lesson[1]

        with st.expander(label=u['unit_title'], expanded=expd):
            for (k_subunit, su) in enumerate(u['subunits']):

                past = (k_unit < next_lesson[1]) or (k_unit == next_lesson[1] and k_subunit < next_lesson[2])
                present = k_unit == next_lesson[1] and k_subunit == next_lesson[2]
                future = (k_unit > next_lesson[1]) or (k_unit == next_lesson[1] and k_subunit > next_lesson[2])

                label = '{0}: Clase {1} de {2}'.format(su['subunit_title'], 1 + next_lesson[3], len(su['lessons'])) if present else su['subunit_title']
                bttype = 'primary' if present else 'secondary'
                disabled = future
                k_lesson = -1 if (past or future) else next_lesson[3]

                key = 'es-eus_A1-{0:02d}-{1:02d}'.format(k_unit, k_subunit)
                st.button(label=label, type=bttype, use_container_width=True, key=key, disabled=disabled, 
                          on_click=begin_lesson, kwargs={'unit': k_unit, 'subunit': k_subunit, 'lesson': k_lesson})

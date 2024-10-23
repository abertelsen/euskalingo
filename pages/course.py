import json
import os
import random

import pandas as pd
import streamlit as st

import data

def begin_lesson(unit, subunit, lesson):
    st.session_state.lesson_index = ['A1', unit, subunit, lesson]

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

    # TODO Replace this with user's data.
    # Load user's progress.
    if 'userdata' not in st.session_state:
        conn = data.get_connection()
        records = conn.query(f'SELECT user_name, user_nextlesson FROM users WHERE user_name="{st.session_state['username']}" LIMIT 1')
        st.session_state.userdata = records.iloc[0].to_dict()

    if 'exercise_progress' in st.session_state and st.session_state.exercise_progress >= 1.0:

        # Only update if the last exercise was completed.
        if st.session_state.lesson_index >= st.session_state.userdata['user_nextlesson']:

            n_lessons = len(st.session_state.course
                            ['units'][st.session_state.lesson_index['unit']]
                            ['subunits'][st.session_state.lesson_index['subunit']]
                            ['lessons'])
            n_subunits = len(st.session_state.course
                    ['units'][st.session_state.lesson_index['unit']]
                    ['subunits'])
            n_units = len(st.session_state.course['units'])

            next_lesson = list(st.session_state.lesson_index)

            next_lesson[3] = (next_lesson[3] + 1) % n_lessons
            if next_lesson[3] == 0:
                next_lesson[2] = (next_lesson[2] + 1) % n_subunits
                if next_lesson[2] == 0:
                    next_lesson[1] = (next_lesson[1] + 1) % n_units
                    if next_lesson[1] == 0:
                        # TODO Advance to next level
                        next_lesson[0] = 'A2'

            st.session_state.userdata['user_nextlesson'] = next_lesson

            # TODO Save to database
            conn = data.get_connection()
            records = conn.query(f'UPDATE users SET user_progress={st.session_state.userdata['user_nextlesson']} WHERE user_name="{st.session_state.userdata['user_name']}"')

    st.session_state.exercise_progress = 0.0

    # GUI
    for (k_unit, u) in enumerate(st.session_state.course['units']):

        expd = k_unit == st.session_state.userdata['user_nextlesson'][1]

        with st.expander(label=u['unit_title'], expanded=expd):
            for (k_subunit, su) in enumerate(u['subunits']):

                rr = (k_unit > st.session_state.userdata['user_nextlesson'][1]) \
                    or (k_unit == st.session_state.userdata['user_nextlesson'][1] and k_subunit > st.session_state.userdata['user_nextlesson'][2])

                key = 'es-eus_A1-{0:01d}-{1:d}'.format(k_unit, k_subunit)
                st.button(label=su['subunit_title'], type='primary', use_container_width=True, key=key, disabled=rr, 
                          on_click=begin_lesson, kwargs={'unit': k_unit, 'subunit': k_subunit, 'lesson': 0})  # TODO update lesson number.

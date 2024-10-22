import json
import random

import streamlit as st

def begin_lesson(unit, subunit, lesson):
    st.session_state.lesson_index = {'unit': unit, 'subunit': subunit, 'lesson': lesson}

    # TODO Generate exercises on the fly, based on the section's keywords and keyphrases.
    st.session_state.lesson = st.session_state.course['units'][unit]['subunits'][subunit]['lessons'][lesson]
    
    random.shuffle(st.session_state.lesson['exercises'])

if __name__ == '__main__':

    if not 'lesson' in st.session_state:
        st.session_state.lesson = None

    if st.session_state.lesson is not None:
        st.switch_page('pages/lesson.py')

    st.set_page_config(page_title='Euskolingo', page_icon='🦉', layout='wide')

    if not 'course' in st.session_state:
        with open('course.json', encoding='utf-8') as f:
            st.session_state.course = json.load(f)

    # TODO Replace this with user's data.
    if 'course_progress' not in st.session_state:
        st.session_state.course_progress = {'n_u': 0, 'n_su': 0, 'n_l': 0}

    if 'exercise_progress' in st.session_state and st.session_state.exercise_progress >= 1.0:

        # TODO Only update if the last exercise was completed.

        n_lessons = len(st.session_state.course
                        ['units'][st.session_state.lesson_index['unit']]
                        ['subunits'][st.session_state.lesson_index['subunit']]
                        ['lessons'])
        n_subunits = len(st.session_state.course
                ['units'][st.session_state.lesson_index['unit']]
                ['subunits'])
        # n_units = len(st.session_state.course['units'])

        st.session_state.course_progress['n_l'] = (st.session_state.course_progress['n_l'] + 1) % n_lessons
        if st.session_state.course_progress['n_l'] == 0:
            st.session_state.course_progress['n_su'] = (st.session_state.course_progress['n_su'] + 1) % n_subunits
            if st.session_state.course_progress['n_su'] == 0:
                st.session_state.course_progress['n_u'] = st.session_state.course_progress['n_u'] + 1

    st.session_state.exercise_progress = 0.0

    # GUI
    for (n_u, u) in enumerate(st.session_state.course['units']):

        expd = n_u == st.session_state.course_progress['n_u']

        with st.expander(label=u['unit_title'], expanded=expd):
            for (n_su, su) in enumerate(u['subunits']):

                rr = (n_u > st.session_state.course_progress['n_u']) or (n_u == st.session_state.course_progress['n_u'] and n_su > st.session_state.course_progress['n_su'])

                key = 'es-eus_section01_unit{0:01d}_subunit{1:d}'.format(n_u, n_su)
                st.button(label=su['subunit_title'], type='primary', use_container_width=True, key=key, disabled=rr, 
                          on_click=begin_lesson, kwargs={'unit': n_u, 'subunit': n_su, 'lesson': 0})

import json
import random

import streamlit as st

from choices import choices 
from puzzle import puzzle

if __name__ == '__main__':

    st.set_page_config(page_title='Euskolingo', page_icon='🦉')

    if 'lesson' not in st.session_state:
        with open('lesson.json', encoding='utf-8') as f:
            st.session_state.lesson = json.load(f)

            # Shuffle exercise order?
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

            random.shuffle(st.session_state.lesson['exercises'])

            st.session_state.exercise_index = 0
            st.session_state.score = 0.0
            st.rerun()
    
    else:
        exercise = st.session_state.lesson['exercises'][st.session_state.exercise_index]

        if exercise['type'] == 'choices': result = choices(text=exercise['text'], target=exercise['target'])
        elif exercise['type'] == 'puzzle': result = puzzle(text=exercise['text'], target=exercise['target'])
        
        if result is not None:
            # Update score
            if result == True:
                st.session_state.score += 1.0/len(st.session_state.lesson['exercises'])

            # Next exercise...
            st.session_state.exercise_index = st.session_state.exercise_index + 1
            st.rerun()

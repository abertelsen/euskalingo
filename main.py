import json

import streamlit as st

from puzzle import puzzle

if __name__ == '__main__':

    st.set_page_config(page_title='Euskolingo')

    with open('lesson.json', encoding='utf-8') as f:
        lesson = json.load(f)
    
    if not 'exercise_index' in st.session_state:
        st.session_state.exercise_index = 0

    if not 'score' in st.session_state:
        st.session_state.score = 0.0

    pro = st.session_state.exercise_index /len(lesson['exercises'])

    # HEADER
    with st.container():
        st.progress(value=pro)

    # ACTIVITY
    if pro >= 1.0:
        st.title('Lesson completed!')

        st.metric(label='Score', value='{0} %'.format(int(100 * st.session_state.score)))

        if st.button(label='Start over?', use_container_width=True, type='primary'):
            st.session_state.exercise_index = 0
            st.session_state.score = 0.0
            st.rerun()
    
    else:
        exercise = lesson['exercises'][st.session_state.exercise_index]

        result = puzzle(text=exercise['text'], target=exercise['target'])
        
        if result is not None:
            # Update score
            if result == True:
                st.session_state.score += 1.0/len(lesson['exercises'])

            # Next exercise...
            st.session_state.exercise_index = st.session_state.exercise_index + 1
            st.rerun()

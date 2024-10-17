import streamlit as st

from puzzle import puzzle

if __name__ == '__main__':

    st.set_page_config(page_title='Euskalingo')

    exercises = [['Tú no eres mi amigo', 'Zu ez zaude nire laguna'],
         ['Yo vivo en Donostia', 'Ni Donostian bizi naiz'],
         ['Ellos viven muy bien', 'Haiek oso ondo bizi dira']]
    
    if not 'exercise_index' in st.session_state:
        st.session_state.exercise_index = 0

    if not 'score' in st.session_state:
        st.session_state.score = 0.0

    pro = st.session_state.exercise_index /len(exercises)

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
        result = puzzle(text=exercises[st.session_state.exercise_index][0],
                        target=exercises[st.session_state.exercise_index][1])
        
        if result is not None:
            # Update score
            if result == True:
                st.session_state.score += 1.0/len(exercises)

            # Next exercise...
            st.session_state.exercise_index = st.session_state.exercise_index + 1
            st.rerun()

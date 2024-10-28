import streamlit as st

from euskalingo import exercises


st.set_page_config()

exercises.matching(
    ['Donostia', 'Bilbo', 'Gasteiz', 'Iruñea', 'Baiona'],
    ['San Sebastián', 'Bilbao', 'Vitoria', 'Pamplona', 'Bayona']
)

if st.session_state.finished:
    st.markdown('¡Ejercicio finalizado!')

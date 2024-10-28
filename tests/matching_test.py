import streamlit as st

import os
import sys
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..', 'src'))
import euskalingo.exercises as exercises


st.set_page_config()

exercises.matching(
    ['Donostia', 'Bilbo', 'Gasteiz', 'Iruñea', 'Baiona'],
    ['San Sebastián', 'Bilbao', 'Vitoria', 'Pamplona', 'Bayona']
)

if st.session_state.finished:
    st.markdown('¡Ejercicio finalizado!')

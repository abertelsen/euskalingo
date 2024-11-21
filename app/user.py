import os
import sys 

import streamlit as st

sys.path.insert(1, os.path.join(os.path.dirname(__file__), "..", "src"))
import hitzon.ui as hui

st.title(st.session_state["userdata"]["name"])

hui.logout_button()

with st.expander("Datos del usuario"):
    hui.userdata_form(userdata=st.session_state["userdata"])

# st.divider()
with st.expander("Cambiar contraseña"):
    hui.chagepassword_widget(userdata=st.session_state["userdata"])

# st.divider()
with st.expander("Validar correo electrónico"):
    hui.changeemail_widget(userdata=st.session_state["userdata"])

# st.divider()
with st.expander(":rotating_light: Zona peligrosa"):
    hui.deletion_widget(userdata=st.session_state["userdata"])
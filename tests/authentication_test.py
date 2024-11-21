import streamlit as st

import os
import sys
sys.path.insert(1, os.path.join(os.path.dirname(__file__), "..", "src"))
import hitzon.ui as hui

# =============================================================================


if __name__ == "__main__":
    st.set_page_config(page_title=__file__, layout="wide")

    st.session_state["userdata"] = hui.request_userdata_from_cookie()

    # st.divider()
    st.subheader("Registrar a un nuevo usuario")
    hui.registration_widget()

    # st.divider()
    if st.session_state["userdata"] is None:
        st.subheader("Login")
        hui.login_widget()
    else:
        st.empty()

    # No userdata? Do not go any further...
    if st.session_state["userdata"] is not None:
        st.markdown(":id: " + st.session_state["userdata"]["name"])

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

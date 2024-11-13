import json 

import sqlalchemy
import streamlit as st

@st.dialog("Reportar error")
def on_feedback(userdata: dict, attachment=None):

    conn = st.connection(name="turso", type="sql", ttl=30)

    options = conn.query("SELECT id, spa FROM feedback_options", index_col="id")
    feedback_option = st.radio(label="Motivo", options=options.index[::-1], format_func=lambda x: options.loc[x, "spa"])
    feedback_text = st.text_area(label="Comentarios")

    if st.button(label="Enviar", use_container_width=True, type="primary"):
        with conn.session as session:
            session.execute(sqlalchemy.text('INSERT INTO feedback (datetime, user_id, option_id, comment, attachment) VALUES (DATETIME(), :u, :o, :c, :a);'),
                            params={"u": userdata["id"], "o": feedback_option, "c": feedback_text, "a": json.dumps(attachment)})
            session.commit()

        st.rerun()

    if st.button(label="Cancelar", use_container_width=True, type="secondary"):
        st.rerun()

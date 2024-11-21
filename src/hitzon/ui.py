import json 
import uuid

import bcrypt
import extra_streamlit_components as stx
import sqlalchemy.exc
import streamlit as st
from sqlalchemy import text as sqltext
import sqlalchemy

@st.cache_resource
def get_cookiemanager():
    return stx.CookieManager()


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


# CALLBACKS ===================================================================

def on_changeemail(username: str, new_email: str):   
    conn = st.connection(name="turso", type="sql", ttl=1)
    
    with conn.session as session:
        session.execute(sqltext("UPDATE users SET email='{0}' WHERE name='{1}';".format(new_email, username)))
        session.commit()
        # TODO Check 
        # TODO 2 users cannot have the same email
        # TODO Emails must be verified
    
    return True

def on_changepasswd(username: str, old_passwd: str, new_passwd: str, rep_passwd: str):

    # TODO Should all tokens be removed after a password change?

    if new_passwd != rep_passwd:
        return False
    
    conn = st.connection(name="turso", type="sql", ttl=1)
    
    records = conn.query("SELECT password FROM Users WHERE name='{0}' LIMIT 1;".format(username))
    if len(records) == 0: return False
    b0 = str(records.iloc[0,0]).encode("utf-8")

    b1 = old_passwd.encode("utf-8")
    if bcrypt.checkpw(password=b1, hashed_password=b0):

        b2 = bcrypt.hashpw(new_passwd.encode("utf-8"), bcrypt.gensalt())
        b2 = b2.decode("utf-8")
        st.info(b2)
        with conn.session as session:
            session.execute(sqltext("UPDATE users SET password='{0}' WHERE name='{1}';".format(b2, username)))
            session.commit()
            
            st.toast(body="¡Contraseña cambiada con éxito!".format(username), icon="👍")
            return True
        
        return False

    else: return False

def on_delete(name):
    # TODO Should we ask for the password for this?

    # Logout first, delete later...
    on_logout()

    conn = st.connection(name="turso", type="sql", ttl=1)
    with conn.session as session:
        session.execute(sqltext("DELETE FROM users WHERE name='{0}';".format(name)))
        session.commit()
        return True
    
    # Normally, this line should not be reached (unless "with conn.session..." fails)
    return False 

def on_login(username, password):
    b1 = password.encode("utf-8")

    conn = st.connection(name="turso", type="sql", ttl=1)
    records = conn.query("SELECT password FROM Users WHERE name='{0}' LIMIT 1;".format(username))

    if len(records) == 0: 
        st.toast(body="El nombre de usuario **{0}** no existe.".format(username), icon="⛔")
        return False

    b0 = str(records.iloc[0,0]).encode("utf-8")
    if bcrypt.checkpw(password=b1, hashed_password=b0):
        
        st.session_state["userdata"] = request_userdata(username)

        token = str(uuid.uuid4())
        with conn.session as session:
            session.execute(sqltext("DELETE FROM tokens WHERE user_id={0};".format(st.session_state["userdata"]["id"])))
            session.execute(sqltext("INSERT INTO tokens (uuid, user_id) VALUES ('{0}', {1})".format(token, st.session_state["userdata"]["id"])))
            session.commit()

        get_cookiemanager().set(cookie="user@hitzon.streamlit.app",
                                path="/",
                                domain="hitzon.streamlit.app",
                                same_site="strict",
                                val=token)

        st.toast(body="¡Has accedido con éxito!", icon="👍")
        return True
    else:
        st.toast(body="La contraseña no es correcta", icon="⛔")
        return False 

def on_logout():
    st.session_state["userdata"] = None
    get_cookiemanager().delete("user@hitzon.streamlit.app")

def on_register(name, email, password):
    b0 = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    conn = st.connection(name="turso", type="sql", ttl=1)
    with conn.session as session:
        try:
            session.execute(sqltext("INSERT INTO users (name, email, password) VALUES ('{0}', '{1}', '{2}')".format(
                name, email, b0.decode("utf-8")
            )))
        except sqlalchemy.exc.IntegrityError as e:  # e.g. UNIQUE constraint failed: users.name
            if str(e).find("users.name") > -1:
                st.toast(body="El nombre de usuario **{0}** no está disponible: Escoge uno diferente.".format(name), icon="⛔")
            if str(e).find("users.email") > -1:
                st.toast(body="El correo electrónico **{0}** no está disponible: Escoge uno diferente.".format(email), icon="⛔")
            return False 

        session.commit()

        st.toast("¡Nuevo usuario **{0}** registrado con éxito!".format(name), icon="👍")
        return True
    
    # Normally, this line should not be reached (unless "with conn.session..." fails)
    return False 

# UI ==========================================================================

def deletion_widget(userdata: dict):
    st.button("Haz clic aquí para borrar al usuario", type="primary", use_container_width=True,
              on_click=on_delete, kwargs={"name": userdata["name"]})

def login_widget():
    username = st.text_input(label="Nombre de usuario")
    password = st.text_input(label="Contraseña", type="password")
    st.button(label="Entrar", use_container_width=True, type="primary",
              on_click=on_login, kwargs={"username": username, "password": password})

def logout_button():
    st.button(label="Logout", on_click=on_logout, use_container_width=True, type="secondary")

def changeemail_widget(userdata: dict):
    new_email = st.text_input(label="Nuevo correo electrónico")
    st.button(label="Cambiar correo electrónico", use_container_width=True, type="primary",
              on_click=on_changeemail, kwargs={"username": userdata["name"], "new_email": new_email})

def chagepassword_widget(userdata: dict):
    old_passwd = st.text_input(label="Contraseña actual", type="password")
    new_passwd = st.text_input(label="Contraseña nueva", type="password")
    rep_passwd = st.text_input(label="Repite la contraseña nueva", type="password")
    st.button(label="Cambiar contraseña", use_container_width=True, type="primary",
              on_click=on_changepasswd, kwargs={"username": userdata["name"], "old_passwd": old_passwd, "new_passwd": new_passwd, "rep_passwd": rep_passwd})

def registration_widget():
    reg_username = st.text_input(label="Nombre de usuario", key="reg_username")
    reg_email = st.text_input(label="Correo electrónico", key="reg_email")
    reg_password = st.text_input(label="Contraseña", type="password", key="reg_password")
    st.button(label="Registrarse", use_container_width=True, type="primary",
              on_click=on_register, kwargs={"name": reg_username, "email": reg_email, "password": reg_password})

# def lost_username():
#     pass

def request_userdata(username):
    conn = st.connection(name="turso", type="sql", ttl=1)
    records = conn.query("SELECT id,name,email,nextlesson,xp,gp,hp FROM Users WHERE name='{0}' LIMIT 1;".format(username))

    if len(records) < 1: return None 

    return records.iloc[0].to_dict()

def request_userdata_from_cookie(name="user@hitzon.streamlit.app"):
    cookie = get_cookiemanager().get(cookie=name)

    if cookie is None: return None

    conn = st.connection(name="turso", type="sql", ttl=1)
    token = conn.query("SELECT uuid, expiration, user_id FROM tokens WHERE uuid='{0}' LIMIT 1;".format(cookie))

    if len(token) == 0: return None
    token = token.iloc[0].to_dict()

    userdata = conn.query("SELECT id,name,email,nextlesson,xp,gp,hp FROM users WHERE id={0} LIMIT 1;".format(token["user_id"]))
    if len(userdata) == 0: return None
    userdata = userdata.iloc[0].to_dict()

    return userdata 

def userdata_form(userdata: dict):
    with st.form("userdata_form"):
        st.text_input(label="Nombre de usuario", disabled=True, value=userdata["name"])
        st.text_input(label="Correo electrónico", disabled=True, value=userdata["email"])  # TODO revalidate email
        # password = st.text_input(label="Contraseña", type="password")

        st.form_submit_button(label="Actualizar", use_container_width=True, type="primary")


import json 
import uuid

import bcrypt
import sqlalchemy.exc
import streamlit as st
import streamlit_cookies_controller as stcc
from sqlalchemy import text as sqltext
import sqlalchemy

import hitzon.email as hemail

def safeget(key, type):
    """
    Safely get objects from st.session_state.

    If key is a string:
    1. Checks that 'key' is present on st.session_state.keys()
    2. Checks that st.session_state[key] is an instance of 'type'.
    
    If so, returns st.session_state[key] or None otherwise.

    If key is a list or tuple
    1. Checks that st.session_state[key[0]][key[1]]...[key[n-2]] are all dictionaries
    2. For every k=0..n-2 st.session_state[key[0]]...[key[k]] checks that key[k+1] is present on the dictionary's keys.
    3. For the last dictionary, checks that the last key is present and its object is an instance of 'type'
    4. If all holds, returns the last object, or None otherwise.

    """
     
    if isinstance(key, list) or isinstance(key, tuple):
        d = st.session_state
        for k in range(0, len(key) - 1):
            if (key[k] in d) and (isinstance(d[key[k]], dict)):
                d = d[key[k]]
            else:
                return None 
       
        if (key[-1] in d) and (isinstance(d[key[-1]], type)):
            return d[key[-1]]
        else:
            return None 
        
    elif isinstance(key, str):      
        if key in st.session_state and isinstance(st.session_state[key], type):
            return st.session_state[key]
        else:
            return None
    else:
        return None

def notify(body, icon=None):
    st.session_state["notification"] = {"body": body, "icon": icon}


# CALLBACKS ===================================================================

def on_changeemail():

    username = safeget(["userdata", "name"], str)
    new_email = safeget("uem_email", str).strip()
    if username is None or new_email is None: return False 

    conn = st.connection(name="turso", type="sql", ttl=1)
    
    with conn.session as session:
        session.execute(sqltext("UPDATE users SET email='{0}' WHERE name='{1}';".format(new_email, username)))
        session.commit()
        # TODO Check 
        # TODO 2 users cannot have the same email
        # TODO Emails must be verified
    
    return True

def on_changepasswd():

    username = safeget(["userdata", "name"], str)
    old_passwd = safeget("upw_old_password", str).strip()
    new_passwd = safeget("upw_new_password", str).strip()
    rep_passwd = safeget("upw_rep_password", str).strip()

    # TODO Should all tokens be removed after a password change?

    if new_passwd != rep_passwd:
        return False
    
    conn = st.connection(name="turso", type="sql", ttl=1)
    
    records = conn.query("SELECT password FROM Users WHERE name='{0}' LIMIT 1;".format(username), ttl=1)
    if len(records) == 0: return False
    b0 = str(records.iloc[0,0]).encode("utf-8")

    b1 = old_passwd.encode("utf-8")
    if bcrypt.checkpw(password=b1, hashed_password=b0):

        b2 = bcrypt.hashpw(new_passwd.encode("utf-8"), bcrypt.gensalt())
        # st.info(b2)
        with conn.session as session:
            session.execute(sqltext("UPDATE users SET password='{0}' WHERE name='{1}';".format(b2.decode("utf-8"), username)))
            session.commit()
            
            notify(body="¡Contraseña cambiada con éxito!".format(username), icon="👍")
            return True
        
        return False

    else: return False

def on_delete():
    name = safeget(["userdata", "name"], str)
    if name is None: return False 

    # Logout first, delete later...
    on_logout()

    conn = st.connection(name="turso", type="sql", ttl=1)
    with conn.session as session:
        session.execute(sqltext("DELETE FROM users WHERE name='{0}';".format(name)))
        session.commit()
        return True
    
    # Normally, this line should not be reached (unless "with conn.session..." fails)
    return False 

@st.dialog("Reportar error")
def on_feedback():

    userdata = safeget("userdata", dict)
    attachment = safeget("exercise", dict)
    if userdata is None or attachment is None: return False 

    conn = st.connection(name="turso", type="sql", ttl=30)

    options = conn.query("SELECT id, spa FROM feedback_options", index_col="id", ttl=1)
    feedback_option = st.radio(label="Motivo", options=options.index[::-1], format_func=lambda x: options.loc[x, "spa"])
    feedback_text = st.text_area(label="Comentarios")

    if st.button(label="Enviar", use_container_width=True, type="primary"):
        with conn.session as session:
            session.execute(sqlalchemy.text('INSERT INTO feedback (datetime, user_id, option_id, comment, attachment) VALUES (DATETIME(), :u, :o, :c, :a);'),
                            params={"u": userdata["id"], "o": feedback_option, "c": feedback_text, "a": json.dumps(attachment)})
            session.commit()

            notify(body="Tu reporte ha sido enviado.", icon="📧")

        st.rerun()

    if st.button(label="Cancelar", use_container_width=True, type="secondary"):
        st.rerun()

def on_forgotten():
    email = safeget("fgt_email", str).strip()
    if email is None: return False

    conn = st.connection(name="turso", type="sql", ttl=1)
    records = conn.query("SELECT name FROM users WHERE email='{0}' LIMIT 1;".format(email), ttl=1)
    
    if len(records) == 0:
        notify(body="El correo electrónico **{0}** no tiene usuario asignado.".format(email), icon="⛔")
        return False
    
    # TODO Actually send an email
    hemail.send_email_forgotten_password(to=email)

def on_login():

    username = safeget("lgn_username", str).strip()
    password = safeget("lgn_password", str).strip()
    if username is None or password is None: return False 

    b1 = password.encode("utf-8")

    conn = st.connection(name="turso", type="sql", ttl=1)
    records = conn.query("SELECT password FROM users WHERE name='{0}' LIMIT 1;".format(username), ttl=1)

    if len(records) == 0: 
        notify(body="El nombre de usuario **{0}** no existe.".format(username), icon="⛔")
        return False

    b0 = str(records.iloc[0,0]).encode("utf-8")
    if bcrypt.checkpw(password=b1, hashed_password=b0):
        
        st.session_state["userdata"] = request_userdata(username)

        token = str(uuid.uuid4())
        with conn.session as session:
            session.execute(sqltext("DELETE FROM tokens WHERE user_id={0};".format(st.session_state["userdata"]["id"])))
            session.execute(sqltext("INSERT INTO tokens (uuid, user_id) VALUES ('{0}', {1})".format(token, st.session_state["userdata"]["id"])))
            session.commit()

        stcc.CookieController().set(name="user@hitzon.streamlit.app",
                                    value=token,
                                    path="/",
                                    domain=None,  # hitzon.streamlit.app?
                                    same_site="strict")

        # notify(body="¡Has accedido con éxito!", icon="👍")
        return True
    else:
        notify(body="La contraseña no es correcta", icon="⛔")
        return False 

def on_logout():
    st.session_state["userdata"] = None
    try:
        stcc.CookieController().remove("user@hitzon.streamlit.app")
    except KeyError:
        pass

def on_register():

    username = safeget("reg_username", str).strip()
    email = safeget("reg_email", str).strip()
    password = safeget("reg_password", str).strip()

    b0 = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    conn = st.connection(name="turso", type="sql", ttl=1)
    with conn.session as session:
        try:
            session.execute(sqltext("INSERT INTO users (name, email, password) VALUES ('{0}', '{1}', '{2}')".format(
                username, email, b0.decode("utf-8")
            )))
        except sqlalchemy.exc.IntegrityError as e:  # e.g. UNIQUE constraint failed: users.name
            if str(e).find("users.name") > -1:
                notify(body="El nombre de usuario **{0}** no está disponible: Escoge uno diferente.".format(username), icon="⛔")
            if str(e).find("users.email") > -1:
                notify(body="El correo electrónico **{0}** no está disponible: Escoge uno diferente.".format(email), icon="⛔")
            return False 

        session.commit()

        notify("¡Nuevo usuario **{0}** registrado con éxito!".format(username), icon="👍")
        return True
    
    # Normally, this line should not be reached (unless "with conn.session..." fails)
    return False 

# UI ==========================================================================

@st.fragment
def deletion_widget(scope="fragment"):
    if st.button("Haz clic aquí para borrar al usuario", type="primary", use_container_width=True, on_click=on_delete):
        st.rerun(scope=scope)

@st.fragment
def login_widget(scope="fragment"):
    st.text_input(label="Nombre de usuario", key="lgn_username")
    st.text_input(label="Contraseña", type="password", key="lgn_password")
    
    if st.button(label="Entrar", use_container_width=True, type="primary", 
                 disabled=any([len(st.session_state[x])==0 for x in ["lgn_username", "lgn_password"]]),
                 on_click=on_login):
        st.rerun(scope=scope)

    # st.info(st.session_state["lgn_username"])
    # st.info(st.session_state["lgn_password"])

@st.fragment
def logout_button(scope="fragment"):
    if st.button(label="Logout", on_click=on_logout, use_container_width=True, type="secondary"):
        st.rerun(scope=scope)

@st.fragment
def changeemail_widget(scope="fragment"):
    st.text_input(label="Nuevo correo electrónico", key="uem_email")
    
    if st.button(label="Cambiar correo electrónico", use_container_width=True, type="primary", 
                 disabled=len(st.session_state["uem_email"])==0,
                 on_click=on_changeemail):
        st.rerun(scope=scope)

@st.fragment
def chagepassword_widget(scope="fragment"):
    st.text_input(label="Contraseña actual", type="password", key="upw_old_password")
    st.text_input(label="Contraseña nueva", type="password", key="upw_new_password")
    st.text_input(label="Repite la contraseña nueva", type="password", key="upw_rep_password")
    
    if st.button(label="Cambiar contraseña", use_container_width=True, type="primary", 
                 disabled=any([len(st.session_state[x])==0 for x in ["upw_old_password", "upw_new_password", "upw_rep_password"]]),
                 on_click=on_changepasswd):
        st.rerun(scope=scope)

@st.fragment
def forgotten_widget(scope="fragment"):
    st.text_input(label="Correo electrónico", key="fgt_email")

    if st.button(label="Enviar", use_container_width=True, type="primary", 
                 disabled=len(st.session_state["fgt_email"])==0, on_click=on_forgotten):
        st.rerun(scope=scope)

@st.fragment
def registration_widget(scope="fragment"):
    st.text_input(label="Nombre de usuario", key="reg_username")
    st.text_input(label="Correo electrónico", key="reg_email")
    st.text_input(label="Contraseña", type="password", key="reg_password")
    
    if st.button(label="Registrarse", use_container_width=True, type="primary", key="reg_button", 
                 disabled=any([len(st.session_state[x])==0 for x in ["reg_username", "reg_email", "reg_password"]]),
                 on_click=on_register):
        st.rerun(scope=scope)


# OTHER FUNCTIONS =============================================================

def request_userdata(username):
    conn = st.connection(name="turso", type="sql", ttl=1)
    records = conn.query("SELECT id,name,email,nextlesson,xp,gp,hp,nextbandaids FROM Users WHERE name='{0}' LIMIT 1;".format(username), ttl=1)

    if len(records) < 1: return None 

    return records.iloc[0].to_dict()

def request_userdata_from_cookie(name="user@hitzon.streamlit.app"):
    cookie = stcc.CookieController().get(name=name)

    if cookie is None: return None

    conn = st.connection(name="turso", type="sql", ttl=1)
    token = conn.query("SELECT uuid, expiration, user_id FROM tokens WHERE uuid='{0}' LIMIT 1;".format(cookie), ttl=1)

    if len(token) == 0: return None
    token = token.iloc[0].to_dict()

    userdata = conn.query("SELECT id,name,email,nextlesson,xp,gp,hp,nextbandaids FROM users WHERE id={0} LIMIT 1;".format(token["user_id"]), ttl=1)
    if len(userdata) == 0: return None
    userdata = userdata.iloc[0].to_dict()

    return userdata 


def userdata_form():
    with st.form("userdata_form"):

        username = safeget(["userdata", "name"], str)
        email = safeget(["userdata", "email"], str)

        st.text_input(label="Nombre de usuario", disabled=True, value=username)
        st.text_input(label="Correo electrónico", disabled=True, value=email)  # TODO revalidate email
        # password = st.text_input(label="Contraseña", type="password")

        st.form_submit_button(label="Actualizar", use_container_width=True, type="primary")


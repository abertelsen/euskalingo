import uuid

import bcrypt
import extra_streamlit_components as stx
import streamlit as st

@st.cache_resource
def get_cookiemanager():
    return stx.CookieManager()

def login_form():
    with st.form("loginform", clear_on_submit=False, enter_to_submit=True, border=True):
        username = st.text_input(label="Nombre de usuario")
        password = st.text_input(label="Contraseña", type="password")
        st.form_submit_button(label="Entrar", use_container_width=True, type="primary", 
                              on_click=on_login, kwargs={"username": username, "password": password})

def on_login(username, password):
    b1 = password.encode("utf-8")

    conn = st.connection(name="turso", type="sql", ttl=1)
    records = conn.query("SELECT password FROM Users WHERE name='{0}' LIMIT 1;".format(username))

    if len(records) == 0: return False

    b0 = str(records.iloc[0,0]).encode("utf-8")
    if bcrypt.checkpw(password=b1, hashed_password=b0):
        st.session_state["userdata"] = request_userdata(username)

        token = str(uuid.uuid4())
        with conn.session as session:
            session.execute("INSERT INTO tokens (uuid, user_id) VALUES ('{0}', {1})".format(token, st.session_state["userdata"]["id"]))
            session.commit()

        get_cookiemanager().set(cookie="user@hitzon.streamlit.app",
                                path="/",
                                domain="hitzon.streamlit.app",
                                same_site="strict",
                                val=token)
        
        return True
    else:
        return False 

def on_logout():
    st.session_state["userdata"] = None
    get_cookiemanager().delete("user@hitzon.streamlit.app")

def on_token():
    pass 

# def lost_password():
#     email = st.text_input(label="Correo electrónico")
#     if st.button(label="Restablecer contraseña", use_container_width=True, type="primary"):
#         conn = st.connection(name="turso", type="sql", ttl=1)
#         records = conn.query("SELECT email FROM Users WHERE name='{0}' LIMIT 1;".format(username))
        
#         if len(records) == 0: return None

        

# def lost_username():
#     pass

def request_userdata(username):
    conn = st.connection(name="turso", type="sql", ttl=1)
    records = conn.query("SELECT id,name,email,nextlesson,xp,gp,hp FROM Users WHERE name='{0}' LIMIT 1;".format(username))

    if len(records) < 1: return None 

    return records.iloc[0].to_dict()

def userdata_form(userdata: dict):
    with st.form("userdata_form"):
        name = st.text_input(label="Nombre de usuario", disabled=True, value=userdata["name"])
        email = st.text_input(label="Correo electrónico", disabled=True, value=userdata["email"])  # TODO revalidate email
        # password = st.text_input(label="Contraseña", type="password")

        st.form_submit_button(label="Actualizar", use_container_width=True, type="primary")




st.set_page_config(page_title=__file__, layout="wide")

st.session_state["userdata"] = None 

cookiemanager = get_cookiemanager()
cookie = cookiemanager.get(cookie="user@hitzon.streamlit.app")
if cookie is not None:
    # TODO Use token
    pass
    # username, password = str(cookie).split(sep=":", maxsplit=1)

    # if on_login(username, password):
    #     st.session_state["userdata"] = request_userdata(username)

with st.container():
    if st.session_state["userdata"] is not None:
        # st.info(st.session_state["userdata"])
        st.markdown(":id: " + st.session_state["userdata"]["name"])
        st.button(label="Logout", on_click=on_logout)
    else:
        login_form()

# No userdata? Do not go any further...
if st.session_state["userdata"] is None:
    st.stop()

# Extra things for logged users.

st.divider()
userdata_form(userdata=st.session_state["userdata"])

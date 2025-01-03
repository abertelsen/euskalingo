import os
import sys 
# import pathlib
# import shutil

# from bs4 import BeautifulSoup
import streamlit as st

sys.path.insert(1, os.path.join(os.path.dirname(__file__), "src"))
import hitzon.ui as hui

# @st.dialog("Registro")
# def on_register():
#     hui.registration_widget()
    
#     if st.session_state["reg_button"]:
#         # hui.on_register()
#         st.rerun()

# @st.dialog("Contraseña olvidada")
# def on_forgotten():
#     pass

# def inject_ga():
#     GA_ID = "google_adsense"
#     GA_META = '<meta name="google-adsense-account" content="ca-pub-xxxxxxxxxxxx9488">'

#     # Insert the script in the head tag of the static template inside your virtual
#     index_path = pathlib.Path(st.__file__).parent / "static" / "index.html"
#     # logging.info(f'editing {index_path}')
#     soup = BeautifulSoup(index_path.read_text(), features="html.parser")
#     if not soup.find(id=GA_ID): 
#         bck_index = index_path.with_suffix('.bck')
#         if bck_index.exists():
#             shutil.copy(bck_index, index_path)  # FAIL PermissionDenied
#         else:
#             shutil.copy(index_path, bck_index)  # FAIL PermissionDenied
#         html = str(soup)
#         new_html = html.replace('<head>', '<head>\n' + GA_META)
#         index_path.write_text(new_html)  # FAIL PermissionDenied

# inject_ga()

st.set_page_config(page_title="HitzOn", layout="wide", page_icon="random")

# TODO Process query arguments here (e.g. email validation, forgotten password)

# Show pending notifications.
notification = hui.safeget("notification", dict)
if notification is not None:
    st.toast(body=st.session_state["notification"]["body"], icon=st.session_state["notification"]["icon"])
st.session_state["notification"] = None 

# No user? Redirect to login page...
st.session_state["userdata"] = hui.request_userdata_from_cookie()
if st.session_state["userdata"] is None:

    with st.container(border=True):
        logo_path = os.path.join(os.path.dirname(__file__), "data", "images", "hitzon_logo.png")
        st.image(image=logo_path)
        hui.login_widget(scope="app")

    with st.expander(label="¿Eres nuevo? ¡Regístrate aquí!"):
        hui.registration_widget(scope="app")
    # st.button(label="¿Has olvidado tu contraseña? Haz clic aquí.", use_container_width=True, type="secondary",
    #           on_click=on_forgotten)

else:
    # Navigation panel...
    
    st.logo(image=os.path.join(os.path.dirname(__file__), "data", "images", "hitzon_logo.png"), size="large")

    pages = [
        st.Page(page='app/course.py', title='Curso'),
        st.Page(page='app/ranking.py', title='Ranking'),
        st.Page(page='app/shop.py', title='Tienda'),
        st.Page(page='app/user.py', title='Perfil')
        ]
    pg = st.navigation(pages=pages)

    # ... and sidebar
    if "userdata" in st.session_state:
        with st.sidebar:
            st.markdown(':id: {0}'.format(st.session_state['userdata']['name']))
            st.markdown(':dart: {0} **xp**'.format(st.session_state['userdata']['xp']))
            st.markdown(':coin: {0} **gp**'.format(st.session_state['userdata']['gp']))
            st.markdown(':adhesive_bandage: {0} **hp**'.format(st.session_state['userdata']['hp']))

    # Finally, execute the selected page.
    pg.run()

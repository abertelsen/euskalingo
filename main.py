import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader


pages = [
    st.Page(page='app/login.py', title='Login'),
    st.Page(page='app/course.py', title='Curso'),
    st.Page(page='app/ranking.py', title='Ranking'),
    st.Page(page='app/shop.py', title='Tienda')
    ]
pg = st.navigation(pages=pages)
pg.run()

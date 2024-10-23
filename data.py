import streamlit as st

@st.cache_resource
def get_connection():
    return st.connection('turso', type='sql')

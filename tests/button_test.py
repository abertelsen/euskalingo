import streamlit as st
from streamlit_extras.stylable_container import stylable_container

st.markdown('<style>.big-font {font-size:48px !important;}</style>', unsafe_allow_html=True)

st.markdown('<span class="big-font">pepper</span>', unsafe_allow_html=True)
st.button('<span class="big-font">pepper</span>', key='big_font_button', help='Button with increased font size')

with stylable_container(key='stylable', css_styles='''
                        button {
                            font-size: 48px !important;
                        }
                        '''):
    st.button(':hot_pepper:')

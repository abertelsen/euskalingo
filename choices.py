import random

import streamlit as st
import streamlit_antd_components as sac

def choices(text, choices, key=None):
    st.header('¿Cómo se dice...')

    st.subheader('...«{0}»?'.format(text), anchor=False)

    answer = sac.segmented(items=choices, index=None,
                           label='',
                           align='center', direction='vertical', use_container_width=True,
                           color='#82c91e', bg_color=None,
                           key=key)
    
    return answer

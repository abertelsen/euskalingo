import random

import streamlit as st
import streamlit_antd_components as sac
from streamlit_extras.bottom_container import bottom

import utils

def puzzle(text, choices, key=None):
    st.header('Traduce esta oración:')

    # TODO Add distractors.

    st.subheader(text, anchor=False)

    answer_list = sac.chip(items=choices, index=None,
                           label='',
                           align='start', radius='md', variant='outline', multiple=True,
                           color='#82c91e',
                           key=key)

    answer = ' '.join(answer_list)
    st.subheader(answer, anchor=False)

    return answer

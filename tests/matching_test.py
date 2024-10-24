import random

import streamlit as st
import streamlit_antd_components as sac

def on_click():
    if st.session_state.matches[0] is not None and st.session_state.matches[1] is not None and st.session_state.result is None:
        word_left = buttons_left[st.session_state.matches[0]].label
        word_right = buttons_right[st.session_state.matches[1]].label

        if st.session_state.solution[word_left] == word_right:
            st.session_state.result = True

            st.session_state.disabled_left[st.session_state.matches[0]] = True
            st.session_state.disabled_right[st.session_state.matches[1]] = True

        else:
            st.session_state.result = False

st.set_page_config()

if 'result' not in st.session_state:
    st.session_state.result = None

if st.session_state.result is not None:
    st.toast('¡**{0}**!'.format('Correcto' if st.session_state.result else 'Incorrecto'))

    st.session_state.matches[0] = None
    st.session_state.matches[1] = None

    st.session_state.result = None

if 'solution' not in st.session_state:
    st.session_state.words_left = ['Donostia', 'Bilbo', 'Gasteiz', 'Iruñea', 'Baiona']
    st.session_state.words_right = ['San Sebastián', 'Bilbao', 'Vitoria', 'Pamplona', 'Bayona']

    st.session_state.solution = dict(zip(st.session_state.words_left, st.session_state.words_right))

    random.shuffle(st.session_state.words_left)
    random.shuffle(st.session_state.words_right)

if 'matches' not in st.session_state:
    st.session_state.matches = [None, None]

if 'disabled_left' not in st.session_state:
    st.session_state.disabled_left = [False for x in range(5)]

if 'disabled_right' not in st.session_state:
    st.session_state.disabled_right = [False for x in range(5)]

cols = st.columns(2)

buttons_left = [sac.ChipItem(label=st.session_state.words_left[x], disabled=st.session_state.disabled_left[x]) for x in range(5)]
buttons_right = [sac.ChipItem(label=st.session_state.words_right[x], disabled=st.session_state.disabled_right[x]) for x in range(5)]

for (k,v) in enumerate([buttons_left, buttons_right]):
    with cols[k]:
        st.session_state.matches[k] = sac.chip(items=v,
            index=st.session_state.matches[k],
            label='',
            color='grape',
            direction='vertical',
            return_index=True,
            multiple=False,
            radius='md',
            variant='outline',
            align='center',
            on_change=on_click,
            key='matchchips_{0}'.format('left' if k==0 else 'right'))

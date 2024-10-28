import random
import uuid

import streamlit as st
import streamlit_antd_components as sac

st.set_page_config()

if 'finished' not in st.session_state:
    st.session_state.finished = False 

if 'solution' not in st.session_state:
    st.session_state.words_left = ['Donostia', 'Bilbo', 'Gasteiz', 'Iruñea', 'Baiona']
    st.session_state.words_right = ['San Sebastián', 'Bilbao', 'Vitoria', 'Pamplona', 'Bayona']

    st.session_state.solution = dict(zip(st.session_state.words_left, st.session_state.words_right))

    random.shuffle(st.session_state.words_left)
    random.shuffle(st.session_state.words_right)

if 'result' not in st.session_state:
    st.session_state.result = None

if st.session_state.result is not None:
    st.toast('¡**{0}**!'.format('Correcto' if st.session_state.result else 'Incorrecto'))

    st.session_state.result = None

if 'matching_state' not in st.session_state:
    st.session_state.matching_state = {
        'matches': [None, None],
        'disabled': [
            [False for x in range(5)],
            [False for x in range(5)]
        ],
        'chip_keys': [str(uuid.uuid4()), str(uuid.uuid4())]
    }

cols = st.columns(2)

buttons_left = [sac.ChipItem(label=st.session_state.words_left[x], disabled=st.session_state.matching_state['disabled'][0][x]) for x in range(5)]
buttons_right = [sac.ChipItem(label=st.session_state.words_right[x], disabled=st.session_state.matching_state['disabled'][1][x]) for x in range(5)]

for (k,v) in enumerate([buttons_left, buttons_right]):
    with cols[k]:
        st.session_state.matching_state['matches'][k] = sac.chip(
            items=v,
            index=None,
            label='',
            color='grape',
            direction='vertical',
            return_index=True,
            multiple=False,
            radius='md',
            variant='outline',
            align='center',
            key=st.session_state.matching_state['chip_keys'][k]
        )

if st.session_state.matching_state['matches'][0] is not None and st.session_state.matching_state['matches'][1] is not None:
    word_left = buttons_left[st.session_state.matching_state['matches'][0]].label
    word_right = buttons_right[st.session_state.matching_state['matches'][1]].label

    if st.session_state.solution[word_left] == word_right:
        st.session_state.result = True

        st.session_state.matching_state['disabled'][0][st.session_state.matching_state['matches'][0]] = True
        st.session_state.matching_state['disabled'][1][st.session_state.matching_state['matches'][1]] = True

    else:
        st.session_state.result = False

    st.session_state.matching_state['matches'][0] = None
    st.session_state.matching_state['matches'][1] = None

    st.session_state.matching_state['chip_keys'] = [str(uuid.uuid4()), str(uuid.uuid4())]

if all(st.session_state.matching_state['disabled'][0]) and all(st.session_state.matching_state['disabled'][1]):
    st.session_state.finished = True

if st.session_state.finished:
    st.markdown('¡Ejercicio finalizado!')

import random
import uuid 

import streamlit as st
import streamlit_antd_components as sac

def blankfill(text: str):
    st.header('Completa la oración')
    t = text.split(sep='_', maxsplit=1)
    st.subheader(t[0] + '...')
    answer = st.text_input(label='...', label_visibility='collapsed', disabled=st.session_state.checked)
    st.subheader('...' + t[1])
    answer = answer.strip()  # Remove trailing and ending whitespaces.    

def choices(text: str):
    st.header('¿Cómo se dice «{0}»?'.format(text), anchor=False)
    # TODO Title should change depending on the shown word.
    answer = sac.segmented(items=st.session_state.choices, index=None,
            label='',
            align='center', direction='vertical', use_container_width=True,
            color='#82c91e', bg_color=None)

def matching(words_left, words_right):

    if 'finished' not in st.session_state:
        st.session_state.finished = False 

    if 'solution' not in st.session_state:
        st.session_state.words_left = words_left
        st.session_state.words_right = words_right

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

def translation(text: str):
    st.header('Traduce esta oración:')
    # TODO Add distractors.
    st.subheader(text, anchor=False)
    answer_list = sac.chip(items=st.session_state.choices, index=None,
                            label='',
                            align='start', radius='md', variant='outline', multiple=True,
                            color='#82c91e')
    answer = ' '.join(answer_list)
    st.subheader(answer, anchor=False)
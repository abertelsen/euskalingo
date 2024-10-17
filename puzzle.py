import random

import streamlit as st
import streamlit_antd_components as sac

@st.fragment
def puzzle_widget():

    if st.session_state.checked:
        items_top = [sac.ButtonsItem(label=x, disabled=st.session_state.checked) for x in st.session_state.puzzle_top]
        items_bottom = [sac.ButtonsItem(label=x, disabled=st.session_state.checked) for x in st.session_state.puzzle_bottom]
    else:
        items_top = st.session_state.puzzle_top
        items_bottom = st.session_state.puzzle_bottom

    with st.container(border=True):
        top_ix = sac.buttons(
            items=items_top,
            index=None,
            align='center',
            direction='horizontal',
            return_index=True,
        )

    if top_ix is not None:
        word = st.session_state.puzzle_top.pop(top_ix)
        st.session_state.puzzle_bottom.append(word)
        st.rerun(scope='fragment')

    with st.container(border=True):
        bottom_ix = sac.buttons(
            items=items_bottom,
            index=None,
            align='center',
            direction='horizontal',
            return_index=True,
        )

    if bottom_ix is not None:
        word = st.session_state.puzzle_bottom.pop(bottom_ix)
        st.session_state.puzzle_top.append(word)
        st.rerun(scope='fragment')

    if st.button(label='Check', use_container_width=True, type='primary',
        disabled = st.session_state.checked or len(st.session_state.puzzle_top) <= 0):
        st.session_state['checked'] = True 
        st.rerun(scope='app')

def puzzle(text, target):
    st.header('Translate this sentence:')

    st.markdown(text)

    # SETUP
    if not 'checked' in st.session_state:
        st.session_state.checked = False

    if not 'puzzle_top' in st.session_state:
        st.session_state.puzzle_top = []

    if not 'puzzle_bottom' in st.session_state:
        pieces = target.split()
        random.shuffle(pieces)
        st.session_state.puzzle_bottom = pieces

    puzzle_widget()

    if st.session_state.checked:

        sentence = ' '.join(st.session_state.puzzle_top)

        result = sentence == target

        cols = st.columns(2, vertical_alignment='bottom')

        with cols[0]:
            if result: st.success('Correct!')
            else: st.error('Wrong!')
        
        with cols[1]:
            if st.button(label='Next...', use_container_width=True, type='primary'):
                # CLEANUP
                del st.session_state['checked']
                del st.session_state['puzzle_top']
                del st.session_state['puzzle_bottom']

                return result

    else:
        return None

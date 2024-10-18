import random

import streamlit as st

import utils

def choices(text, target):
    st.title(':owl:')

    st.header('¿Cómo se dice...')

    # st.markdown(text)

    # SETUP
    if not 'checked' in st.session_state:
        st.session_state.checked = False

    if not 'choices' in st.session_state:
        st.session_state.choices = list(target)  # Ensure copy, not reference
        random.shuffle(st.session_state.choices)  # Works in place, no return.

    answer = st.radio(label='...{0}?'.format(text),
                      options=st.session_state.choices)
    
    st.button(label='Comprobar', use_container_width=True, type='primary',
              disabled = st.session_state.checked, on_click=utils.on_check)

    if st.session_state.checked:

        result = answer==target[0]

        if result: 
            st.success('**Correcto!**')
        else:
            st.error('''
                     **Incorrecto!**  
                     {0}'''.format(target[0]))

        cols = st.columns((2,1), vertical_alignment='bottom')

        with cols[0]:
            st.empty()    
        
        with cols[1]:
            if st.button(label='Siguiente...', use_container_width=True, type='primary'):
                # CLEANUP
                del st.session_state.checked
                del st.session_state.choices

                return result

    else:
        return None

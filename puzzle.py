import random

import streamlit as st
# import streamlit_antd_components as sac

import utils

# @st.fragment
# def puzzle_widget():
#     with st.container(border=True):
#         top_ix = sac.buttons(
#             items=[sac.ButtonsItem(label=x, color='dark', disabled=st.session_state.checked) for x in st.session_state.puzzle_top],
#             index=None,
#             align='center',
#             direction='horizontal',
#             return_index=True,
#             variant='dashed'
#         )

#     if top_ix is not None:
#         word = st.session_state.puzzle_top.pop(top_ix)
#         st.session_state.puzzle_bottom.append(word)
#         st.rerun(scope='fragment')

#     with st.container(border=True):
#         bottom_ix = sac.buttons(
#             items=[sac.ButtonsItem(label=x, color='dark', disabled=st.session_state.checked) for x in st.session_state.puzzle_bottom],
#             index=None,
#             align='center',
#             direction='horizontal',
#             return_index=True,
#             variant='dashed'
#         )

#     if bottom_ix is not None:
#         word = st.session_state.puzzle_bottom.pop(bottom_ix)
#         st.session_state.puzzle_top.append(word)
#         st.rerun(scope='fragment')

#     if st.button(label='Check', use_container_width=True, type='primary',
#         disabled = st.session_state.checked or len(st.session_state.puzzle_top) <= 0):
#         st.session_state['checked'] = True 
#         st.rerun(scope='app')

def on_check():
    st.session_state['checked'] = True 

def puzzle(text, target):
    st.title(':owl:')
    
    st.header('Traduce esta oración:')

    # st.markdown(text)

    # SETUP
    if not 'checked' in st.session_state:
        st.session_state.checked = False

    # if not 'puzzle_top' in st.session_state:
    #     st.session_state.puzzle_top = []

    # if not 'puzzle_bottom' in st.session_state:
    #     pieces = utils.to_list(target)

    # TODO Add distractors.

    if not 'pieces' in st.session_state:
        st.session_state.pieces = utils.to_list(target)
        random.shuffle(st.session_state.pieces)  # Works in place, no return.

    # puzzle_widget()
    answer_list = st.multiselect(label=text,
                                 options=st.session_state.pieces,
                                 disabled=st.session_state.checked)

    st.button(label='Check', use_container_width=True, type='primary', disabled = st.session_state.checked, on_click=on_check)

    if st.session_state.checked:

        sentence = ' '.join(answer_list)

        result = utils.match(text=sentence, target=target)

        if result: 
            st.success('**Correcto!**')
        else:
            st.error('''
                     **Incorrecto!**  
                     {0}'''.format(utils.to_canon(target)))

        cols = st.columns((2,1), vertical_alignment='bottom')

        with cols[0]:
            st.empty()    
        
        with cols[1]:
            if st.button(label='Siguiente...', use_container_width=True, type='primary'):
                # CLEANUP
                del st.session_state.checked
                del st.session_state.pieces

                return result

    else:
        return None

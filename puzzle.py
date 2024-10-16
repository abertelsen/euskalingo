import random

import streamlit as st
import streamlit_antd_components as sac

def puzzle(text, target):

    def puzzle_check():
        st.session_state['checked'] = True 

    st.text(text)

    if not 'checked' in st.session_state:
        st.session_state.checked = False

    if not 'puzzle_top' in st.session_state:
        st.session_state.puzzle_top = []

    if not 'puzzle_bottom' in st.session_state:
        pieces = target.split()
        random.shuffle(pieces)
        st.session_state.puzzle_bottom = pieces 

    with st.container(border=True):
        top_ix = sac.buttons(
            items=[sac.ButtonsItem(label=x, disabled=st.session_state.checked) for x in st.session_state.puzzle_top],
            index=None,
            align='center',
            direction='horizontal',
            return_index=True,
        )

    if top_ix is not None:
        word = st.session_state.puzzle_top.pop(top_ix)
        st.session_state.puzzle_bottom.append(word)
        st.rerun()  # TODO Would be nice to avoid using rerun().

    with st.container(border=True):
        bottom_ix = sac.buttons(
            items=[sac.ButtonsItem(label=x, disabled=st.session_state.checked) for x in st.session_state.puzzle_bottom],
            index=None,
            align='center',
            direction='horizontal',
            return_index=True,
        )

    if bottom_ix is not None:
        word = st.session_state.puzzle_bottom.pop(bottom_ix)
        st.session_state.puzzle_top.append(word)
        st.rerun()  # TODO Would be nice to avoid using rerun().

    st.button(label='Check', use_container_width=True, type='primary',
            disabled = st.session_state.checked or len(st.session_state.puzzle_top) <= 0,
            on_click=puzzle_check)

    if st.session_state.checked:

        sentence = ' '.join(st.session_state.puzzle_top)

        result = sentence == target
        if result:
            st.success('Correct!')
        else:
            st.error('Wrong!')

        # Cleanup
        del st.session_state['checked']
        del st.session_state['puzzle_top']
        del st.session_state['puzzle_bottom']

        return result

    else:
        return None


if __name__ == '__main__':

    st.set_page_config(page_title='Euskalingo')

    pages = [['Tú no eres mi amigo', 'Zu ez zaude nire laguna'],
         ['Yo vivo en Donostia', 'Ni Donostian bizi naiz'],
         ['Ellos viven muy bien', 'Haiek oso ondo bizi dira']]
    
    if not 'page_index' in st.session_state:
        st.session_state.page_index = random.randint(0, 2)
    
    result = puzzle(text=pages[st.session_state.page_index][0],
                    target=pages[st.session_state.page_index][1])

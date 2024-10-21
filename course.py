import json

import streamlit as st

if __name__ == '__main__':

    st.set_page_config(page_title='Euskolingo', page_icon='🦉', layout='wide')

    if not 'course' in st.session_state:
        with open('course.json', encoding='utf-8') as f:
            st.session_state.course = json.load(f)

    pro = {'n_u': 2, 'n_su': 3, 'n_l': 3}

    # GUI
    for (n_u, u) in enumerate(st.session_state.course['units']):

        expd = n_u == pro['n_u']

        with st.expander(label=u['unit_title'], expanded=expd):
            for (n_su, su) in enumerate(u['subunits']):

                rr = (n_u > pro['n_u']) or (n_u == pro['n_u'] and n_su > pro['n_su'])

                key = 'es-eus_section01_unit{0:01d}_subunit{1:d}'.format(n_u, n_su)
                st.button(label=su['subunit_title'], type='primary', use_container_width=True, key=key, disabled=rr)

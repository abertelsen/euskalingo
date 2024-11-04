import json 
import os 

import streamlit as st

with open(file=os.path.join('data', 'shop.json'), mode='r', encoding='utf-8') as f:
    data = json.load(f)

st.title('Tienda')

for section in data.keys():
    st.header(section)

    items = data[section]

    for i in items:
        with st.container(border=True):
            st.subheader(i['name'])
            st.markdown(i['description'])
            st.button(label='Comprar: :coin: {0} gp'.format(i['price']), use_container_width=True, type='secondary')

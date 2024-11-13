import json 
import os 

import sqlalchemy
import streamlit as st

def on_purchase(price: int, effect: str):
    stat, value = effect.split(sep="+", maxsplit=1)

    if stat not in st.session_state["userdata"].keys(): return 
    if price > st.session_state["userdata"]["gp"]: return  # Not enough money? Do nothing...

    st.session_state["userdata"]["gp"] -= price
    st.session_state["userdata"][stat] += int(value)  # TODO No limit checking!

    conn = st.connection("turso", "sql", ttl=30)
    with conn.session as session:
        session.execute(sqlalchemy.text('UPDATE users SET gp= :g, hp= :h WHERE name= :u ;'),
                                        params={'g': st.session_state["userdata"]["gp"],
                                                'h': st.session_state["userdata"]["hp"],
                                                'u': st.session_state["username"]})
        session.commit()

    if stat == "hp":
        st.toast("¡Has comprado {0} tiritas!".format(value), icon="🩹")

if "userdata" not in st.session_state:
    conn = st.connection("turso", "sql", ttl=30)
    records = conn.query("SELECT name, nextlesson, xp, gp, hp FROM users WHERE name = :u LIMIT 1",
                            params={"u": st.session_state['username']}, ttl=30)
    st.session_state["userdata"] = records.iloc[0].to_dict()

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
            st.button(label='**Comprar** :coin: {0} gp'.format(i['price']),
                      use_container_width=True,
                      type='secondary',
                      disabled=i["price"] > st.session_state["userdata"]["gp"],
                      on_click=on_purchase,
                      kwargs={"price": i['price'], "effect": i["effect"]})

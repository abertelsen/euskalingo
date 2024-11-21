import json 
import os 

import sqlalchemy
import streamlit as st

def on_promocode(code: str, userdata: dict):

    code = code.strip().replace(" ", "")  # Remove all spaces

    # st.info(code)
    # st.info(userdata)

    # Does the promocode exist? Is it valid?
    # NOTE Potential SQL injection here: restrict the promocode format (e.g. no spaces)
    conn = st.connection("turso", "sql", ttl=30)
    try:
        rec = conn.query("SELECT * FROM promocodes WHERE id='{0}' LIMIT 1".format(code))
    except:
        st.toast(body="Ha ocurrido un error al buscar el código promocional", icon="⚠️")
        return 

    if len(rec) <= 0:
        st.toast(body="No existe ese código promocional", icon="🧱")
        return 

    promo = rec.iloc[0].to_dict()

    if promo["disabled"]:
        st.toast(body="El código promocional no es válido", icon="🗑️")
        return 
    
    # TODO Check for expiration

    stat, value = promo["effect"].split(sep="+", maxsplit=1)
    
    if stat not in st.session_state["userdata"].keys(): return 
    value = int(value)

    # For now, just add things...
    st.session_state["userdata"][stat] += int(value)

    with conn.session as session:
        session.execute(sqlalchemy.text('UPDATE users SET gp= :g, hp= :h WHERE name= :u ;'),
                                        params={'g': userdata["gp"],
                                                'h': userdata["hp"],
                                                'u': userdata["name"]})
        session.commit()

    # TODO Implement one-use-per-user codes using the database.

    if stat == "gp":
        st.toast("**{0}** ¡Has conseguido {1} monedas!".format(code, value), icon="🪙")
    elif stat == "hp":
        st.toast("**{0}** ¡Has conseguido {1} tiritas!".format(code, value), icon="🩹")

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
                            params={"u": st.session_state["userdata"]["name"]}, ttl=30)
    st.session_state["userdata"] = records.iloc[0].to_dict()

with open(file=os.path.join('data', 'shop.json'), mode='r', encoding='utf-8') as f:
    data = json.load(f)

st.title('Tienda')

for section in data.keys():
    st.header(section, anchor=False)

    items = data[section]

    for i in items:
        with st.container(border=True):
            st.subheader(i['name'], anchor=False)
            st.markdown(i['description'])
            st.button(label='**Comprar** :coin: {0} gp'.format(i['price']),
                      use_container_width=True,
                      type='secondary',
                      disabled=i["price"] > st.session_state["userdata"]["gp"],
                      on_click=on_purchase,
                      kwargs={"price": i['price'], "effect": i["effect"]})

# Add the promo code section
st.header("Códigos promocionales", anchor=False)

with st.container(border=True):
    st.subheader(":admission_tickets: Código promocional")
    st.markdown("¿Tienes un código promocional? Utilízalo aquí...")
    code = st.text_input(label="Código promocional", label_visibility="collapsed")
    st.button(label="**Activar**", use_container_width=True, type="secondary", 
              on_click=on_promocode, kwargs={"code": code, "userdata": st.session_state["userdata"]})

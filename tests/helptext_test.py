import apertium
# import pyspellchecker
import streamlit as st

st.set_page_config(page_title=__file__)

text = "Zu ez zara nire laguna."

t = apertium.Translator('eus', 'spa')
text_eus = t.translate(text)

st.markdown(text, help=text_eus)
st.markdown(text_eus)

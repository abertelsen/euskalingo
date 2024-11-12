# import apertium
# import pyspellchecker
import streamlit as st

st.set_page_config(page_title=__file__)

text_eus = 'Zu ez zara nire [laguna](</> "amigo, amiga").'

help_text = '''
**Zu ez zara nire laguna**:  
Tú no eres mi amigo  
  - **zu**: tú  
  - **ez**: no  
    - **ez zara**: no eres
  - **nire**: mi  
  - **laguna**: amigo  
'''

# t = apertium.Translator('eus', 'spa')
# text_eus = t.translate(text)

# st.markdown(text, help=text_spa)
# st.markdown(text_spa)

st.markdown(text_eus, help=help_text)
st.subheader(text_eus, help=help_text)

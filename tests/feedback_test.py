import streamlit as st

import os
import sys
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..', 'src'))
from euskalingo.ui import on_feedback

st.set_page_config(page_title=__file__, layout="wide")

attachment = {
    "exercise": {
        "text": "Nor da sure aita?"
    }
}

on_feedback(userdata={"id": 0}, attachment=attachment)

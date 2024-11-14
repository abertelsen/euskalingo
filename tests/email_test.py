# import streamlit as st

import os
import sys
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..', 'src'))
from hitzon.email import send_email

text = """
This is a test email sent by the basque language course.

Do not reply to this message!
"""

send_email(receiver_email="abertelsen@gmail.com", text=text)

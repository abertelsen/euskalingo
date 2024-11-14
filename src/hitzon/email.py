import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import streamlit as st

def send_email(receiver_email, text):
    message = MIMEMultipart("alternative")
    message["Subject"] = "multipart test"
    message["From"] = st.secrets["email"]["address"]
    message["To"] = receiver_email

# Create the plain-text and HTML version of your message
#     text = """\
# Hi,
# How are you?
# Real Python has many great tutorials:
# www.realpython.com"""
#     html = """\
# <html>
#   <body>
#     <p>Hi,<br>
#        How are you?<br>
#        <a href="http://www.realpython.com">Real Python</a> 
#        has many great tutorials.
#     </p>
#   </body>
# </html>
# """

# Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    # part2 = MIMEText(html, "html")

# Add HTML/plain-text parts to MIMEMultipart message
# The email client will try to render the last part first
    message.attach(part1)
    # message.attach(part2)

# Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(st.secrets["email"]["address"], st.secrets["email"]["password"])
        server.sendmail(st.secrets["email"]["address"], receiver_email, message.as_string()
    )

def send_email_forgotten_password(to: str):
    pass

def send_email_forgotten_username(to: str):
    pass

def send_email_onboarding(to: str):
    pass

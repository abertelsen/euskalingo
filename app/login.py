import json
import os

import streamlit as st
import streamlit_authenticator as stauth
# import yaml
# from yaml.loader import SafeLoader

with open(os.path.join('data', 'users.json'), encoding='utf-8') as file:
    config = json.load(file)

# Pre-hashing all plain text passwords once
# stauth.Hasher.hash_passwords(config['credentials'])

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

try:
    authenticator.login()
except stauth.LoginError as e:
    st.error(e)

# If login is successful...
if st.session_state['authentication_status']:
    authenticator.logout()
    st.write(f'Welcome *{st.session_state["name"]}*')
    
    # UPDATE USER DETAILS
    with st.expander('Actualizar datos personales...'):
        try:
            if authenticator.update_user_details(st.session_state['username']):
                with open(os.path.join('data', 'users.json'), 'w', encoding='utf-8') as file:
                    json.dump(config, file)
                st.success('Entries updated successfully')
        except Exception as e:
            st.error(e)

    # RESET PASSWORD
    with st.expander('Cambiar contraseña...'):
        try:
            if authenticator.reset_password(st.session_state['username']):
                with open(os.path.join('data', 'users.json'), 'w', encoding='utf-8') as file:
                    json.dump(config, file)
                st.success('Password modified successfully')
        except Exception as e:
            st.error(e)

# If login fails...
elif st.session_state['authentication_status'] is False:
    st.error('Username/password is incorrect')

elif st.session_state['authentication_status'] is None:
    st.warning('Please enter your username and password')

if st.session_state['authentication_status'] in (None, False):

    # Register a new user
    with st.expander('Registrar a un nuevo usuario...'):
        try:
            email_of_registered_user, \
            username_of_registered_user, \
            name_of_registered_user = authenticator.register_user(pre_authorized=config['pre-authorized']['emails'])
            if email_of_registered_user:
                st.success('User registered successfully')
            with open(os.path.join('data', 'users.json'), 'w', encoding='utf-8') as file:
                    json.dump(config, file)
        except Exception as e:
            st.error(e)

    # FORGOTTEN PASSWORD
    with st.expander('Recuperar contraseña olvidada...'):
        try:
            username_of_forgotten_password, \
            email_of_forgotten_password, \
            new_random_password = authenticator.forgot_password()
            if username_of_forgotten_password:
                # TODO The developer should securely transfer the new password to the user.
                st.success(new_random_password)

                with open(os.path.join('data', 'users.json'), 'w', encoding='utf-8') as file:
                    json.dump(config, file)

            elif username_of_forgotten_password == False:
                st.error('Username not found')
        except Exception as e:
            st.error(e)

    # FORGOTTEN USERNAME
    with st.expander('Recuperar nombre de usuario olvidado...'):
        try:
            username_of_forgotten_username, \
            email_of_forgotten_username = authenticator.forgot_username()
            if username_of_forgotten_username:
                # TODO The developer should securely transfer the username to the user.
                st.success(username_of_forgotten_username)
            elif username_of_forgotten_username == False:
                st.error('Email not found')
        except Exception as e:
            st.error(e)

import json
import os
import time 
from typing import Dict

import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import Validator
# import yaml
# from yaml.loader import SafeLoader

# class Authenticator(stauth.Authenticate):
#     def __init__(self, credentials: dict | str, 
#                  cookie_name: str = 'some_cookie_name',
#                  cookie_key: str = 'some_key',
#                  cookie_expiry_days: float = 30,
#                  validator: Validator | None = None,
#                  auto_hash: bool = True,
#                  **kwargs: Dict[str, Any] | None):
#         super().__init__(credentials, cookie_name, cookie_key, cookie_expiry_days, validator, auto_hash, **kwargs)

#     def login(self,
#               location: str = 'main',
#               max_concurrent_users: int | None = None,
#               max_login_attempts: int | None = None,
#               fields: Dict[str, str] | None = None,
#               captcha: bool = False,
#               single_session: bool = False,
#               clear_on_submit: bool = False,
#               key: str = 'Login',
#               callback: Callable[..., Any] | None = None):
#         """
#         Renders a login widget.

#         Parameters
#         ----------
#         location: str
#             Location of the logout button i.e. main, sidebar or unrendered.
#         max_concurrent_users: int, optional
#             Maximum number of users allowed to login concurrently.
#         max_login_attempts: int, optional
#             Maximum number of failed login attempts a user can make.
#         fields: dict, optional
#             Rendered names of the fields/buttons.
#         captcha: bool
#             Captcha requirement for the login widget, 
#             True: captcha required,
#             False: captcha removed.
#         single_session: bool
#             Disables the ability for the same user to log in multiple sessions,
#             True: single session allowed,
#             False: multiple sessions allowed.
#         clear_on_submit: bool
#             Clear on submit setting, 
#             True: clears inputs on submit, 
#             False: keeps inputs on submit.
#         key: str
#             Unique key provided to widget to avoid duplicate WidgetID errors.
#         callback: callable, optional
#             Callback function that will be invoked on form submission.
#         """
#         if fields is None:
#             fields = {'Form name':'Login',
#                       'Username':'Username',
#                       'Password':'Password',
#                       'Login':'Login',
#                       'Captcha':'Captcha'}
            
#         if location not in ['main', 'sidebar', 'unrendered']:
#             raise ValueError("Location must be one of 'main' or 'sidebar' or 'unrendered'")
        
#         if not st.session_state['authentication_status']:
#             token = self.cookie_controller.get_cookie()
#             if token:
#                 self.authentication_controller.login(token=token)

#             time.sleep(params.PRE_LOGIN_SLEEP_TIME if 'login_sleep_time' not in self.attrs \
#                        else self.attrs['login_sleep_time'])
            
#             if not st.session_state['authentication_status']:
#                 if location == 'main':
#                     login_form = st.form(key=key, clear_on_submit=clear_on_submit)
#                 elif location == 'sidebar':
#                     login_form = st.sidebar.form(key=key, clear_on_submit=clear_on_submit)
#                 elif location == 'unrendered':
#                     return (st.session_state['name'], st.session_state['authentication_status'], st.session_state['username'])
                
#                 login_form.subheader('Login' if 'Form name' not in fields else fields['Form name'])
#                 username = login_form.text_input('Username' if 'Username' not in fields else fields['Username'])

#                 if 'password_hint' in st.session_state:
#                     password = login_form.text_input('Password' if 'Password' not in fields
#                                                      else fields['Password'], type='password',
#                                                      help=st.session_state['password_hint'])
#                 else:
#                     password = login_form.text_input('Password' if 'Password' not in fields else fields['Password'], type='password')

#                 entered_captcha = None
#                 if captcha:
#                     entered_captcha = login_form.text_input('Captcha' if 'Captcha' not in fields else fields['Captcha'])
#                     login_form.image(Helpers.generate_captcha('login_captcha'))

#                 if login_form.form_submit_button('Login' if 'Login' not in fields else fields['Login']):
#                     if self.authentication_controller.login(username, password,
#                                                             max_concurrent_users,
#                                                             max_login_attempts,
#                                                             single_session=single_session,
#                                                             callback=callback, captcha=captcha,
#                                                             entered_captcha=entered_captcha):
#                         self.cookie_controller.set_cookie()
#                         if self.path and self.cookie_controller.get_cookie():
#                             st.rerun()


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
    authenticator.login(
        fields={
            'Form name':'Login',
            'Username':'Nombre de usuario',
            'Password':'Contraseña',
            'Login':':material/login: Acceder',
            'Captcha':'Captcha'
        }
    )
except stauth.LoginError as e:
    st.error(e)

# If login is successful...
if st.session_state['authentication_status']:
    
    st.write(f'¡Bienvenido, *{st.session_state["name"]}*!')
    
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
            if authenticator.reset_password(
                st.session_state['username'],
                fields={'Form name':'Cambiar contraseña',
                        'Current password':'Contraseña actual',
                        'New password':'Contraseña nueva',
                        'Repeat password':'Repetir la contraseña nueva',
                        'Reset':'Cambiar'}
                ):
                with open(os.path.join('data', 'users.json'), 'w', encoding='utf-8') as file:
                    json.dump(config, file)
                st.success('¡Contraseña cambiada exitosamente!')
        except Exception as e:
            st.error(e)

    authenticator.logout(button_name=':material/logout: Salir')

# If login fails...
elif st.session_state['authentication_status'] is False:
    st.error('El nombre de usuario o la contraseña son incorrectos.')

elif st.session_state['authentication_status'] is None:
    st.warning('Por favor, indica tu nombre de usuario y contraseña.')

if st.session_state['authentication_status'] in (None, False):

    # Register a new user
    with st.expander('Registrar a un nuevo usuario...'):
        try:
            email_of_registered_user, \
            username_of_registered_user, \
            name_of_registered_user = authenticator.register_user(
                pre_authorized=config['pre-authorized']['emails']
                )
            if email_of_registered_user:
                st.success('¡Usuario registrado exitosamente!')
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
                st.error('Nombre de usuario no encontrado.')

        except Exception as e:
            st.error(e)

    # FORGOTTEN USERNAME
    with st.expander('Recuperar nombre de usuario olvidado...'):
        try:
            username_of_forgotten_username, \
            email_of_forgotten_username = authenticator.forgot_username(

            )
            if username_of_forgotten_username:
                # TODO The developer should securely transfer the username to the user.
                st.success(username_of_forgotten_username)

            elif username_of_forgotten_username == False:
                st.error('Correo electrónico no encontrado.')
        except Exception as e:
            st.error(e)

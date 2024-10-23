import streamlit as st

conn = st.connection('turso', type='sql')

records = conn.query('SELECT * FROM users')

print(records)

username = 'abertelsen'
records = conn.query(f'SELECT user_name, user_nextlesson FROM users WHERE user_name="{username}" LIMIT 1')
print(records.iloc[0].to_dict())

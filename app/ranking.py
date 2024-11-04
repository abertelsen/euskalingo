import streamlit as st
import sqlalchemy 

st.title('Ranking', anchor=False)

conn = st.connection(name='turso', type='sql', ttl=60)

data = conn.query("SELECT user_name, user_xp FROM users ORDER BY user_xp DESC LIMIT 30")

data['user_position'] = data.index + 1
data = data.set_index('user_position')

data['user_comment'] = ''
data.loc[1, 'user_comment'] = '🥇'
data.loc[2, 'user_comment'] = '🥈'
data.loc[3, 'user_comment'] = '🥉'
data.loc[5, 'user_comment'] = '⏬'

cc = {
    'user_position': st.column_config.NumberColumn(label='Posición', width='small'),
    'user_comment': st.column_config.TextColumn(label='', width='small'),
    'user_name': st.column_config.TextColumn(label='ID', width='large'),
    'user_xp': st.column_config.NumberColumn(label='Puntuación')
    }
co = ['user_comment', 'user_name', 'user_xp']

st.dataframe(data=data, use_container_width=True, column_config=cc, column_order=co)

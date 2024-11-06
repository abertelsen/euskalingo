import streamlit as st

conn = st.connection(name='turso', type='sql', ttl=0)

data = conn.query("SELECT name, xp FROM users ORDER BY xp DESC LIMIT 30")

data['position'] = data.index + 1
data = data.set_index('position')

for r in data.iloc:
    print(r.to_dict())

# data['comment'] = ''
# data.loc[1, 'comment'] = '🥇'
# data.loc[2, 'comment'] = '🥈'
# data.loc[3, 'comment'] = '🥉'
# data.loc[5, 'comment'] = '⏬'

# cc = {
#     'position': st.column_config.NumberColumn(label='Posición', width='small'),
#     'comment': st.column_config.TextColumn(label='', width='small'),
#     'name': st.column_config.TextColumn(label='ID', width='large'),
#     'xp': st.column_config.NumberColumn(label='Puntuación')
#     }
# co = ['comment', 'name', 'xp']

# st.dataframe(data=data, use_container_width=True, column_config=cc, column_order=co)

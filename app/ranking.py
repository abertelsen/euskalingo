import streamlit as st
import sqlalchemy 

st.title('Ranking', anchor=False)

conn = st.connection(name='turso', type='sql', ttl=30)

data = conn.query("SELECT name, xp FROM users ORDER BY xp DESC LIMIT 30", ttl=30)

with st.container(border=True):
    for i, r in enumerate(data.iloc):
        p = i+1
        r = r.to_dict()
       
        if p==1:
            p_str = "🥇"
        elif p==2:
            p_str = "🥈"
        elif p==3:
            p_str = "🥉"
        else:
            p_str = "{0}.".format(p)

        st.metric(label="position", value="{0} {1}".format(p_str, r["name"]), delta="🎯 {0} xp".format(r["xp"]), label_visibility="collapsed")

        # cols = st.columns([.7, .3], vertical_alignment="bottom")
        # with cols[0]:
        #     st.subheader(body="{0} {1}".format(p_str, r["name"]), anchor=False, divider=True)
        # with cols[1]:
        #     st.markdown(body="#### :dart: {0} xp".format(r["xp"]))

import streamlit as st
import streamlit_antd_components as sac

st.set_page_config(page_title="Columns test")

k_min = 2
k_max = 6

for k in range(k_min,k_max):
    st.write("{0} columns".format(k))

    cols = st.columns(k)

    for c in range(k):
        with cols[c]:
            st.button(label="group {0}, column {1}".format(k,c), use_container_width=True)

for k in range(k_min,k_max):
    st.write("{0} buttons".format(k))
    sac.buttons(items=["group {0}, button {1}".format(k,x) for x in range(k)], use_container_width=True)

for k in range(k_min,k_max):
    st.write("{0} segments".format(k))
    sac.segmented(items=["group {0}, segment {1}".format(k,x) for x in range(k)], use_container_width=True)
    
st.divider()

for v in ["dashed","filled", "link", "outline", "text"]:
    st.write("Variant: {0}".format(v))

    sac.buttons(items=[
        sac.ButtonsItem(label='Cancel'),
        sac.ButtonsItem(label='Progress', disabled=True)
    ], use_container_width=True, index=None, variant=v)

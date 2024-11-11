import streamlit as st
import streamlit.components.v1 as stc

st.title("Advertisment test")

stc.html('''
         <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5145093140039488" crossorigin="anonymous"></script>
         <!-- display_ad --><ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-5145093140039488" data-ad-slot="7872550965" data-ad-format="auto" data-full-width-responsive="true"></ins>
         <script>(adsbygoogle = window.adsbygoogle || []).push(\{\});</script>
         ''')

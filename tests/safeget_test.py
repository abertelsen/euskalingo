import os
import sys

import streamlit as st

sys.path.insert(1, os.path.join(os.path.dirname(__file__), "..", "src"))
import hitzon.ui as hui

KEY_NOT = "not-existing-key"
assert(hui.safeget("not-existing-key", str) is None)

KEY_YES = "existing-key"
st.session_state[KEY_YES] =  "existing-str"
assert(hui.safeget(KEY_YES, str) is not None)
assert(isinstance(hui.safeget(KEY_YES, str), str))

KEY_0 = "existing-dict"
st.session_state[KEY_0] = {"a": 1, "b": "letter-b", "c": {"d": 0}}
assert(hui.safeget(KEY_0, str) is None)
assert(isinstance(hui.safeget(KEY_0, dict), dict))
assert(hui.safeget([KEY_NOT, 'a'], int) is None)
assert(hui.safeget((KEY_NOT, 'a'), int) is None)
assert(isinstance(hui.safeget((KEY_0, 'a'), int), int))
assert(isinstance(hui.safeget([KEY_0, 'a'], int), int))
assert(hui.safeget([KEY_0, 'z'], int) is None)
assert(hui.safeget((KEY_0, 'z'), int) is None)
assert(isinstance(hui.safeget([KEY_0, 'b'], str), str))

assert(isinstance(hui.safeget([KEY_0, "c", "d"], int), int))
assert(hui.safeget([KEY_0, "c", "d"], str) is None)  # Wrong type
assert(hui.safeget([KEY_0, "c", "z"], int) is None)  # Unexisting key

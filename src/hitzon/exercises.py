import datetime
import os 
import random
import uuid 

import sqlalchemy
import streamlit as st
import streamlit_antd_components as sac
from streamlit_extras.bottom_container import bottom

import hitzon.ui as hui
import hitzon.utils as utils

# CALLBACKS

def on_exercise_check():
    # st.session_state['exercise']['answer'] = answer
    st.session_state['exercise']['state'] = 'checked'

def on_exercise_next():
    st.session_state['exercise']['answer'] = ""  # Do not set None: use a blank str instead.
    st.session_state['exercise']['choices'] = None
    st.session_state['exercise']['state'] = 'finished'



@st.dialog("¡No tienes tiritas!")
def on_zero_hp():
    st.markdown('''
¡No te quedan tiritas! No puedes hacer lecciones hasta que consigas más.
''')
    
    bandaids_price = 500
    if st.button(label=":adhesive_bandage: Comprar tiritas (:coin: {0})".format(bandaids_price),
                 use_container_width=True,
                 type="primary",
                 disabled=st.session_state["userdata"]["gp"] < bandaids_price):
        st.session_state["userdata"]["gp"] = max(st.session_state["userdata"]["gp"] - bandaids_price, 0)
        st.session_state["userdata"]["hp"] = 5

        conn = st.connection(name="turso", type="sql", ttl=30)
        with conn.session as session:
            session.execute(sqlalchemy.text('UPDATE users SET hp = :h, gp = :g WHERE name = :u'),
                                            params={'h': st.session_state["userdata"]['hp'],
                                                    'g': st.session_state["userdata"]['gp'],
                                                    'u': st.session_state["userdata"]["name"]})
            session.commit()

        st.rerun()

    if st.button(label="Cancelar", use_container_width=True, type="secondary"):
        # on_attempt_cancel()
        st.rerun()


@st.fragment
def exercise_widget(exercise: dict):

    if st.session_state["exercise"]["state"] == "finished":
        st.rerun(scope="app")

    # Render the exercise
    if exercise["type"] == "blankfill": 
        blankfill(text=exercise["text"], target=exercise["target"])

    elif exercise["type"] == "choices": 
        choices(text=exercise["text"], target=exercise["target"], variant=exercise["variant"])

    # TODO Add matches exercises.                
    # elif exercise["type"] == "matching":
    #     matching(words_left=exercise["text"], words_right=exercise["target"])

    elif exercise["type"] == "translation":

        if ("distractors" not in exercise) or (exercise["distractors"] is None) or (not isinstance(exercise["distractors"], list)):
            exercise["distractors"] = []

        translation(text=exercise["text"], target=exercise["target"], distractors=exercise["distractors"])

    if st.session_state["exercise"]["state"] == "checked":

        if isinstance(exercise["target"], list):
            target = exercise["target"][0]
        elif isinstance(exercise["target"], str):
            target = exercise["target"]

        try:
            st.session_state["exercise"]["result"] = utils.match(text=st.session_state["exercise"]["answer"], target=target)
        except AttributeError:
            st.session_state["exercise"]["result"] = False

        if st.session_state["exercise"]["result"]:
            st.success("""**¡Correcto!**  
            {0}""".format(utils.to_canon(target)))
        else:
            st.error("""
            **¡Incorrecto!**  
            {0}""".format(utils.to_canon(target)))

            st.session_state["userdata"]["hp"] = max(st.session_state["userdata"]["hp"] - 1, 0)  # Do not go < 0
            if (st.session_state["userdata"]["nextbandaids"] is None) and (st.session_state["userdata"]["hp"] < 5):
                st.session_state["userdata"]["nextbandaids"] = str(datetime.datetime.now() + datetime.timedelta(hours=8))

            conn = st.connection(name="turso", type="sql", ttl=1)
            with conn.session as session:
                session.execute(sqlalchemy.text("UPDATE users SET hp={0}, nextbandaids='{1}' WHERE name='{2}' ;".format(
                    st.session_state["userdata"]["hp"],
                    st.session_state["userdata"]["nextbandaids"] if st.session_state["userdata"]["nextbandaids"] is not None else "NULL",
                    st.session_state["userdata"]["name"])))
                session.commit()

            # React if the user loses all his band-aids.
            if st.session_state["userdata"]["hp"] <= 0:
                on_zero_hp()

        cols = st.columns(3, vertical_alignment="bottom")

        with cols[0]:
            st.button(label="Reportar error...", use_container_width=True, type="secondary", on_click=hui.on_feedback)

        # TODO Include additional information in the attachment: question"s text and index are missing.

        with cols[1]:
            st.empty()

        with cols[2]:
            st.button(label="Siguiente...", use_container_width=True, type="primary", on_click=on_exercise_next,
                      disabled=st.session_state["userdata"]["hp"] <= 0)

    else:
        # st.info(st.session_state["exercise"]["state"])
        # st.info(st.session_state["exercise"]["answer"])

        st.button(label="Comprobar", use_container_width=True, type="primary",
                    disabled = (st.session_state["exercise"]["state"] == "checked") or st.session_state["exercise"]["answer"] is None or len(st.session_state["exercise"]["answer"])==0, 
                    on_click=on_exercise_check)

def blankfill(text: str, target: str):

    # st.info(text)
    st.session_state["exercise"]["choices"] = None

    if hui.safeget(["exercise", "answer"], str) is None:
        st.session_state["exercise"]["answer"] = ""

    if hui.safeget(["exercise", "text"], str) is None:
        st.session_state["exercise"]["text"] = text

    if hui.safeget(["exercise", "target"], str) is None:
        st.session_state["exercise"]["target"] = target

    st.header("Completa la oración")

    # TODO Get the audio files from a storage server.
    audio_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "audio_spa-eus_A1")
    audio_name = utils.to_filename(st.session_state["exercise"]["text"].replace("_", st.session_state["exercise"]["target"]))
    audio_path = os.path.join(audio_dir, audio_name + ".wav")

    # st.info(audio_path)

    if os.path.exists(audio_path):
        st.audio(data=audio_path, loop=False, autoplay=True)

    # st.info(st.session_state["exercise"]["text"])

    t = st.session_state["exercise"]["text"].split(sep="_", maxsplit=1)
    if len(t[0].strip()) > 0:
        st.subheader(t[0] + "...")
    st.text_input(label="...", label_visibility="collapsed",
                  disabled=st.session_state["exercise"]["state"] == "checked",
                  key="blankfill_text_input")
    if len(t[1].strip()) > 0:
        st.subheader("... " + t[1])

    st.session_state["exercise"]["answer"] = st.session_state["blankfill_text_input"].strip()  # Remove trailing and ending whitespaces.

def choices(text: str, target: list, variant: str):

    if hui.safeget(["exercise", "choices"], list) is None:
        st.session_state["exercise"]["choices"] = list(target)  # Ensure copy, not reference
        random.shuffle(st.session_state["exercise"]["choices"])  # Works in place, no return.

    helptext = utils.create_helptext(text, target[0])

    if variant == "to_target":
        st.header("¿Cómo se dice «{0}»?".format(text), anchor=False, help=helptext)
    else:
        st.header("¿Qué significa «{0}»?".format(text), anchor=False, help=helptext)

    st.session_state["exercise"]["answer"] = sac.segmented(items=st.session_state["exercise"]["choices"], index=None,
                                                           label="",
                                                           align="center", direction="vertical", use_container_width=True,
                                                           color="lightsalmon", bg_color="white")

def matching(words_left, words_right):

    if "finished" not in st.session_state:
        st.session_state.finished = False 

    if "solution" not in st.session_state:
        st.session_state.words_left = words_left
        st.session_state.words_right = words_right

        st.session_state.solution = dict(zip(st.session_state.words_left, st.session_state.words_right))

        random.shuffle(st.session_state.words_left)
        random.shuffle(st.session_state.words_right)

    if "result" not in st.session_state:
        st.session_state.result = None

    if st.session_state.result is not None:
        st.toast("¡**{0}**!".format("Correcto" if st.session_state.result else "Incorrecto"))

        st.session_state.result = None

    if "matching_state" not in st.session_state:
        st.session_state.matching_state = {
            "matches": [None, None],
            "disabled": [
                [False for x in range(5)],
                [False for x in range(5)]
            ],
            "chip_keys": [str(uuid.uuid4()), str(uuid.uuid4())]
        }

    cols = st.columns(2)

    buttons_left = [sac.ChipItem(label=st.session_state.words_left[x], disabled=st.session_state.matching_state["disabled"][0][x]) for x in range(5)]
    buttons_right = [sac.ChipItem(label=st.session_state.words_right[x], disabled=st.session_state.matching_state["disabled"][1][x]) for x in range(5)]

    for (k,v) in enumerate([buttons_left, buttons_right]):
        with cols[k]:
            st.session_state.matching_state["matches"][k] = sac.chip(
                items=v,
                index=None,
                label="",
                color="grape",
                direction="vertical",
                return_index=True,
                multiple=False,
                radius="md",
                variant="outline",
                align="center",
                key=st.session_state.matching_state["chip_keys"][k]
            )

    if st.session_state.matching_state["matches"][0] is not None and st.session_state.matching_state["matches"][1] is not None:
        word_left = buttons_left[st.session_state.matching_state["matches"][0]].label
        word_right = buttons_right[st.session_state.matching_state["matches"][1]].label

        if st.session_state.solution[word_left] == word_right:
            st.session_state.result = True

            st.session_state.matching_state["disabled"][0][st.session_state.matching_state["matches"][0]] = True
            st.session_state.matching_state["disabled"][1][st.session_state.matching_state["matches"][1]] = True

        else:
            st.session_state.result = False

        st.session_state.matching_state["matches"][0] = None
        st.session_state.matching_state["matches"][1] = None

        st.session_state.matching_state["chip_keys"] = [str(uuid.uuid4()), str(uuid.uuid4())]

    if all(st.session_state.matching_state["disabled"][0]) and all(st.session_state.matching_state["disabled"][1]):
        st.session_state.finished = True

def translation(text: str, target: str, distractors=[]):

    # TODO Implement variants with audio only.

    if hui.safeget(["exercise", "choices"], list) is None:
        st.session_state["exercise"]["choices"] = utils.to_list(target) + distractors
        random.shuffle(st.session_state["exercise"]["choices"])  # Works in place, no return.

    st.header("Traduce esta oración:", anchor=False)
    st.subheader(text, anchor=False, help=utils.create_helptext(text, target))

    # TODO Get the audio files from a storage server.
    audio_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "audio_spa-eus_A1")
    audio_name = utils.to_filename(text)
    audio_path = os.path.join(audio_dir, audio_name + ".wav")
    if os.path.exists(audio_path):
        st.audio(data=audio_path, loop=False, autoplay=True)

    # TODO Add distractors.
    answer_list = sac.chip(items=st.session_state["exercise"]["choices"], index=None,
                            label="",
                            align="start", radius="md", variant="outline", multiple=True,
                            color="lightsalmon")
    # Other color #9ab9bf
    st.session_state["exercise"]["answer"] = " ".join(answer_list)
    st.subheader(st.session_state["exercise"]["answer"], anchor=False)

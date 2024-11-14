# Create audio files for all units' keyphrases.

# TODO Make dependencies optional: transformers, simpleaudio, scipy

import json
import os
# import time

import numpy as np
# import simpleaudio as sa
import scipy
from transformers import pipeline


# import os
import sys
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..', 'src'))
import hitzon.utils as utils

overwrite = False

pipe = pipeline(task="text-to-speech", model="facebook/mms-tts-eus")
# pipe.model.config.num_speakers is 1

with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'course_spa-eus_A1.json'), encoding="utf-8") as file:
    data = json.load(file)

out_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'audio_spa-eus_A1')

for u in data["units"]:

    if "keyphrases" not in u.keys(): continue

    for kph in u["keyphrases"]:
        kph = utils.to_canon(kph["eus"])
        print(kph)

        out_name = utils.to_filename(kph)
        out_path = os.path.join(out_dir, out_name + ".wav")

        if overwrite or (not os.path.exists(out_path)):
            # If multiple speakers are supported, they should be set like this (but I am not sure)
            # forward_params={"speaker_id": 0}
            out = pipe(kph)

            # sa.play_buffer(audio_data=out["audio"], num_channels=1, bytes_per_sample=4, sample_rate=out["sampling_rate"])
            # time.sleep(5)

            scipy.io.wavfile.write(filename=out_path, rate=out["sampling_rate"], data=out["audio"].T)

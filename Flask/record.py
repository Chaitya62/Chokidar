import speech_recognition as sr
import threading
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import json

mic = sr.Microphone()
r = sr.Recognizer()
print(sr.Microphone.list_microphone_names())

def recognize_google(audio_data, key=None, language="en-US", pfilter=0, show_all=False):

        flac_data = audio_data.get_flac_data(
            convert_rate=None if audio_data.sample_rate >= 8000 else 8000,  # audio samples must be at least 8 kHz
            convert_width=2  # audio samples must be 16-bit
        )
        if key is None: key = "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw"
        url = "http://www.google.com/speech-api/v2/recognize?{}".format(urlencode({
            "client": "chromium",
            "lang": language,
            "key": key,
            "pFilter": pfilter
        }))
        request = Request(url, data=flac_data, headers={"Content-Type": "audio/x-flac; rate={}".format(audio_data.sample_rate)})

        # obtain audio transcription results
        try:
            response = urlopen(request, timeout=20)
        except HTTPError as e:
            raise RequestError("recognition request failed: {}".format(e.reason))
        except URLError as e:
            raise RequestError("recognition connection failed: {}".format(e.reason))
        response_text = response.read().decode("utf-8")

        # ignore any blank blocks
        actual_result = []
        for line in response_text.split("\n"):
            if not line: continue
            result = json.loads(line)["result"]
            if len(result) != 0:
                actual_result = result[0]
                break

        # return results
        if show_all: return actual_result
        if not isinstance(actual_result, dict) or len(actual_result.get("alternative", [])) == 0: raise Exception()

        if "confidence" in actual_result["alternative"]:
            # return alternative with highest confidence score
            best_hypothesis = max(actual_result["alternative"], key=lambda alternative: alternative["confidence"])
        else:
            # when there is no confidence available, we arbitrarily choose the first hypothesis.
            best_hypothesis = actual_result["alternative"][0]
        if "transcript" not in best_hypothesis: raise Exception()
        return best_hypothesis["transcript"]



def provideAudioText():
    try:
        with mic as source:
            print("Recording now")
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source, timeout = 1, phrase_time_limit=3)
            print("Ending record")
            print(recognize_google(audio))
    except:
        print("No audio recorded")

import time
nexttime = time.time()
while True:
    provideAudioText()
    nexttime += 1
    sleeptime = nexttime - time.time()
    if sleeptime > 0:
        time.sleep(sleeptime)
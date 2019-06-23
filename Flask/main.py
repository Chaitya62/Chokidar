import os

print(os.listdir())
from flask import Flask, render_template, Response, request, jsonify
from camera import VideoCamera
from predict import *
import json
import threading
import wave
import time
import pyaudio
import wave
import http.client
import requests

import speech_recognition as sr
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from listen_to_speech import audioToSpeech

import queue

url = "http://10.10.40.17:7000/speak"
app = Flask(__name__, static_url_path='', static_folder='templates', template_folder='templates')

# recorder defaults

prev_time = None
mic = sr.Microphone()
r = sr.Recognizer()

CURRENT_AUDIO = 0
AUDIO_QUEUE = queue.Queue()
# SYNCHRONIZER = {}
# SYNCHRONIZER['init'] = False
# SYNCHRONIZER['ready'] = False
# SYNCHRONIZER['frame_queue'] = queue.Queue()



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
    global CURRENT_AUDIO
    try:
        with mic as source:
            skip = False
            print("a")
            print("Recording now")
            list_classes = ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]
            r.adjust_for_ambient_noise(source)
            print("b")
            audio = r.listen(source, timeout = 3, phrase_time_limit = 3)
            print("c")
            print("Ending record")
            text = recognize_google(audio)
            print("Predicting toxicity")
            print(text)
            print(1)
            response = generatePredictions(text)
            print(2)
            for key in list_classes:
                print(3)
                if float(response[key]) > 0.7:
                    skip = True
            print(4)
            if skip:
                print(5)
                print("SKIP")
                return False, None
                # beep Audio response
            else:
                print(6)
                try:
                    filename = "audio" + str(CURRENT_AUDIO) + ".wav"
                
                    print("-----------------------")
                    print(audio)
                    # print(filename)
                    # with open(filename, "wb") as f:
                    #     f.write(audio.get_wav_data())
                    AUDIO_QUEUE.put(filename)
                    CURRENT_AUDIO += 1    
                    data = audio.get_wav_data()
                    files = {
                        'file': ('sample.wav', data, 'audio/wav'),
                    }
                    response = requests.post(url, files=files, data = {})
                    print("======================")
                    print(response)
                    print("======================")
                except:
                    pass
                return True, audio.get_raw_data()
            # print(recognize_google(audio))
            # return None
            return False, None
    except:
        print("No audio recorded")
        return False, None
        # return None

def get_audio():
    while True:
        # AUDIO_FILE = './beep-01a.wav'
        bool, aud = provideAudioText()
        yield(aud)
        # beeped_audio = None
        # with sr.AudioFile(AUDIO_FILE) as source:
        #     beeped_audio = r.record(source) 
        # with open(AUDIO_FILE, "rb") as fwav:
        #     data = fwav.read(1024)
        #     while data:
        #         yield data
        #         data = fwav.read(1024)

def pipeLine(WAVE_OUTPUT_FILENAME):
    text = audioToSpeech(WAVE_OUTPUT_FILENAME)
    print(text)
    response = generatePredictions(text)
    skip = False
    list_classes = ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]
    for key in list_classes:
        if float(response[key]) > 0.7:
            skip = True

    if skip:
        print("SKIP")
        # beep Audio response
    else:
        print("CLEAN AUDIO")
        # Transmit Audio
    # raj's filtering
    # Audio filtering
    # Emit to the stream

def recorder():
    global prev_time
    chunk = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    RECORD_SECONDS = 5
    audio_frames = []

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    output=True,
                    frames_per_buffer=chunk)

    while True:
        data = stream.read(chunk, exception_on_overflow=False)
        audio_frames.append(data)
        curr_time = time.time()
        if curr_time - prev_time >= 20:
            if len(audio_frames) == 0:
                continue
            WAVE_OUTPUT_FILENAME = "./audio.wav"
            waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
            waveFile.setnchannels(CHANNELS)
            waveFile.setsampwidth(p.get_sample_size(FORMAT))
            waveFile.setframerate(RATE)
            waveFile.writeframes(b''.join(audio_frames))
            waveFile.close()

            # init pipeline
            print("Bhai sahab")
            pipeLine(WAVE_OUTPUT_FILENAME)

            prev_time = time.time()
            audio_frames = []


@app.route('/')
def index():
    # global prev_time
    # prev_time = time.time()
    # th = threading.Thread(target=recorder)
    # th.start()
    return render_template('index.html')

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/audio_feed')
def audio_feed():
    return Response(get_audio(), mimetype='audio/mp3')

@app.route('/test')
def test():
    if request.method == 'GET':
        string  = request.args.get('str', None)
        return jsonify(generatePredictions(string))

@app.route('/fetch_recent_audio')
def fetch_recent_audio():
    res = {}
    audio_empty = AUDIO_QUEUE.empty()
    if not audio_empty:
        res['audio_path'] = AUDIO_QUEUE.get()
    res['status'] = audio_empty
    print(res)
    return jsonify(res)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
    
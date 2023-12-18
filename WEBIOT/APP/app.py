from datetime import datetime
import time

from flask import Flask, render_template, request, redirect, url_for

import sounddevice as sd
import soundfile as sf

import librosa   #for audio processing
import IPython.display as ipd
import numpy as np
from sklearn.preprocessing import LabelEncoder

from keras.models import load_model

import paho.mqtt.client as paho

broker="broker.hivemq.com"

client= paho.Client("client-001")

model=load_model('Speech_to_Text.hdf5')

#Setup Label
all_label = ['bed', 'bird', 'cat', 'dog', 'down', 'eight', 'five', 'four', 'go', 'left', 'nine', 'no', 'off', 
             'on', 'one', 'right', 'seven', 'six', 'stop', 'three', 'two', 'up', 'wow', 'yes', 'zero']

#Convert the output labels to integer encoded
le = LabelEncoder()
y=le.fit_transform(all_label)
classes = list(le.classes_)

def predict(audio):
    prob=model.predict(audio.reshape(1,8000,1))
    index=np.argmax(prob[0])
    return classes[index]

#Web App
app = Flask(__name__)

@app.route('/')
def home():
    return "Hello World"

@app.route('/voice', methods=["GET","POST"])
def voice():
    if request.method == "GET":
        return render_template("index.html")
    if request.method == "POST":
        samplerate = 16000  
        duration = 1 # seconds
        filename = 'voice.wav'
        print("start")
        mydata = sd.rec(int(samplerate * duration), samplerate=samplerate,
            channels=1, blocking=True)
        print("end")
        sd.wait()
        sf.write(filename, mydata, samplerate)

        #reading the voice commands
        samples, sample_rate = librosa.load('voice.wav', sr = 16000)
        samples = librosa.resample(samples, orig_sr=sample_rate, target_sr=8000)
        ipd.Audio(samples,rate=8000)

        #Send message
        print("connecting to broker ",broker)
        client.connect(broker)#connect
        client.loop_start() #start loop to process received messages
        print("publishing ")
        msg=predict(samples)
        client.publish("PTIT_26/Light/Control",msg)#publish
        time.sleep(4)
        client.loop_stop() #stop loop
        client.disconnect() #disconnect

        #Write history
        file = open("templates/history.html", "a")
        file.write(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
        file.write(" | Sended Request: ")
        file.write(msg)
        file.write("<br>")
        file.write("\n")
        file.close()

        #Delete old history
        with open("templates/history.html", 'r') as fp:
            lines = len(fp.readlines())
        if(lines>27):
            with open('templates/history.html', 'r') as fin:
                data = fin.read().splitlines(True)
            with open('templates/history.html', 'w') as fout:
                fout.writelines(data[1:])

        return redirect(request.referrer)

if __name__ == "__main__":
    app.run(debug=True)

import os
import librosa   #for audio processing
import IPython.display as ipd
import numpy as np
from sklearn.preprocessing import LabelEncoder

train_audio_path = 'train/audio/'
labels=os.listdir(train_audio_path)

from keras.models import load_model
model=load_model('Speech_to_Text.hdf5')

all_label = ['bed', 'bird', 'cat', 'dog', 'down', 'eight', 'five', 'four', 'go', 'left', 'nine', 'no', 'off', 'on', 'one', 
             'right', 'seven', 'six', 'stop', 'three', 'two', 'up', 'wow', 'yes', 'zero']

le = LabelEncoder()
y=le.fit_transform(all_label)
classes = list(le.classes_)

def predict(audio):
    prob=model.predict(audio.reshape(1,8000,1))
    index=np.argmax(prob[0])
    return classes[index]

filepath='voice-commands'

#reading the voice commands
samples, sample_rate = librosa.load(filepath + '/' + 'yes.wav', sr = 16000)
samples = librosa.resample(samples, orig_sr=sample_rate, target_sr=8000)
ipd.Audio(samples,rate=8000)  

print("Text:",predict(samples))
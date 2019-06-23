import sys, os, re, csv, math, codecs, numpy as np, pandas as pd
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.layers.normalization import BatchNormalization
from keras.layers.advanced_activations import ELU
from keras.layers import Dense, Input, LSTM, Embedding, Dropout, Activation, SpatialDropout1D
from keras.layers import MaxPool1D, Flatten, Conv1D, GRU, GlobalAveragePooling1D, GlobalMaxPooling1D
from keras.callbacks import ReduceLROnPlateau, ModelCheckpoint, EarlyStopping
from keras.layers import concatenate
from keras.layers import Bidirectional, GlobalMaxPool1D
from keras.models import Model, load_model
from keras.optimizers import Adam
from keras import initializers, regularizers, constraints, optimizers, layers


EMBEDDING_FILE='./data/glove.6B.50d.txt'
TRAIN_DATA_FILE='./data/train.csv'
MODEL_WEIGHTS_FILE = './toxic_model.h5'

embed_size = 50
max_features = 20000
maxlen = 100

train = pd.read_csv(TRAIN_DATA_FILE)

list_sentences_train = train["comment_text"].fillna("_na_").values
list_classes = ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]

tokenizer = Tokenizer(num_words=max_features)
tokenizer.fit_on_texts(list(list_sentences_train))
list_tokenized_train = tokenizer.texts_to_sequences(list_sentences_train)
model = load_model('./toxic_model.h5')

def generatePredictions(sample):
    json_return = {}
    sample_tokenizer = tokenizer.texts_to_sequences([sample])
    sample_token = pad_sequences(sample_tokenizer, maxlen=maxlen)
    test = model.predict([sample_token])
    json_return['text'] = sample
    for i in range(len(test)):
        # print(test[i])
        # print(np.mean(test[i]))
        for j, name in enumerate(list_classes):
            json_return[name] = str(test[i][j])
        json_return["mean"] = str(np.mean(test[i]))
    return json_return


print(generatePredictions(("Today is a sunny day")))

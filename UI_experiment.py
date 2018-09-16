#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 12 15:34:09 2018

@author: Apple
"""

import numpy as np
import scipy.io as io
import keras
from keras import backend as K
from EEG_models import ShallowConvNet
from keras.callbacks import Callback, EarlyStopping


datapath = '/Users/dustintt123/SSVEP_CNN/SSVEP_Data/'
SSVEP_l_data = io.loadmat(datapath+'SSVEP_l.mat')
SSVEP_l = SSVEP_l_data['SSVEP_l']
SSVEP_label = io.loadmat(datapath+'SSVEP_label.mat')['label'] # i_subj, i_session, i_stim, i_trial

n_class = 2

def process_train_data(arr, label, day_index=1):
    arr = arr[:,:,np.where(label[:,1]==day_index)]
    arr = np.squeeze(arr)
    arr = np.transpose(arr, axes = [2, 0, 1])
    return arr

def process_test_data(arr, day_index=1, binary=False, subject_index=1):
    arr = arr[np.where(arr[:,1]==day_index),0]
    if binary:
        arr[0,np.where(arr[0,:]!=subject_index)] = subject_index+1    
    arr = keras.utils.to_categorical(arr-1, n_class)
    arr = np.squeeze(arr)
    
x_train = process_train_data(SSVEP_l, SSVEP_label, day_index=1)
y_train_onehot = process_test_data(SSVEP_label, day_index=1, 
                                   binary=True, subject_index=1)

#x_train = np.squeeze(SSVEP_l[:,:,np.where(SSVEP_label[:,1]==1)])
#x_train = np.transpose(x_train, axes = [2, 0, 1])
#y_train = SSVEP_label[np.where(SSVEP_label[:,1]==1),0]
#
#permutation = np.random.permutation(x_train.shape[0])
#x_train = x_train[permutation,:,:]
#y_train = y_train[:,permutation]
#
#target_class = 1
##
#y_train[0,np.where(y_train[0,:]!=target_class)] = target_class+1
#y_train_onehot = keras.utils.to_categorical(y_train-target_class, n_class)
#y_train_onehot = np.squeeze(y_train_onehot)


x_test = process_train_data(SSVEP_l, SSVEP_label, day_index=2)
y_train_onehot = process_test_data(SSVEP_label, day_index=2, 
                                   binary=True, subject_index=1)

#x_test = np.squeeze(SSVEP_l[:,:,np.where(SSVEP_label[:,1]==2)])
#x_test = np.transpose(x_test, axes = [2, 0, 1])
#y_test = SSVEP_label[np.where(SSVEP_label[:,1]==2),0]
##y_test[0,np.where(y_test[0,:]!=1)] = 2
#
#y_test[0,np.where(y_test[0,:]!=target_class)] = target_class+1
#y_test_onehot = keras.utils.to_categorical(y_test-target_class, n_class)
#y_test_onehot = np.squeeze(y_test_onehot)


# input image dimensions
K.set_image_data_format('channels_first')
n_trial, n_channel, n_timesamp = x_train.shape
if K.image_data_format() == 'channels_first':
    x_train = x_train.reshape(x_train.shape[0], 1, n_channel, n_timesamp)
    x_test = x_test.reshape(x_test.shape[0], 1, n_channel, n_timesamp)
    input_shape = (1, n_channel, n_timesamp)
else:
    x_train = x_train.reshape(x_train.shape[0], n_channel, n_timesamp, 1)
    x_test = x_test.reshape(x_test.shape[0], n_channel, n_timesamp, 1)
    input_shape = (n_channel, n_timesamp, 1)

batch_size = 100
n_epoch = 5
varEarlyStopping = 0
n_patience = 10

model = ShallowConvNet(input_shape)
#model = SCCNet(input_shape)
adam = keras.optimizers.adam()
model.compile(loss=keras.losses.categorical_crossentropy,
          optimizer=adam,
          metrics=['accuracy'])
class AccuracyHistory(keras.callbacks.Callback):
    def on_train_begin(self, logs={}):
        self.acc = []
    def on_epoch_end(self, batch, logs={}):
        self.acc.append(logs.get('acc'))
history = AccuracyHistory()
#    varEarlyStopping = 0 # 0 -> no early stopping; 1 -> early stopping
if varEarlyStopping == 0:
    callbacks = [history]
else:    # For early stopping:
    callbacks = [history, EarlyStopping(monitor='val_loss',patience=n_patience, verbose=1, mode='auto', min_delta=0.001)]
#    batch_size = np.amax([72, int(np.around(x.shape[0]/8))]);
#    n_epoch = 100
    
print(model.summary())

fit_hist = model.fit(x_train, y_train_onehot,
      batch_size=batch_size,
      epochs=n_epoch,
      verbose=1,
#          validation_data=(x_test, y_test),
#          validation_data=(x_valid, y_valid),
      validation_split=0.25,
      callbacks=callbacks,
      shuffle=True)

y_hat = model.predict_on_batch(x_test)
score = model.evaluate(x_test, y_test_onehot, verbose = 1)
print(score)







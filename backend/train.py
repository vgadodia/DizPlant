import tensorflow as tf
from tensorflow import keras
import matplotlib.pyplot as plt
import numpy as np
import os

train_data = keras.preprocessing.image.ImageDataGenerator(rescale = 1/255.0,shear_range = 0.2,zoom_range = 0.2,width_shift_range = 0.2,height_shift_range = 0.2,fill_mode="nearest").flow_from_directory("output/train",target_size=(224,224),batch_size=32,class_mode="categorical")
test_data =  keras.preprocessing.image.ImageDataGenerator(rescale = 1/255.0).flow_from_directory("output/valid",target_size=(224,224),batch_size=32,class_mode="categorical")
base_model = keras.applications.MobileNet(weights="imagenet",include_top=False,input_shape=(224,224,3))
base_model.trainable = False
inputs = keras.Input(shape=(224,224,3))
x = keras.layers.Dense(38,activation="softmax")(keras.layers.Dropout(0.2)(keras.layers.GlobalAveragePooling2D()(base_model(inputs,training=False))))
model = keras.Model(inputs=inputs, outputs=x, name="plant_disease")
optimizer = keras.optimizers.Adam()
model.compile(optimizer=optimizer,loss=keras.losses.CategoricalCrossentropy(from_logits=True),metrics=[keras.metrics.CategoricalAccuracy()])
history = model.fit_generator(train_data,validation_data=test_data,epochs=25,steps_per_epoch=150,validation_steps=100)
model.evaluate(test_data)
model.save('model.h5')

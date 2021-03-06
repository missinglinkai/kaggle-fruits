import numpy as np  # linear algebra
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)
import keras
import tensorflow as tf
# import matplotlib.pyplot as plt
import cv2
import glob
import os
from keras.models import Sequential, Model
from keras.layers import Dense, Dropout, Conv2D, MaxPooling2D, Flatten, Activation, BatchNormalization
from keras.optimizers import Adamax
from keras.layers.advanced_activations import LeakyReLU
from keras import backend as K
import missinglink
from keras.callbacks import ModelCheckpoint, ReduceLROnPlateau, TensorBoard
import errno


def safe_make_dirs(dir_name):
    try:
        os.makedirs(dir_name)
    except OSError as ex:
        if ex.errno != errno.EEXIST:
            raise


input_path = './input/fruits-360'

training_fruit_img = []
training_label = []
for dir_path in glob.glob(os.path.join(input_path, 'Training', '*')):
    img_label = dir_path.split("/")[-1]
    for image_path in glob.glob(os.path.join(dir_path, "*.jpg")):
        image = cv2.imread(image_path, cv2.IMREAD_COLOR)
        image = cv2.resize(image, (64, 64))
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        training_fruit_img.append(image)
        training_label.append(img_label)
training_fruit_img = np.array(training_fruit_img)
training_label = np.array(training_label)

label_to_id = {v: k for k, v in enumerate(np.unique(training_label))}
id_to_label = {v: k for k, v in label_to_id.items()}

training_label_id = np.array([label_to_id[i] for i in training_label])

validation_fruit_img = []
validation_label = []
for dir_path in glob.glob(os.path.join(input_path, 'Validation', '*')):
    img_label = dir_path.split("/")[-1]
    for image_path in glob.glob(os.path.join(dir_path, "*.jpg")):
        image = cv2.imread(image_path, cv2.IMREAD_COLOR)
        image = cv2.resize(image, (64, 64))
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        validation_fruit_img.append(image)
        validation_label.append(img_label)
validation_fruit_img = np.array(validation_fruit_img)
validation_label = np.array(validation_label)
validation_label_id = np.array([label_to_id[i] for i in validation_label])

X_train, X_test = training_fruit_img, validation_fruit_img
Y_train, Y_test = training_label_id, validation_label_id
# mean(X) = np.mean(X_trai
X_train = X_train / 255
X_test = X_test / 255

X_flat_train = X_train.reshape(X_train.shape[0], 64 * 64 * 3)
X_flat_test = X_test.reshape(X_test.shape[0], 64 * 64 * 3)

# One Hot Encode the Output
Y_train = keras.utils.to_categorical(Y_train, 60)
Y_test = keras.utils.to_categorical(Y_test, 60)

print('Original Sizes:', X_train.shape, X_test.shape, Y_train.shape, Y_test.shape)
print('Flattened:', X_flat_train.shape, X_flat_test.shape)

model = Sequential()
model.add(Conv2D(16, (3, 3), input_shape=(64, 64, 3), padding='same'))
model.add(LeakyReLU(0.5))
model.add(BatchNormalization())
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Conv2D(32, (3, 3), padding='same'))
model.add(LeakyReLU(0.5))
model.add(BatchNormalization())
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Conv2D(32, (3, 3), padding='same'))
model.add(LeakyReLU(0.5))
model.add(BatchNormalization())
model.add(MaxPooling2D(pool_size=(2, 2)))


model.add(Conv2D(64, (3, 3), padding='same'))
model.add(LeakyReLU(0.5))
model.add(BatchNormalization())
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Flatten())
model.add(Dense(256, activation='elu'))
# model.add(LeakyReLU(0.1))
model.add(Dropout(0.5))
model.add(Dense(60))
model.add(Activation("softmax"))

model.summary()

missinglink_callback = missinglink.KerasCallback()
missinglink_callback.set_properties(display_name='Fruits 360 dataset', description='https://www.kaggle.com/naveenc131/cnn-with-accuracy-of-98 called with GIT LFS support')
missinglink_callback.set_properties(class_mapping={k: v for k, v in enumerate(np.unique(training_label))}
)

checkpoint_path = 'weights_epoch-{epoch:02d}_loss-{loss:.4f}.h5'
tensor_board_path = 'tensorboard'
if missinglink_callback.rm_active:
    directory = '/output/checkpoints'
    safe_make_dirs(directory)
    checkpoint_path = os.path.join(directory, checkpoint_path)
    tensor_board_path = os.path.join('/output', tensor_board_path)

model.compile(loss='categorical_crossentropy',
              optimizer=Adamax(),
              metrics=['accuracy'])

model.fit(X_train,
          Y_train,
          batch_size=128,
          epochs=20,
          verbose=1,
          validation_data=(X_test, Y_test),
          callbacks=[
              ModelCheckpoint(
                  checkpoint_path,
                  monitor='val_acc',
                  verbose=1,
                  save_best_only=True,
                  save_weights_only=False,
                  mode='max',
                  period=5
              ),
              TensorBoard(log_dir=tensor_board_path),
              missinglink_callback,
          ]
          )
print('Training done. Testing.')
# endregion
safe_make_dirs('/output/models')
model_name = 'fruits db'
model.save('/output/models/{}.h5'.format(model_name))
model.save_weights('/output/models/{}_weights.h5'.format(model_name))

with missinglink_callback.test(model):
    score = model.evaluate(X_test, Y_test, verbose=0)

print('Test loss:', score[0])
print('Test accuracy:', score[1])

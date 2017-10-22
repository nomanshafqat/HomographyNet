#!/usr/bin/env python

import os.path

from keras.applications import MobileNet
from keras.utils.data_utils import get_file
from keras.models import Sequential, Model
from keras.layers import Conv2D, Dense, MaxPooling2D, InputLayer, Dropout, \
    BatchNormalization, Flatten, Concatenate


BASELINE_WEIGHTS_PATH = 'https://github.com/baudm/HomographyNet/raw/master/models/homographynet_weights_tf_dim_ordering_tf_kernels.h5'
MOBILENET_WEIGHTS_PATH = 'https://github.com/baudm/HomographyNet/raw/master/models/mobile_homographynet_weights_tf_dim_ordering_tf_kernels.h5'


def create_model(use_weights=False):
    model = Sequential(name='homographynet')
    model.add(InputLayer((128, 128, 2), name='input_1'))

    # 4 Layers with 64 filters, then another 4 with 128 filters
    filters = 4 * [64] + 4 * [128]
    for i, f in enumerate(filters, 1):
        model.add(Conv2D(f, 3, padding='same', activation='relu', name='conv2d_{}'.format(i)))
        model.add(BatchNormalization(name='batch_normalization_{}'.format(i)))
        # MaxPooling after every 2 Conv layers except the last one
        if i % 2 == 0 and i != 8:
            model.add(MaxPooling2D(strides=(2, 2), name='max_pooling2d_{}'.format(int(i/2))))

    model.add(Flatten(name='flatten_1'))
    model.add(Dropout(0.5, name='dropout_1'))
    model.add(Dense(1024, activation='relu', name='dense_1'))
    model.add(Dropout(0.5, name='dropout_2'))

    # Regression model
    model.add(Dense(8, name='dense_2'))

    if use_weights:
        weights_name = os.path.basename(BASELINE_WEIGHTS_PATH)
        weights_path = get_file(weights_name, BASELINE_WEIGHTS_PATH,
                                cache_subdir='models',
                                md5_hash='3118ab8ddb49dfa48b38d7cad7efcb88')
        model.load_weights(weights_path)

    return model


def create_mobilenet_model(use_weights=False):
    base_model = MobileNet(input_shape=(128, 128, 2), include_top=False, weights=None)
    x = base_model.output

    x1 = Conv2D(2, 4, name='conv2d_1')(x)
    x2 = Conv2D(2, 4, name='conv2d_2')(x)
    x3 = Conv2D(2, 4, name='conv2d_3')(x)
    x4 = Conv2D(2, 4, name='conv2d_4')(x)
    x = Concatenate(name='concatenate_1')([x1, x2, x3, x4])
    x = Flatten(name='flatten_1')(x)

    model = Model(base_model.input, x, name='mobile_homographynet')

    if use_weights:
        weights_name = os.path.basename(MOBILENET_WEIGHTS_PATH)
        weights_path = get_file(weights_name, MOBILENET_WEIGHTS_PATH,
                                cache_subdir='models',
                                md5_hash='7f14ab44ad375fa0ed5c205f077c4bbe')
        model.load_weights(weights_path)

    return model

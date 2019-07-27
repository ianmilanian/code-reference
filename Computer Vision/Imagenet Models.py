import os
import cv2
import numpy as np
os.environ["KERAS_BACKEND"] = "tensorflow" # tensorflow, theano, or cntk

from keras.applications import VGG16
from keras.applications import VGG19
from keras.applications import ResNet50
from keras.applications import Xception # tensorflow only
from keras.applications import InceptionV3
from keras.applications import imagenet_utils
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from keras.applications.inception_v3 import preprocess_input

path = "data/images"
for n, network in enumerate([ResNet50, VGG16, VGG19, InceptionV3, Xception]):
    model   = network(weights="imagenet")
    shape   = (299, 299)       if network is InceptionV3 or network is Xception else (224, 224)
    process = preprocess_input if network is InceptionV3 or network is Xception else imagenet_utils.preprocess_input
    for file in (os.listdir(path)):
        image = load_img("{}/{}".format(path, file), target_size=shape) # res/vgg specific size!
        image = img_to_array(image)
        image = np.expand_dims(image, axis=0)
        image = process(image)
        preds = model.predict(image)
        _, desc, prob = imagenet_utils.decode_predictions(preds)[0][0]
        print("Network: {} Predicted: {} ({:.0%}) Image: {}".format(n+1, desc, prob, file))
    break

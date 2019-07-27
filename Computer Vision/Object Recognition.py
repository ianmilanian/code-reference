import os
import cv2
import sys
import numpy as np
import tensorflow as tf

from multiprocessing import Queue, Pool
from scripts.tensor_out import worker

sys.path.append("C:/Users/user/AppData/Local/Continuum/Anaconda3/Lib/site-packages/tensorflow/models/")
sys.path.append("C:/Users/user/AppData/Local/Continuum/Anaconda3/Lib/site-packages/tensorflow/models/slim")

from PIL import Image
from lxml import etree
from multiprocessing import Queue
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils
from object_detection.utils import dataset_util

# ssd_mobilenet_v1 model trained on coco_11_06_2017 data set.
# https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md

def _detect_objects(image, tf_session, category_index, detection_graph):
    image_expanded = np.expand_dims(image, axis=0)
    image_tensor   = detection_graph.get_tensor_by_name('image_tensor:0')
    boxes          = detection_graph.get_tensor_by_name('detection_boxes:0')
    scores         = detection_graph.get_tensor_by_name('detection_scores:0')
    classes        = detection_graph.get_tensor_by_name('detection_classes:0')
    num_detections = detection_graph.get_tensor_by_name('num_detections:0')
    
    boxes, scores, classes, num_detections = tf_session.run(
        [boxes, scores, classes, num_detections],
        feed_dict={image_tensor: image_expanded})
    
    visualization_utils.visualize_boxes_and_labels_on_image_array(
        image,
        np.squeeze(boxes),
        np.squeeze(classes).astype(np.int32),
        np.squeeze(scores),
        category_index,
        use_normalized_coordinates=True,
        line_thickness=5)
    return image

def worker(in_q, out_q):
    path            = "C:/Users/user/AppData/Local/Continuum/Anaconda3/Lib/site-packages/tensorflow/models/"
    label_map       = label_map_util.load_labelmap("{}/object_detection/data/mscoco_label_map.pbtxt".format(path))
    categories      = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=90, use_display_name=True)
    category_index  = label_map_util.create_category_index(categories)
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile("models/ssd_mobilenet_v1_coco_11_06_2017/frozen_inference_graph.pb", 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name="")
        tf_session = tf.Session(graph=detection_graph)
        while True:
            out_q.put(_detect_objects(in_q.get(), tf_session, category_index, detection_graph))
        tf_session.close()

if __name__ == '__main__':
    output = cv2.VideoWriter("output.mp4", cv2.VideoWriter_fourcc(*"MP4V"), 30, (640,360))
    video  = cv2.VideoCapture("data/Street Market in Thailand.mp4")
    in_q   = Queue(maxsize=5)
    out_q  = Queue(maxsize=5)
    pool   = Pool(3, worker, (in_q, out_q))

    while True:
        state, frame = video.read() # I/O heavy reads in separate thread
        if not state:
            break
        try:
            h,w   = frame.shape[:2]
            r     = 0.5
            dim   = (int(w * r), int(h * r))
            frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
        except:
            continue
        in_q.put(frame)
        output.write(out_q.get())

    pool.terminate()
    output.release()
    cv2.waitKey(0)
    cv2.destroyAllWindows()

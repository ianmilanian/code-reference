import os
import cv2
import dlib
import numpy as np

from glob import glob
from tqdm import tqdm
from jinja2 import Environment
from jinja2 import FileSystemLoader
from multiprocessing import Pool
from sklearn.externals import joblib
from scipy.spatial.distance import cdist

#install dlib with 'conda install -c conda-forge dlib'
#dlib models found at https://github.com/davisking/dlib-models

face_detector  = dlib.get_frontal_face_detector() # cnn detector is faster for gpu (requires building dlib 19.9)
pose_predictor = dlib.shape_predictor("models/shape_predictor_68_face_landmarks.dat")
face_encoder   = dlib.face_recognition_model_v1("models/dlib_face_recognition_resnet_model_v1.dat")

def encode(file, sample=1, jitters=1):
    def encoder(img):
        faces = face_detector(img, sample) # [dlib.rectangle(62, 157, 170, 42)] # (top, right, bottom, left)
        poses = [pose_predictor(img, box) for box in faces]
        feats = [face_encoder.compute_face_descriptor(img, face, jitters) for face in poses]
        return feats
    if os.path.getsize(file) > 2000:
        img  = cv2.imread(file)
        hash = os.path.basename(file).split(".")[0]
        try:
            return [(hash, feats) for feats in encoder(img)]
        except Exception as e:
            print(e)
            pass
    return []

def batch_encode():
    with Pool() as p:
        paths = glob("images/*")
        hash_list, feat_list = [],[]
        for data in tqdm(p.imap_unordered(encode, paths), total=len(paths)):
            if not data:
                continue
            for hash, feats in data:
                hash_list.append(hash)
                feat_list.append(feats)
    hash_list = np.asarray(hash_list)
    feat_list = np.asarray(feat_list)
    feat_norm = feat_list / np.linalg.norm(feat_list, axis=1).reshape(-1,1)
    joblib.dump([hash_list, feat_norm], "models/feats.pkl")

def image_match(file, tolerance=0.48):
    matched = []
    hash_list, feat_list = joblib.load("models/feats.pkl")
    for _, feats in encode(file):
        match = (cdist(feat_list, [feats]) < tolerance).nonzero()[0].tolist()
        matched.extend(hash_list[match])
        
    images = "\n".join(set([img for img in matched]))
    
    with open("{}_output.html".format(date.strftime("%Y%m%d-%H%M%S")), "w") as f:
        template = Environment(loader=FileSystemLoader(""), trim_blocks=True).get_template("template.html")
        f.write(template.render(images=images).replace("&#39;", "\'"))

html = \ # template.html
"""
<div id="images"></div>

<script>
var images = [{{ images }}];

var container   = document.getElementById("images");
var docFragment = document.createDocumentFragment();

images.forEach(function(url, index, originalArray){
    var img = document.createElement("img");
    img.src = url + ".jpeg";
    img.style.width   = "160px";
    img.style.height  = "120px";
    img.style.padding = "2px";
    img.onerror = function(){
        img.src = url + ".png";
    };
    img.onclick = function(){
        window.open(img.src);
    };
    docFragment.appendChild(img);
});

container.appendChild(docFragment);
</script>
"""

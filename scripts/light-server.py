'''
pip install flask gevent requests pillow

https://github.com/jrosebr1/simple-keras-rest-api

https://gist.github.com/kylehounslow/767fb72fde2ebdd010a0bf4242371594

'''

''' Usage
python ..\scripts\classifier.py --socket=5000 --weights=weights\obj_last.weights
curl -X POST -F image=@dog.png http://localhost:5000/training/begin?plan=testplan
'''


import threading
import time
import csv
import datetime
import flask
import sys
import os
import cv2 as cv
import argparse
import lightnet
import darknet
import socket
import requests
import logging
logger = logging.getLogger(__name__)
app = flask.Flask(__name__)

args = None
nets = []
metas = []
args_groups = []
csv_file = None
csv_writer = None
cap = None

gpu_lock = threading.Lock()

host_ip = 'localhost'

def get_Host_name_IP():
    try:
        global host_ip
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("baidu.com", 80))
        host_ip, _ = s.getsockname()
        print("http://%s:5000" % host_ip)
    except:
        print("Unable to get Hostname and IP")


@app.route("/", methods=["GET"])
def index_get():
    data = vars(args)
    data['usage'] = "curl -X POST -F image=@dog.png http://%s:5000/predict" % (
        host_ip)
    return flask.jsonify(data)

@app.route("/training/begin", methods=["GET"])
def training_begin():
    plan = flask.request.args.get("plan")
    print(plan)
    url = 'http://localhost:8800/api/Training/plan?plan=%s' % plan
    response = requests.get(url)
    result = response.json()    
    return result

@app.route("/predict", methods=["POST"])
def predict_post():
    import numpy as np

    # initialize the data dictionary that will be returned from the
    # view

    logger.info("/predict start")

    data = []

    # ensure an image was properly uploaded to our endpoint
    if flask.request.method != "POST":
        return '[]'
    image = flask.request.files.get("image")
    if not image:
        return '[]'

    try:
        # read the image in PIL format
        image = flask.request.files["image"].read()
        logger.info("|flask.request")
        # convert string of image data to uint8
        nparr = np.fromstring(image, np.uint8)

        # decode image
        frame = cv.imdecode(nparr, cv.IMREAD_COLOR)

        logger.info("|cv.imdecode")
        results = slave_labor(frame)
        logger.info(results)
    except:
        logger.error('|exception', exc_info=True)
        return "[]"

    logger.info("\predict end")
    # return the data dictionary as a JSON response
    return flask.jsonify(results)

def cvDrawBoxes(detections, img):
    roi_array = []
    for detection in detections:
        x, y, w, h = detection[2][0],\
            detection[2][1],\
            detection[2][2],\
            detection[2][3]
        xmin, ymin, xmax, ymax = lightnet.convertBack(
            float(x), float(y), float(w), float(h))
        pt1 = (xmin, ymin)
        pt2 = (xmax, ymax)
        roi_array.append((xmin, ymin, xmax, ymax))

        if args.debug:
            cv.rectangle(img, pt1, pt2, (0, 255, 0), 1)
            cv.putText(img,
                       # detection[0] +
                       " [" + str(round(detection[1] * 100, 2)) + "]",
                       (pt1[0], pt1[1] - 5), cv.FONT_HERSHEY_SIMPLEX, 0.5,
                       [0, 255, 0], 2)
    return roi_array


def validate_run():
    with open(args.valid_csv) as csv_file:
        csv_reader = csv.DictReader(csv_file)
        next(csv_reader)

        for row in csv_reader:
            sku = row['SKU']
            filename = row['image']
            # print(filename)
            frame = cv.imread(filename)
            if frame is None:
                continue
            results = slave_labor(frame)
            rank = 0
            score = 0
            for i, r in enumerate(results):
                if r[0] == sku:
                    rank = i + 1
                    score = r[1]
                    break
            print(sku, filename, rank, score)


def slave_labor(frame):
    h, w, _ = frame.shape
    roi_array = []
    full_im, _ = darknet.array_to_image(frame)
    darknet.rgbgr_image(full_im)

    gpu_lock.acquire()
    if args.yolo:
        if w < h:
            spacing = int((h - w) / 2)
            roi_array = [(0, spacing, w, h - spacing)]
        else:
            spacing = int((w - h) / 2)
            roi_array = [(spacing, 0, w - spacing, h)]

    if not roi_array:
        roi_array = [(0, 0, w, h)]

    preds = []

    frame_rois = []

    for i, _ in enumerate(nets):
        results = [] # cross all rois
        for roi in roi_array:
            if args.yolo:
                # print(roi)
                frame_roi = frame[roi[1]: roi[3], roi[0]:roi[2]]
                frame_rois.append(frame_roi)
                if not args.socket and not args.interactive:
                    cv.imshow("frame_roi", frame_roi)
            else:
                frame_roi = frame
            im, _ = darknet.array_to_image(frame_roi)
            darknet.rgbgr_image(im)
            r = lightnet.classify(nets[i], metas[i], im) # for single roi

            results.extend(r)
        results = sorted(results, key=lambda x: -x[1])
        for rank in range(0, args.top_k):
            (label, score) = results[rank]
            preds.append({
                'plan': '100XGROUP', # TODO: remove hardcoding
                'group': args_groups[i], 
                'predicate_sku': label,
                'score': score,
            })
    logger.info("|lightnet.classify")
    gpu_lock.release()

    return preds


def main():
    # lightnet.set_cwd(dir)
    global nets, metas, args, cap, args_groups

    def add_bool_arg(parser, name, default=False):
        group = parser.add_mutually_exclusive_group(required=False)
        group.add_argument('--' + name, dest=name, action='store_true')
        group.add_argument('--no-' + name, dest=name, action='store_false')
        parser.set_defaults(**{name: default})

    parser = argparse.ArgumentParser()
    parser.add_argument('--group', default='default')
    parser.add_argument('--cfg', default='obj.cfg')
    parser.add_argument('--weights', default='weights/obj_last.weights')
    parser.add_argument('--names', default='obj.names')
    parser.add_argument('--socket', type=int, default=5000)
    parser.add_argument('--top_k', type=int, default=5)
    parser.add_argument('--gold_confidence', type=float, default=0.95)
    parser.add_argument('--threshold', type=float, default=0.5)
    add_bool_arg(parser, 'debug')

    args = parser.parse_args()
    # args_cfgs = args.cfg.split(',')
    # args_weights = args.weights.split(',')
    # args_names = args.names.split(',')
    # args_groups = args.group.split(',')
    # for i, _ in enumerate(args_cfgs):
    #     net, meta = lightnet.load_network_meta(
    #         args_cfgs[i], args_weights[i], args_names[i])
    #     nets.append(net)
    #     metas.append(meta)

    logging.basicConfig(level=logging.INFO)

    # flask routine
    print('=========================================')
    get_Host_name_IP()
    print('=========================================')
    app.run(host='0.0.0.0', port=args.socket, threaded=True)

if __name__ == "__main__":
    main()
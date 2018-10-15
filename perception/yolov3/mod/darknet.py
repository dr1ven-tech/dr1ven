from ctypes import Structure
from ctypes import c_float, c_int, c_char_p, c_void_p, pointer
from ctypes import POINTER, CDLL, RTLD_GLOBAL
import cv2
import os
import time


class BOX(Structure):
    _fields_ = [("x", c_float),
                ("y", c_float),
                ("w", c_float),
                ("h", c_float)]


class DETECTION(Structure):
    _fields_ = [("bbox", BOX),
                ("classes", c_int),
                ("prob", POINTER(c_float)),
                ("mask", POINTER(c_float)),
                ("objectness", c_float),
                ("sort_class", c_int)]


class IMAGE(Structure):
    _fields_ = [("w", c_int),
                ("h", c_int),
                ("c", c_int),
                ("data", POINTER(c_float))]


class METADATA(Structure):
    _fields_ = [("classes", c_int),
                ("names", POINTER(c_char_p))]


module_dir = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))

lib = CDLL(os.path.join(module_dir, "..", "libdarknet.so"), RTLD_GLOBAL)
lib.network_width.argtypes = [c_void_p]
lib.network_width.restype = c_int
lib.network_height.argtypes = [c_void_p]
lib.network_height.restype = c_int

predict = lib.network_predict
predict.argtypes = [c_void_p, POINTER(c_float)]
predict.restype = POINTER(c_float)

set_gpu = lib.cuda_set_device
set_gpu.argtypes = [c_int]

make_image = lib.make_image
make_image.argtypes = [c_int, c_int, c_int]
make_image.restype = IMAGE

get_network_boxes = lib.get_network_boxes
get_network_boxes.argtypes = [
    c_void_p, c_int, c_int, c_float,
    c_float, POINTER(c_int), c_int, POINTER(c_int),
]
get_network_boxes.restype = POINTER(DETECTION)

make_network_boxes = lib.make_network_boxes
make_network_boxes.argtypes = [c_void_p]
make_network_boxes.restype = POINTER(DETECTION)

free_detections = lib.free_detections
free_detections.argtypes = [POINTER(DETECTION), c_int]

free_ptrs = lib.free_ptrs
free_ptrs.argtypes = [POINTER(c_void_p), c_int]

network_predict = lib.network_predict
network_predict.argtypes = [c_void_p, POINTER(c_float)]

reset_rnn = lib.reset_rnn
reset_rnn.argtypes = [c_void_p]

load_net = lib.load_network
load_net.argtypes = [c_char_p, c_char_p, c_int]
load_net.restype = c_void_p

do_nms_obj = lib.do_nms_obj
do_nms_obj.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

do_nms_sort = lib.do_nms_sort
do_nms_sort.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

free_image = lib.free_image
free_image.argtypes = [IMAGE]

letterbox_image = lib.letterbox_image
letterbox_image.argtypes = [IMAGE, c_int, c_int]
letterbox_image.restype = IMAGE

load_meta = lib.get_metadata
lib.get_metadata.argtypes = [c_char_p]
lib.get_metadata.restype = METADATA

load_image = lib.load_image_color
load_image.argtypes = [c_char_p, c_int, c_int]
load_image.restype = IMAGE

rgbgr_image = lib.rgbgr_image
rgbgr_image.argtypes = [IMAGE]

predict_image = lib.network_predict_image
predict_image.argtypes = [c_void_p, IMAGE]
predict_image.restype = POINTER(c_float)


def load_meta_chdir(
        path,
):
    cwd = os.getcwd()
    os.chdir(os.path.join(module_dir, ".."))
    meta = load_meta(path)
    os.chdir(cwd)

    return meta


def classify(net, meta, im):
    out = predict_image(net, im)
    res = []
    for i in range(meta.classes):
        res.append((meta.names[i], out[i]))
    res = sorted(res, key=lambda x: -x[1])
    return res


def detect_from_disk(net, meta, image, thresh=.5, hier_thresh=.5, nms=.45):
    im = load_image(image, 0, 0)
    num = c_int(0)
    pnum = pointer(num)
    predict_image(net, im)
    dets = get_network_boxes(
        net, im.w, im.h, thresh, hier_thresh, None, 0, pnum,
    )
    num = pnum[0]
    if (nms):
        do_nms_obj(dets, num, meta.classes, nms)

    res = []
    for j in range(num):
        for i in range(meta.classes):
            if dets[j].prob[i] > 0:
                b = dets[j].bbox
                res.append(
                    (meta.names[i], dets[j].prob[i], (b.x, b.y, b.w, b.h))
                )
    res = sorted(res, key=lambda x: -x[1])
    free_image(im)
    free_detections(dets, num)
    return res


def array_to_image(arr):
    arr = arr.transpose(2, 0, 1)
    c = arr.shape[0]
    h = arr.shape[1]
    w = arr.shape[2]
    arr = (arr/255.0).flatten()
    data = (c_float * len(arr))(*arr)
    im = IMAGE(w, h, c, data)
    return im


def detect(net, meta, image, thresh=.5, hier_thresh=.5, nms=.45):
    im = array_to_image(image)
    num = c_int(0)
    pnum = pointer(num)
    predict_image(net, im)
    dets = get_network_boxes(
        net, im.w, im.h, thresh, hier_thresh, None, 0, pnum,
    )
    num = pnum[0]
    if (nms):
        do_nms_obj(dets, num, meta.classes, nms)

    res = []
    for j in range(num):
        for i in range(meta.classes):
            if dets[j].prob[i] > 0:
                b = dets[j].bbox
                res.append(
                    (meta.names[i], dets[j].prob[i], (b.x, b.y, b.w, b.h))
                )
    res = sorted(res, key=lambda x: -x[1])
    free_detections(dets, num)
    return res


if __name__ == "__main__":
    start = time.time()
    net = load_net(
        bytes(
            os.path.join(module_dir, "../cfg/yolov3.cfg"),
            encoding='utf-8',
        ),
        bytes(
            os.path.join(module_dir, "..", "yolov3.weights"),
            encoding='utf-8',
        ),
        0,
    )
    print("Network loaded: time={}".format(time.time()-start))

    start = time.time()
    meta = load_meta_chdir(
        bytes(
            os.path.join(module_dir, "../cfg/coco.data"),
            encoding='utf-8',
        ),
    )
    print("Metadata loaded: time={}".format(time.time()-start))

    start = time.time()
    r = detect_from_disk(
        net,
        meta,
        bytes(
            os.path.join(module_dir, "../data/dog.jpg"),
            encoding='utf-8',
        ),
    )
    print("Prediction from disk: time={}".format(time.time()-start))
    print(r)

    start = time.time()
    image = cv2.imread(os.path.join(module_dir, "../data/dog.jpg"))
    print("Image loaded: time={}".format(time.time()-start))

    start = time.time()
    r = detect(
        net,
        meta,
        image,
    )
    print("Prediction in-memory: time={}".format(time.time()-start))
    print(r)

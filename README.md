# yolo-studio
A turnkey solution to train and deploy your own object detection network, contains:

- Augmentor - image augmentation library in Python.
- Yolo_mark - the toolkit to prepare training data.
- darknet - the main engine for training & inferencing.
- yolo2_light - lightweighted inferencing engine, optional.

# How to build

## Install CUDA

- Uninstall Geforce Experience and current driver
- CUDA 9.1: https://developer.nvidia.com/cuda-downloads
- cuDNN v7.x for CUDA: https://developer.nvidia.com/rdp/cudnn-download

    -  Extract to the same folder as CUDA SDK
    -  e.g. `c:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v9.1\`

## Install OpenCV
- OpenCV 3.4.0: https://sourceforge.net/projects/opencvlibrary/files/opencv-win/3.4.0/opencv-3.4.0-vc14_vc15.exe/download
- Extract to `d:\opencv\`
- Make symbolic link from `c:\opencv_3.0\opencv\` to `d:\opencv\`

## Build from source

Execute the batch file
> build.bat

Or build the componets from Visual Studio
- darknet: `darknet\build\darknet\darknet.sln`, x64|Release -> `darknet\build\darknet\x64\darknet.exe`
- Yolo_mark: `Yolo_mark\yolo_mark.sln`, x64|Release -> `Yolo_mark\x64\Release\yolo_mark.exe`
- yolo2_light: `yolo2_light\yolo_gpu.sln`, Release -> `yolo2_light\bin\yolo_gpu.exe`

# Object Detection - yolo
## How to mark labelled images

 - delete all files from directory `my-yolo-net/img` and put your `.jpg`-images in
 - change numer of classes (objects for detection) in file `my-yolo-net/obj.data`: https://github.com/jing-vision/yolo-studio/blob/master/networks/yolo-template/obj.data#L1
 - put names of objects, one for each line in file `my-yolo-net/obj.names`: https://github.com/jing-vision/yolo-studio/blob/master/networks/yolo-template/obj.names
 - Run file: `my-yolo-net/yolo_mark.cmd`

## Train yolo v2

0. Fork `networks/yolov2-template` to `networks/my-yolo-net`

1. Download pre-trained weights for the convolutional layers: http://pjreddie.com/media/files/darknet19_448.conv.23 to `bin/darknet19_448.conv.23`

2. To training for your custom objects, you should change 2 lines in file `yolo-obj.cfg`:

 - change `classes` in obj.data#L1
 - set number of classes (objects) in yolo-obj.cfg#L230
 - set `filter`-value equal to `(classes + 5)*5` in yolo-obj.cfg#L224

3. Run `my-yolo-net/train.cmd`

## Train yolo v3

0. Fork `networks/yolov3-template` to `networks/my-yolo-net`

1. Download pre-trained weights for the convolutional layers: http://pjreddie.com/media/files/darknet53.conv.74 to `bin/darknet53.conv.74`

2. Create file `yolo-obj.cfg` with the same content as in `yolov3.cfg` (or copy `yolov3.cfg` to `yolo-obj.cfg)` and:

  * change line batch to [`batch=64`](yolo-obj.cfg#L3)
  * change line subdivisions to [`subdivisions=8`](yolo-obj.cfg#L4)
  * change line `classes=80` to your number of objects in each of 3 `[yolo]`-layers:
      * yolo-obj.cfg#L610
      * yolo-obj.cfg#L696
      * yolo-obj.cfg#L783
  * change [`filters=255`] to filters=(classes + 5)x3 in the 3 `[convolutional]` before each `[yolo]` layer
      * yolo-obj.cfg#L603
      * yolo-obj.cfg#L689
      * yolo-obj.cfg#L776

  So if `classes=1` then should be `filters=18`. If `classes=2` then write `filters=21`.
  
  **(Do not write in the cfg-file: filters=(classes + 5)x3)**
  
  (Generally `filters` depends on the `classes`, `coords` and number of `mask`s, i.e. filters=`(classes + coords + 1)*<number of mask>`, where `mask` is indices of anchors. If `mask` is absence, then filters=`(classes + coords + 1)*num`)

  So for example, for 2 objects, your file `yolo-obj.cfg` should differ from `yolov3.cfg` in such lines in each of **3** [yolo]-layers:

  ```
  [convolutional]
  filters=21

  [region]
  classes=2
  ```

## How to inference

## Pre-trained models for different cfg-files can be downloaded from (smaller -> faster & lower quality):

cfg|weights
---|-------
cfg/yolov2.cfg|https://pjreddie.com/media/files/yolov2.weights
cfg/yolov2-tiny.cfg|https://pjreddie.com/media/files/yolov2-tiny.weights
cfg/yolo9000.cfg|http://pjreddie.com/media/files/yolo9000.weights
cfg/yolov3.cfg|https://pjreddie.com/media/files/yolov3.weights
cfg/yolov3-tiny.cfg|https://pjreddie.com/media/files/yolov3-tiny.weights

## Run Darknet

### General

```
darknet.exe detector demo <data> <cfg> <weights> -c <camera_idx>
darknet.exe detector demo <data> <cfg> <weights> <video_filename>
darknet.exe detector test <data> <cfg> <weights> <img_filename>
```

Default launch device combination is `-i 0 -c 0`.

## Run from networks/ folder

### train_voc
```
..\bin\darknet.exe detector train data/voc.data cfg/yolo-voc.cfg weights/darknet19_448.conv.2
```

### test_voc
```
..\bin\darknet.exe detector test data/voc.data cfg/yolo-voc.cfg weights/yolo-voc.weights -thresh 0.2
```

### yolo9000 on camera #0
```
..\bin\darknet.exe detector demo data/combine9k.data cfg/yolo9000.cfg weights/yolo9000.weights
```

### yolo9000 CPU on camera #0
```
..\bin\darknet-cpu.exe detector demo data/combine9k.data cfg/yolo9000.cfg weights/yolo9000.weights
```

# Image Classification
## Download weights

cfg|weights
---|-------
cfg/alexnet.cfg|https://pjreddie.com/media/files/alexnet.weights
cfg/vgg-16.cfg|https://pjreddie.com/media/files/vgg-16.weights
cfg/extraction.cfg|https://pjreddie.com/media/files/extraction.weights
cfg/darknet.cfg|https://pjreddie.com/media/files/darknet.weights
cfg/darknet19.cfg|https://pjreddie.com/media/files/darknet19.weights
cfg/darknet19_448.cfg|https://pjreddie.com/media/files/darknet19_448.weights
cfg/resnet50.cfg|https://pjreddie.com/media/files/resnet50.weights
cfg/resnet152.cfg|https://pjreddie.com/media/files/resnet152.weights
cfg/densenet201.cfg|https://pjreddie.com/media/files/densenet201.weights
#!/usr/bin/env python3

import time
from pathlib import Path
import cv2
import depthai as dai

# Start defining a pipeline
pipeline = dai.Pipeline()

# Define source and outputs
camRgb = pipeline.createColorCamera()
xoutJpeg = pipeline.createXLinkOut()
xoutRgb = pipeline.createXLinkOut()
videoEnc = pipeline.createVideoEncoder()

xoutJpeg.setStreamName("jpeg")
xoutRgb.setStreamName("rgb")

# Properties
camRgb.setBoardSocket(dai.CameraBoardSocket.RGB)
camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_4_K)
videoEnc.setDefaultProfilePreset(camRgb.getVideoSize(), camRgb.getFps(), dai.VideoEncoderProperties.Profile.MJPEG)

# Linking
camRgb.video.link(xoutRgb.input)
camRgb.video.link(videoEnc.input)
videoEnc.bitstream.link(xoutJpeg.input)

# Connect and start the pipeline
with dai.Device(pipeline) as device:

    # Output queue will be used to get the rgb frames from the output defined above
    qRgb = device.getOutputQueue(name="rgb", maxSize=30, blocking=False)
    qJpeg = device.getOutputQueue(name="jpeg", maxSize=30, blocking=True)

    # Make sure the destination path is present before starting to store the examples
    Path('06_data').mkdir(parents=True, exist_ok=True)

    while True:
        inRgb = qRgb.tryGet()  # Non-blocking call, will return a new data that has arrived or None otherwise

        if inRgb is not None:
            cv2.imshow("rgb", inRgb.getCvFrame())

        for encFrame in qJpeg.tryGetAll():
            with open(f"06_data/{int(time.time() * 1000)}.jpeg", "wb") as f:
                f.write(bytearray(encFrame.getData()))

        if cv2.waitKey(1) == ord('q'):
            break

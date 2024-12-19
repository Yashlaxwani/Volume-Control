import cv2
import time
import numpy as np
import HandtrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

wCam, hCam = 860, 480

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0
detector = htm.handDetector()

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    if len(lmList) != 0:
        # print(lmList[4], lmList[8])
        x1, y1 = lmList[4][1], lmList[4][2] # 4 index on hand
        x2, y2 = lmList[8][1], lmList[8][2] # 8 index on hand
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        # now drawing circle on two finger so that we get to visulazie our start and end point
        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
        # drawing the line between start and end point
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        # circle between line
        cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        # finding the length of line .. so that we can measure the volume and detect it..
        length = math.hypot(x2 - x1, y2 - y1)
        # print(length)

        # WKT Hand range 50 - 300
        # ALSO WKT Volume Range -65 - 0
        # Now we will convert hand to volume range
        vol = np.interp(length, [50, 300], [minVol, maxVol])
        volBar = np.interp(length, [50, 300], [400, 150]) # showing Volume bar so..it looks good
        volPer = np.interp(length, [50, 300], [0, 100]) # showing percentage of volume
        print(int(length), vol)
        volume.SetMasterVolumeLevel(vol, None)
        if length < 50:
            cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)
    cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX,
                1, (255, 0, 0), 3)
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX,
                1, (255, 0, 0), 3)
    cv2.imshow("Img", img)
    cv2.waitKey(1)

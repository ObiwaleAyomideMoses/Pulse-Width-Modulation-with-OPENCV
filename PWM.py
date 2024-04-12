import cv2
import numpy as np
import time
import HandTrackingModule as htm
import math
import json
import socketio

sio = socketio.Client()

# Define event handlers
@sio.event
def connect():
    print('Connected to server')
    sio.send('Hello, server!')
    send_sensor_data()

@sio.event
def disconnect():
    print('Disconnected from server')

@sio.event
def message(data):
    print('Received message:', data)

@sio.event
def my_response(data):
    print('Received response:', data)


def send_sensor_data(pwm_vale):
    try:
        # Simulate sensor data (replace with actual sensor data)
        sensor_data = {"pwm": str(pwm_vale), }

        # Convert sensor data to JSON string
        sensor_data_json = json.dumps(sensor_data)

        # Emit 'client-event' event with pwm data
        sio.emit('client-event', sensor_data)
        print('Sent sensor data to server:', sensor_data)
    except Exception as e:
        print('Error sending sensor data:', e)


# Connect to the server
sio.connect('https://esp32-socketio.onrender.com')


###########
wCam, hCam = 640, 480

cap = cv2.VideoCapture(0)

detector = htm.handDetector(detectionCon=0.7)

pTime = 0

while True:
    success, img = cap.read()
    img = detector.findHands(img, draw=False)
    lmList = detector.findPosition(img, draw=False)
    if len(lmList) != 0:
        # print(lmList[4], lmList[8])

        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        cv2.circle(img, (x1, y1), 7, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 7, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 2)
        cv2.circle(img, (cx, cy), 7, (255, 0, 255), cv2.FILLED)


        # Hand range 50 - 230
        # PWM range 0 - 255
        length = math.hypot(x2 - x1, y2 - y1)
        print(length)

        pwm = np.interp(length, [50, 230], [0, 255])
        print(pwm)
        send_sensor_data(int(pwm))
        if length < 31:
            cv2.circle(img, (cx, cy), 7, (0, 255, 0), cv2.FILLED)




    cap.set(3, wCam)
    cap.set(4, hCam)

    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    #
    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)

    cv2.imshow('image', img)
    cv2.waitKey(1)
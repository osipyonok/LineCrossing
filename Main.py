import argparse
import datetime
import time
import cv2
import imutils
from TrackedObject import *




NEW_OBJECT_THRESHOLD = 50
isFirst = True
trackedObjects = list()
total_cnt = 0
#VER
#A = (250, 0)
#B = (250, 500)
#HOR
A = (0, 160)
B = (500, 160)

def match(curObjects):
    global trackedObjects
    for i in range(0, len(trackedObjects)):
        trackedObjects[i].found = False
        trackedObjects[i].predict_next()


    for e in curObjects:
        opt_idx = -1
        opt_dist = 1e64

        for i in range(0, len(trackedObjects)):
            if trackedObjects[i].need:
                l = len(e.centers)
                cur_dist = dist(e.centers[l - 1], trackedObjects[i].next)

                if cur_dist < opt_dist:
                    opt_dist = cur_dist
                    opt_idx = i

        if opt_dist < NEW_OBJECT_THRESHOLD and opt_idx != -1:
            add(e , opt_idx)
        else:
            addNew(e)


    for i in range(0, len(trackedObjects)):
        global total_cnt
        total_cnt += trackedObjects[i].check_crossing(A, B)
        if not trackedObjects[i].found:
            trackedObjects[i].not_found_cnt = trackedObjects[i].not_found_cnt + 1
        else:
            trackedObjects[i].not_found_cnt = 0
        if trackedObjects[i].not_found_cnt >= 5:
            trackedObjects[i].need = False

def add(obj, pos):
    global trackedObjects
    trackedObjects[pos].contour = obj.contour
    trackedObjects[pos].boundingRect = obj.boundingRect

    l = len(obj.centers)
    trackedObjects[pos].centers.append(obj.centers[l - 1])

    trackedObjects[pos].diagonal = obj.diagonal
    trackedObjects[pos].aspect_ratio = obj.aspect_ratio

    trackedObjects[pos].need = True
    trackedObjects[pos].found = True

def addNew(obj):
    global trackedObjects
    obj.found = True
    trackedObjects.append(obj)



def main():
    global total_cnt
    global trackedObjects
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video", help = "Шлях до вiдео файлу")
    ap.add_argument("-a", "--min-area", type = int, default = 1000, help = "Мiнiмальна площа")
    args = vars(ap.parse_args())
    print(args)

    if args.get("video", None) is None:
        cam = cv2.VideoCapture(0)
        time.sleep(0.25)
    else:
        cam = cv2.VideoCapture(args["video"])

    firstFrame = None

    while 1:
        (flag, cur_frame) = cam.read()

        if not flag:
            break

        cur_frame = imutils.resize(cur_frame, width = 500)
     #   print(cur_frame.shape)
        gray = cv2.cvtColor(cur_frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (15, 15), 0)

        if firstFrame is None:
            firstFrame = gray

        delta = cv2.absdiff(gray, firstFrame)
        thresh = cv2.threshold(delta, 30, 255, cv2.THRESH_BINARY)[1]

        thresh = cv2.dilate(thresh, None, iterations = 2)
        (tmp, contours, tmp) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        curObjects = list()

        for c in contours:
            if cv2.contourArea(c) >= args["min_area"]:
                tmpObj = TrackedObject(c)
                curObjects.append(tmpObj)
                (x, y, w, h) = cv2.boundingRect(c)

        if len(trackedObjects) == 0:
            for el in curObjects:
                trackedObjects.append(el)
        else:
            match(curObjects)
         #   print(len(trackedObjects))

        for i in range(0, len(trackedObjects)):
            e = trackedObjects[i]
            if e.found:
                (x, y, w, h) = e.boundingRect
                cv2.rectangle(cur_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            #    cv2.putText(cur_frame, str(i), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)#obj number


        cv2.line(cur_frame, A, B, (255, 0, 0) , 3)
        cv2.putText(cur_frame, str(total_cnt), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        cv2.imshow("Security Feed", cur_frame)
        cv2.imshow("Thresh", thresh)
        cv2.imshow("Frame Delta", delta)
        #cv2.imshow("First", firstFrame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break
        time.sleep(0.07)

    cam.release()
    cv2.destroyAllWindows()


main()
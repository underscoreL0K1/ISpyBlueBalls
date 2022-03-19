import cv2
from networktables import NetworkTablesInstance, NetworkTables
import sys

#Initialize video capture
cap = cv2.VideoCapture(0)

cap.set(3, 640)
cap.set(4, 480)


NetworkTables.getDefault()
NetworkTables.initialize(server="10.18.7.2")
table = NetworkTables.getTable('SmartDashboard')
VisionTable = NetworkTables.getTable('Vision')



#frame = cv2.imread("balls.jpg")

#scaling fac tor



#create a seperate window named 'controls' for trackbar
#cv2.namedWindow('controls',2)
#cv2.resizeWindow("controls", 550,10)


#global variable
H_low = 0
H_high = 179
S_low= 0
S_high = 255
V_low= 0
V_high = 255
Xcord = 0
Ycord = 0




# Loop until you hit the Esc key
while True:

    ret, frame = cap.read()
    origionlIm = frame
    frame = cv2.GaussianBlur(frame, (7, 7), 0)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    #threshTest = cv2.inRange(frame, (H_low, S_low, V_low), (H_high, S_high, V_high))

    #Red Detection
    #frame = cv2.inRange(frame, (0, 3, 115), (10, 255, 255))

    if table.getString('Team', 0) == "Blue":
        frame = cv2.inRange(frame, (74, 69, 110), (117, 255, 255))
    #Blue Detection
    elif table.getString('Team', 0) == "Red":
        frame = cv2.inRange(frame, (146, 57, 0), (180, 255, 255))
    else:
        print("fuck")
   #
    thresh = frame
    try:


        cntss = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cntss[0] if len(cntss) == 2 else cntss[1]

        cnt = sorted(cnts, key=cv2.contourArea, reverse=False)


        for c in cnts:
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            ##cv2.circle(origionlIm, (int(x), int(y)), int(radius), (0, 255, 255), 2)
        ((xx, yy), rr) = cv2.minEnclosingCircle(max(cnts, key=cv2.contourArea))
        cv2.circle(origionlIm, (int(xx), int(yy)), int(rr), (0, 255, 255), 2)

        M = cv2.moments(max(cnts, key=cv2.contourArea))
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        cv2.circle(origionlIm, center, 5, (0, 0, 255), -1)
        cv2.circle(origionlIm, (int(xx), int(yy)), 6, (255, 0, 0), 2)
        Xcord = xx
        Ycord = yy
        hasTarget = True

    except:
        #print("Nothing To Target Found")
        Xcord = 999
        Ycord = 999
        hasTarget = False
    #finally:



    if Xcord != 999:
        table.putNumber('TargetX', Xcord - 320)

        #print(Xcord)
        #print(Ycord)
    print(NetworkTables.isConnected())

    #print(int(x) + ", " + int(y))
    cv2.imshow('Processed', origionlIm)
    #cv2.imshow('thresh', thresh)

   # cv2.imshow('Threshhold', thresh)

    # ret, frame = cap.read()
    c = cv2.waitKey(1)
    if c == 27:
        break
# Release the video capture object
cap.release()
# Close all active windows
cv2.destroyAllWindows()
print("worked")




from __future__ import division
import cv2
import numpy as np
import socket
import struct
import math
from networktables import NetworkTablesInstance, NetworkTables
import sys


class FrameSegment(object):
    """ 
    Object to break down image frame segment
    if the size of image exceed maximum datagram size 
    """
    MAX_DGRAM = 2**16
    MAX_IMAGE_DGRAM = MAX_DGRAM - 64 # extract 64 bytes in case UDP frame overflown
    def __init__(self, sock, port, addr="192.168.1.216"):
        self.s = sock
        self.port = port
        self.addr = addr

    def udp_frame(self, img):
        """ 
        Compress image and Break down
        into data segments 
        """
        compress_img = cv2.imencode('.jpg', img)[1]
        dat = compress_img.tostring()
        size = len(dat)
        count = math.ceil(size/(self.MAX_IMAGE_DGRAM))
        array_pos_start = 0
        while count:
            array_pos_end = min(size, array_pos_start + self.MAX_IMAGE_DGRAM)
            self.s.sendto(struct.pack("B", count) +
                dat[array_pos_start:array_pos_end], 
                (self.addr, self.port)
                )
            array_pos_start = array_pos_end
            count -= 1
NetworkTables.getDefault()
NetworkTables.initialize(server="10.18.7.2")
table = NetworkTables.getTable('SmartDashboard')
VisionTable = NetworkTables.getTable('Vision')
    


def main():
    """ Top level main function """
    # Set up UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    port = 5805

    fs = FrameSegment(s, port)

    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)
    while (cap.isOpened()):
        ret, frame = cap.read()
        origionlIm = frame
        frame = cv2.GaussianBlur(frame, (7, 7), 0)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        #threshTest = cv2.inRange(frame, (H_low, S_low, V_low), (H_high, S_high, V_high))

        #Red Detection
        #frame = cv2.inRange(frame, (0, 3, 115), (10, 255, 255))

        
       #
        thresh = frame
        try:
            frame = cv2.inRange(frame, (table.getNumber('Hl', 0), table.getNumber('Sl', 0), table.getNumber('Vl', 0)), (table.getNumber('Hh', 0), table.getNumber('Sh', 0), table.getNumber('Vh', 0)))

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
            table.putNumber('TargetY', Ycord - 240)

            #print(Xcord)
            #print(Ycord)
        print(NetworkTables.isConnected())
        print('TargetX', Xcord - 320)

        #print(int(x) + ", " + int(y))
        #cv2.imshow('Processed', origionlIm)
        fs.udp_frame(origionlIm)
    cap.release()
    cv2.destroyAllWindows()
    s.close()

if __name__ == "__main__":
    main()

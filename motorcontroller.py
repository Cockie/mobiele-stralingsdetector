# -*- coding: utf-8 -*-
import serial

class Motor:
    def __init__(self):
        #verbinding maken
        self.url='/dev/ttyACM1'
        self.rate=(9600)
        self.lspeed=0
        self.rspeed=0
        self.brake=True
        self.speed=0.0
        try:
            self.port=serial.Serial(self.url, self.rate, timeout=0)
        except Exception:
	    print "Connection Error"
            self.status=lambda : "Prut"
            self.Brake=lambda : "Stop"
            self.goBackward=lambda speed=255: "BW"
            self.goBackwardLeft=lambda speed=255,dif=155: "BWL"
            self.goBackwardRight=lambda speed=255,dif=155: "BWR"
            self.goForward=lambda speed=255: "FW"
            self.goForwardLeft=lambda speed=255,dif=155: "FWL"
            self.goForwardRight=lambda speed=255,dif=155: "FWR"
            self.RotateLeft=lambda speed=255: "RL"
            self.RotateRight=lambda speed=255: "RR"
            self.write=lambda left,right: "writing"
            self.speed=lambda speed=255: "whee!"

    def write(self,  right, left):
        """
        schrijft snelheden weg naar de Arduino
        """
        if right>0:
            newright=int((right-200)*self.speed+200)
        else:
            newright=int((right+200)*self.speed-200)
        if newright>255:
            newright=255
        elif newright < -255:
            newright=-255
        if left>0:
            newleft=int((left-200)*self.speed+200)
        else:
            newleft=int((left+200)*self.speed-200)
        if newleft>255:
            newleft=255
        elif newleft < -255:
            newleft=-255
        self.port.write(str(newleft)+','+str(newright)+'S')
        self.lspeed=left
        self.rspeed=right
        self.brake=False
	while(self.port.readline()):
            self.port.readline()

    def setSpeed(self, newspeed):
        self.speed=newspeed

    def status(self):
        """
        geeft huidige motorstatus terug
        """
        return (self.lspeed,self.rspeed,self.brake)
#rest van de functies is logisch
    def Brake(self):
        self.port.write('B')
        self.lspeed=0
        self.rspeed=0
        self.brake=True

    def goForward(self, speed=255):
        self.write(speed, speed)

    def goBackward(self, speed=255):
        self.write(-speed, -speed)

    def RotateRight(self, speed=255):
        self.write(speed, -speed)

    def RotateLeft(self, speed=255):
        self.write(-speed, speed)

    def goForwardLeft(self, speed=255, dif=155):
        self.write(speed-dif, speed)

    def goForwardRight(self, speed=255, dif=155):
        self.write(speed, speed-dif)

    def goBackwardLeft(self, speed=255, dif=155):
        self.write(-speed+dif, -speed)

    def goBackwardRight(self, speed=255, dif=155):
        self.write(-speed, -speed+dif)

# -*- coding: utf-8 -*-
import serial
import time
from random import randint, random
from numpy import arctan2, pi
class Sensor:
    url=''
    rate=0
    port=0
    connected=False

    def connect(self):
        """
        maak verbinding met de sensor
        """
        self.port=serial.Serial(self.url, self.rate, timeout=0)

    def __init__(self):
        self.url='/dev/tty'
        self.rate=19200
        self.connect(self)


    #leest de sensor uit en geeft de data terug als het gelukt is
    def read(self, data):
        return 0

    #genereert een string voor weergave van data in de gui op basis van een
    #data-array
    def generateOutput(self, data):
        return ''

#GPS-sensor
class GPS(Sensor):
    def __init__(self):
        self.url='/dev/ttyAMA0'
        self.rate=4800
        try:
            self.connect()
        except Exception:
            self.read=lambda data: False
            self.generateOutput=lambda data: "GPS N.C.\n"
        else:
            self.connected=True
            self.port.write("$PSRF103,01,00,00,01*25")
            self.port.write("$PSRF103,02,00,00,01*26")
            self.port.write("$PSRF103,03,00,00,01*27")
            self.port.write("$PSRF103,04,00,00,01*20")
            self.port.write("$PSRF103,05,00,00,01*21")

    def read(self, data):
	try:
            gpsoutput = self.port.readline()
	except Exception:
	    return False
        if gpsoutput:
            gpsoutput=gpsoutput.strip()
            gpsdata=gpsoutput.split(',')
            #andere protocollen overslaan
            if gpsdata[0]=='$GPGGA':
                #soms geeft de gps een set van lege data door
                if not (len(gpsdata)==1 or gpsdata[1]==''):
                    data["hours"]=int(gpsdata[1][0:2])
                    data["minutes"]=int(gpsdata[1][2:4])
                    data["seconds"]=float(gpsdata[1][4:10])

                    #check of er signaal is
                    if float(gpsdata[7])!=0:

                        data["latdeg"]=gpsdata[2][0:2]
                        data["latmin"]=gpsdata[2][2:10]
                        data["lator"]=gpsdata[3]

                        data["londeg"]=gpsdata[4][0:3]
                        data["lonmin"]=gpsdata[4][3:10]
                        data["lonor"]=gpsdata[5]

                        data["alt"]=gpsdata[9]
                        data["altu"]=gpsdata[10].lower()

                        data["satnum"]=gpsdata[7]
                        data["hdop"]=float(gpsdata[8])

                    return True
            else:
                self.read(data)
        else:
            return False

    def generateOutput(self, data):
        output=""
        output+='UTC: '
        output+=str(data["hours"])
        output+=' h '
        output+=str(data["minutes"])
        output+=' m '
        output+=str(data["seconds"])
        output+=' s'
        output+='\n'
        if float(data["satnum"])!=0:
            output+= 'Lat: '
            output+=str(data["latdeg"])
            output+=' deg '
            output+=str(data["latmin"])
            output+=' min '
            output+=str(data["lator"])
            output+='\n'
            output+= 'Long: '
            output+=str(data["londeg"])
            output+=' deg '
            output+=str(data["lonmin"])
            output+=' min '
            output+=str(data["lonor"])
            output+='\n'
            output+= 'MSL altitude '
            output+=str(data["alt"])
            output+=' '
            output+=str(data["altu"])
            output+='\n'
            output+=str(data["satnum"])
            output+=' satellites in use'
            output+='\n'
            output+= 'hdop '
            output+=str(data["hdop"])
            output+=': '
            if data["hdop"]==1:
                output+= 'ideal'
            elif data["hdop"]<2:
                output+= 'excellent'
            elif data["hdop"]<5:
                output+= 'good'
            elif data["hdop"]<10:
                output+= 'moderate'
            elif data["hdop"]<=20:
                output+= 'fair'
            else:
                output+= 'poor'
        else:
            output+= 'NO SIGNAL'
        output+='\n'
        return output

#Geiger-Müllerteller
class Geiger(Sensor):
    def __init__(self):
        self.url='/dev/ttyACM0'
        self.rate=19200
        try:
            self.connect()
        except Exception:
            self.read=self.RNG
            self.lastread=0
            self.generateOutput=lambda data: "N.C. "+str(data["cpm"])+" CPM\n"
        else:
            self.connected=True

    def read(self, data):
        readout=self.port.readline()
        if readout:
            try:
                data["cpm"]=int(readout)
                return True
            except Exception:
                return False
        else:
            return False

    def RNG(self, data):
	if (int(time.gmtime()[5])-self.lastread+100)%10==0:
            data["cpm"]=randint(0, 50)
            self.lastread=int(time.gmtime()[5])
            return True
	else:
	    return False

    def generateOutput(self, data):
        output='CPM: '
        output+=str(data["cpm"])
        output+='\n'
        return output

#Overige sensoren: proximity, kompas, licht, vochtigheid en de pan/tilt voor de camera
class ProMa(Sensor):
    def __init__(self):
        self.url='/dev/ttyACM2'
        self.rate=4800
        try:
            self.connect()
            self.port.readline()
            self.port.readline()
        except Exception:
            self.read=self.RNG
            self.generateOutput=lambda data: "N.C."
            self.pan=lambda angle: None
            self.tilt=lambda angle: None
        else:
            self.connected=True

	#servo voor pan roteren
    def pan(self, angle):
        self.port.write(str(angle)+'a'+'\n')

	#servo voor tilt roteren
    def tilt(self, angle):
        self.port.write(str(angle)+'b'+'\n')

    def read(self, data):
    	try:
    	    inputstr=self.port.readline()
    	except Exception:
    	    return False
        if inputstr:
            if inputstr.startswith('d'):
                inputstr=inputstr.split('&')
                if len(inputstr)<2:
                    return False
                inputstr[1]=inputstr[1].split(',')
                try:
                    angle=arctan2(float(inputstr[1][1]),float(inputstr[1][0]))
                    data["magn"]=angle
                except Exception:
                    pass
                inputstr[0]=inputstr[0].split(',')
                angle=int(inputstr[0][0].strip('d'))
                dist=float(inputstr[0][1])
                if data["prox"][0].count(angle)>0:
                    ind=data["prox"][0].index(angle)
                    data["prox"][1][ind]=dist
                else:
                    data["prox"][0].append(angle)
                    data["prox"][1].append(dist)
                return True
            elif inputstr.startswith('t'):
                print inputstr
                inputstr=inputstr.split(',')
                try:
                    data["temp"]=float(inputstr[0].strip('t'))
                    data["vocht"]=float(inputstr[1])
                    data["damp"]=float(inputstr[2])
                    data["licht"]=float(inputstr[3])
                except Exception:
		    return False
		return True
            else:
                return False
        else:
            return False

    def RNG(self, data):
        data["magn"]=random()*(2*pi)-pi
        for ind, stuff in enumerate(data["prox"][1]):
            data["prox"][1][ind]=randint(10,100)
        return True

    def generateOutput(self, data):
        output=""
        output+="Temperature: "
        output+=str(data["temp"])
        output+="°C"
        output+=" Humidity: "
        output+=str(data["vocht"])
        output+="%"
        output+=" Dew point: "
        output+=str(data["damp"])
        output+="°C"
        output+=" Light: "
        output+=str(data["licht"])
        output+="%"
        return output

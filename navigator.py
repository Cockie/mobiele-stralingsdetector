# -*- coding: utf-8 -*-
#navifatiepunten
import time
import numpy as np
class Navigator:
    def __init__(self):
        self.index=0
        self.navlist=[]
        self.status="Idle"
        #te tunen
        #minimum afstand tot te naderen punt in m
        #1 boogseconde=30.92 m
        self.tresshold=8
        #PID  constanten
        self.propgain=0.8
        self.intgain=0.2
        self.dergain=1
        self.multiplier=20
        #PID datavelden
        self.lasttime=0
        self.lastdbear=0
        self.cumsum=0

    def reset(self):
        self.lasttime=0
        self.lastdbear=0
        self.cumsum=0

    def getIndex(self):
        return self.index

    def getNavlist(self):
        return self.navlist

    def setNavlist(self, newnavlist):
        self.navlist=newnavlist
        self.index=0
        self.reset()

    def status(self):
        return self.status

    def navigate(self, data, motor):
        """
        Voer gps-navigatie uit
        """
        #navigatie gedaan?
        self.status="Navigating"
        if self.index>=len(self.navlist):
            motor.Brake()
            self.status="Destination reached"
        #voorlopig
        latf=np.deg2rad(float(self.navlist[self.index][0]))
        lonf=np.deg2rad(float(self.navlist[self.index][1]))
        lati=np.deg2rad((data["latdeg"]+data["latmin"]/60)*(-1 if data["lator"]=='S' else 1))
        loni=np.deg2rad((data["londeg"]+data["lonmin"]/60)*(-1 if data["lonor"]=='W' else 1))
        dlon=lonf - loni
        #checken of op bestemming
        dist=np.arccos( np.sin(lati)*np.sin(latf) + np.cos(lati)*np.cos(latf)*np.cos(dlon) )*6371*1000;
        if dist<=self.tresshold:
            #bestemming bereikt
            motor.Brake()
            self.index+=1
            if self.index<len(self.navlist):
                self.reset()
                self.status="Next waypoint"
        else:
            #gewenste richting uitrekenen
            y = np.sin(dlon)*np.cos(latf);
            x = np.cos(lati)*np.sin(latf) - np.sin(lati)*np.cos(latf)*np.cos(dlon);
            bearf = np.arctan2(y, x)
            dbear=bearf-data["magn"]
            dtime=time.time()-self.lasttime
            if self.lasttime==0:
                output=self.propgain*dbear*self.multiplier
            else:
                self.cumsum+=dbear*dtime
                output=self.multiplier*(self.propgain*dbear+self.intgain*self.cumsum+self.dergain*(dbear-self.lastdbear)/dtime)
            self.lasttime=time.time()
            self.lastdbear=dbear
            if output>0:
                motor.goForwardRight(dif=output)
            elif output<0:
                motor.goForwardLeft(dif=-output)

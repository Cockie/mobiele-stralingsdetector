# -*- coding: utf-8 -*-
import time

def parsegpx(filename):
    """
    leest een gpx-file in en geeft een array van (latitude,longitude) tupels terug
    """
    lat=[]
    lon=[]
    f=open(filename, 'r')
    for line in f:
        if line.count('lat')!=0:
            parts=line.split('\"')
            for i in xrange(0,len(parts)):
                if parts[i].count('lat')==1:
                    lat.append(parts[i+1])
                elif parts[i].count('lon')==1:
                    lon.append(parts[i+1])
    data=[(lat[i], lon[i]) for i,value in enumerate(lat)]
    return data

def start():
    """
    maakt en opent een gpx-file waar de meetgegevens naar geschreven zullen worden
    """
    date=time.gmtime()
    filename='strd-'+str(date[0])+'-'+str(date[1])+'-'+str(date[2])+'--'+str(date[3])+'-'+str(date[4])+'.gpx'
    f=open(filename, 'w')
    f.write("<?xml version=\"1.0\"?>")
    f.write('\n')
    f.write("<gpx version=\"1.0\" creator=\"Stralingsdetector\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns=\"http://www.topografix.com/GPX/1/0\" xsi:schemaLocation=\"http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd\">")
    f.write('\n')
    f.write("<trk>")
    f.write('\n')
    f.write("<name>")
    f.write(filename)
    f.write("</name>")
    f.write('\n')
    f.write("<trkseg>")
    f.write('\n')
    return f

def stop(f):
    """
    finaliseert en sluit het gegevensbestand
    """
    f.write("</trkseg>")
    f.write('\n')
    f.write("</trk>")
    f.write('\n')
    f.write("</gpx>")
    f.write('\n')
    f.close()

def printData(data, f):
    """
    voegt een lijn data toe aan het bestand
    """
    f.write("<trkpt lat=\"")
    if data["lator"]!='N':
        f.write('-')
    f.write(str(data["latdeg"]+60*data["latmin"]))
    f.write("\" lon=\"")
    if data["lonor"]!='O':
        f.write('-')
    f.write(str(data["londeg"]+60*data["lonmin"]))
    f.write('\">')
    f.write('\n')
    f.write("<ele>")
    f.write(str(data["cpm"]))
    f.write("</ele>")
    f.write('\n')
    f.write("<time>")
    date=time.gmtime()
    f.write(str(date[0]))
    f.write('-')
    f.write(str(date[1]))
    f.write('-')
    f.write(str(date[2]))
    f.write('T')
    f.write(str(data["hours"]))
    f.write(':')
    f.write(str(data["minutes"]))
    f.write(':')
    f.write(str(data["seconds"]))
    f.write('Z')
    f.write("</time>")
    f.write('\n')
    f.write("</trkpt>")
    f.write('\n')

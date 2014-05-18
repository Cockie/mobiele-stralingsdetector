# -*- coding: utf-8 -*-
"""
main program
"""
import Tkinter as Tk
import tkFileDialog
import matplotlib
matplotlib.use('TkAgg')
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from numpy import pi
from PIL import Image, ImageTk
import io
import thread
import os

import gpxparser
import motorcontroller
import sensor
import navigator

try:
    import picamera
except Exception:
    CAMERA = False
else:
    try:
        camera=picamera.PiCamera()
        camera.resolution = (400, 300)
    except Exception:
        CAMERA = False
    else:
        CAMERA = True

motor = motorcontroller.Motor()
navi = navigator.Navigator()
#sensoren
sensoren = {}
sensoren["gps"] = sensor.GPS()
sensoren["geiger"] = sensor.Geiger()
sensoren["proma"] = sensor.ProMa()

#IO
f = gpxparser.start()


def quitprogram():
    """
    schrijf het einde aan de gpxfile, stopt de auto en sluit af
    """
    global f
    gpxparser.stop(f)
    motor.Brake()
    root.destroy()

#sensorvariabelen
data = {}
data["cpm"] = 0
data["hours"] = 0
data["minutes"] = 0
data["seconds"] = 0
data["latdeg"] = 0
data["latmin"] = 0
data["lator"] = ""
data["londeg"] = 0
data["lonmin"] = 0
data["lonor"] = ""
data["alt"] = 0
data["altu"] = ""
data["satnum"] = 0
data["hdop"] = 0
data["prox"] = [[30,60,90,120,150], [10, 10, 10, 10, 10]]
data["magn"] = 0
data["dir"] = 0
data["temp"]=0
data["vocht"]=0
data["damp"]=0
data["licht"]=0
#geigertellergeschiedenis
hist = [0]*100

#gui
root = Tk.Tk()
root.minsize(800, 600)
root.attributes('-zoomed', True)
root.wm_title("Mobiele stralingsdetector")

#besturingsvariabelen
bestmodus = Tk.IntVar()
bestmodus.set(1)
direction = Tk.IntVar()
direction.set(1)
panpos=90
tiltpos=180
lspeed = 0
rspeed = 0
brake = False

'''--------------Output rechts----------------------------'''
frameright = Tk.Frame(root, relief=Tk.SUNKEN, bd=1)
frameright.pack(side=Tk.RIGHT, fill=Tk.BOTH, expand=1)
outputtxt = Tk.Label(frameright, text="Starting...")
outputtxt.pack(side=Tk.TOP)

#plotgedoe
fig = Figure(figsize=(6, 2), dpi=100)
subp = fig.add_subplot(111)
plot, = subp.plot(hist, 'r-') #komma is geen typfout
subp.set_title('CPM history')
subp.set_xlabel('Time')
subp.set_ylabel('CPM')
canvas = FigureCanvasTkAgg(fig, master=frameright)
canvas.show()
canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

dir = os.path.dirname(__file__)
filename = os.path.join(dir, "test.gif")
photo = Tk.PhotoImage(file=filename)
photolabel = Tk.Label(image=photo, height=300, width=400, master=frameright)
photolabel.image = photo # keep a reference!
photolabel.pack()

quitb = Tk.Button(master=frameright, text='Quit', command=quitprogram)
quitb.pack(side=Tk.BOTTOM)

'''--------------Besturing links----------------------------'''

frameleft = Tk.Frame(root, relief=Tk.SUNKEN, bd=1)
frameleft.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=1)
Tk.Label(frameleft, text="Besturing").pack(side=Tk.TOP)
manb = Tk.Radiobutton(frameleft, text="Manuele besturing", variable=bestmodus, value=1)
manb.pack()
manb.select()
gpsb = Tk.Radiobutton(frameleft, text="GPS-besturing", variable=bestmodus, value=2)
gpsb.pack()
Tk.Canvas(frameleft, height=20).pack(side=Tk.TOP, fill=Tk.X)
lstxt = Tk.Label(frameleft, text="Speed left:")
lstxt.pack(side=Tk.TOP)
rstxt = Tk.Label(frameleft, text="Speed right:")
rstxt.pack(side=Tk.TOP)

pane1 = Tk.Frame(frameleft, relief=Tk.SUNKEN, bd=1)
pane1.pack(fill=Tk.BOTH, expand=1, side=Tk.TOP)
controlwindow = Tk.Frame(pane1, bd=1)
controlwindow.pack(fill=Tk.BOTH, expand=1, side=Tk.TOP)
dist = Tk.Frame(pane1, bd=1)
dist.pack(fill=Tk.BOTH, expand=1, side=Tk.TOP)

pane2 = Tk.Frame(frameleft, relief=Tk.SUNKEN, bd=1)
pane2.pack(fill=Tk.BOTH, expand=1, side=Tk.TOP)

leftf = Tk.Frame(controlwindow, bd=0)
leftf.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=1)
middlef = Tk.Frame(controlwindow, bd=0)
middlef.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=1)
rightf = Tk.Frame(controlwindow, bd=0)
rightf.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=1)
speedf = Tk.Frame(controlwindow, bd=0)
speedf.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=1)
pantiltf = Tk.Frame(controlwindow, bd=0)
pantiltf.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=1)

#knoppen
fb = Tk.Radiobutton(middlef, text="FW", variable=direction, value=1, indicatoron=0)
frb = Tk.Radiobutton(rightf, text="FR", variable=direction, value=2, indicatoron=0)
rb = Tk.Radiobutton(rightf, text="R", variable=direction, value=3, indicatoron=0)
brb = Tk.Radiobutton(rightf, text="BR", variable=direction, value=4, indicatoron=0)
bb = Tk.Radiobutton(middlef, text="BW", variable=direction, value=5, indicatoron=0)
blb = Tk.Radiobutton(leftf, text="BL", variable=direction, value=6, indicatoron=0)
lb = Tk.Radiobutton(leftf, text="L", variable=direction, value=7, indicatoron=0)
flb = Tk.Radiobutton(leftf, text="FL", variable=direction, value=8, indicatoron=0)
stb = Tk.Radiobutton(middlef, text="STP", variable=direction, value=0, indicatoron=0)

flb.pack(fill=Tk.BOTH, expand=1)
fb.pack(fill=Tk.BOTH, expand=1)
frb.pack(fill=Tk.BOTH, expand=1)
lb.pack(fill=Tk.BOTH, expand=1)
stb.pack(fill=Tk.BOTH, expand=1)
rb.pack(fill=Tk.BOTH, expand=1)
blb.pack(fill=Tk.BOTH, expand=1)
bb.pack(fill=Tk.BOTH, expand=1)
brb.pack(fill=Tk.BOTH, expand=1)
stb.select()

#speed slider
speeds = Tk.Scale(speedf, from_=1, to=0, resolution=0.1, length=350, width=40)
speeds.pack(fill=Tk.BOTH)
speeds.set(0)

#pan/tilt sliders
tilts = Tk.Scale(pantiltf, from_=0, to=180, length=200, width=30, resolution=10)
tilts.pack()
tilts.set(180)

pans = Tk.Scale(pantiltf, from_=180, to=0, orient=Tk.HORIZONTAL, length=200, width=30, resolution=10)
pans.pack()
pans.set(90)

#prox plot
fig2 = Figure(figsize=(2, 2), dpi=100)
subp2 = fig2.add_subplot(111, polar=True)
subp2.grid(True)
plot2, = subp2.plot([x*2*pi/360 for x in data["prox"][0]], data["prox"][1], 'b-') #komma is geen typfout
subp2.set_title('Distance\n')
canvas2 = FigureCanvasTkAgg(fig2, master=dist)
canvas2.show()
canvas2.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
canvas2._tkcanvas.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=1)

#haal commentaar weg om een kompas te plotten
#standaard uitgeschakeld omdat plotten de cpu vrij zwaar belast
'''
#magn plot
fig3 = Figure(figsize=(2, 2), dpi=100, rasterized=True)
subp3 = fig3.add_subplot(111, polar=True)
subp3.grid(True)
plot3, = subp3.plot([0, -data["magn"]], [0, 1], 'b-') #komma is geen typfout
subp3.set_title('Heading')
canvas3 = FigureCanvasTkAgg(fig3, master=dist)
axis = canvas3.figure.axes[0]
axis.set_theta_zero_location("N")
axis.set_theta_direction(-1)
canvas3.show()
canvas3.get_tk_widget().pack(side=Tk.RIGHT, fill=Tk.BOTH, expand=1)
#toolbar = NavigationToolbar2TkAgg( canvas, frameright )
#toolbar.update()
canvas3._tkcanvas.pack(side=Tk.RIGHT, fill=Tk.BOTH, expand=1)
'''
#gps navigatieknoppen
navlist = Tk.Listbox(pane2)
navlist.pack()

def openFile():
    global navi
    global navlist
    file_path = tkFileDialog.askopenfilename()
    navi.setNavlist(gpxparser.parsegpx(file_path))
    navlist.delete(0, Tk.END)
    for x,y in navi.getNavlist():
        navlist.insert(Tk.END, str(x)+","+str(y))
    navlist.selection_set(0)

openfileb = Tk.Button(pane2, text="Open track", command=openFile)
openfileb.pack()



if CAMERA:
    def takePicture():
        """
        neem een foto
        """
        global photo
        stream=io.BytesIO()
        camera.capture(stream, format='jpeg')
        stream.seek(0)
        image=Image.open(stream)
        photo=ImageTk.PhotoImage(image)
else:
    def takePicture():
        """
        geen camera, dus doe niks
        """
        return

#update gui
def changeOutput(prox, geiger):
    """
    update alle velden en grafieken
    """
    global photo
    global photolabel
    global data
    if CAMERA and camera:
        photolabel.config(image=photo, height=300, width=400)
        photolabel.image = photo

    newprint = ""
    newprint += sensoren["gps"].generateOutput(data)
    newprint += sensoren["geiger"].generateOutput(data)
    newprint += sensoren["proma"].generateOutput(data)
    outputtxt.config(text = newprint)

    newprint = "Speed left:"
    newprint += str(lspeed)
    lstxt.config(text = newprint)
    newprint = "Speed right:"
    newprint += str(rspeed)
    rstxt.config(text = newprint)
 
    if geiger:
        global canvas
        global plot
        global hist
        H = np.array(hist)
        plot.set_ydata(H)
        ax = canvas.figure.axes[0]
        ax.set_ylim(0, H.max() if H.max()!=0 else 20)
        thread.start_new_thread(canvas.draw,())
 
    if prox:
        global canvas2
        global plot2
        global subp2
        H = np.array(data["prox"][1])
        try:
            a = H.max()
        except Exception:
            a = 20
        plot2.set_ydata(H)
        ax = canvas2.figure.axes[0]
        ax.set_rmax(a if a!=0 else 20)
        thread.start_new_thread(canvas2.draw,())
 
    #wederom commentaar weghalen voor een plot van het kompas
    '''
    global canvas3
    global plot3
    H = np.array(data["magn"])
    plot3.set_xdata(H)
    canvas3.draw()'''
 
def drive():
    """
    Verander de richting van de auto
    """
    global direction
    global rspeed
    global lspeed
    global brake
    if direction.get() == 0 and data["dir"]!=0:
        motor.Brake()
        data["dir"]=0
    elif direction.get() == 1 and data["dir"]!=1:
        motor.goForward()
        data["dir"]=1
    elif direction.get() == 2 and data["dir"]!=2:
        motor.goForwardRight()
        data["dir"]=2
    elif direction.get() == 3 and data["dir"]!=3:
        motor.RotateRight()
        data["dir"]=3
    elif direction.get() == 4 and data["dir"]!=4:
        motor.goBackwardRight()
        data["dir"]=4
    elif direction.get() == 5 and data["dir"]!=5:
        motor.goBackward()
        data["dir"]=5
    elif direction.get() == 6 and data["dir"]!=6:
        motor.goBackwardLeft()
        data["dir"]=6
    elif direction.get() == 7 and data["dir"]!=7:
        motor.RotateLeft()
        data["dir"]=7
    elif direction.get() == 8 and data["dir"]!=8:
        motor.goForwardLeft()
        data["dir"]=8
    status = motor.status()
    lspeed = status[0]
    rspeed = status[1]
    brake = status[2]
 
def task():
    """
    Loop, lees sensoren en update
    """
    global data
    global f
    global hist
    global motor
    geiger=False
    prox=False
    #auto besturen
    motor.speed(speeds.get())
    if bestmodus.get()==1:
        drive()
    else:
        navi.navigate(data, motor)
    #foto nemen
    takePicture()
    #geigerteller uitlezen (moet eerst voor grafiek)
    if sensoren["geiger"].read(data):
        newcpm = data["cpm"]
    else:
        newcpm=False
    if newcpm:
        geiger=True
        hist.append(newcpm)
        hist.pop(0)
        gpxparser.printData(data, f)
    #sensoren uitlezen
    for key, sensor in sensoren.iteritems():
        sensor.read(data)
    #dataveld aanpassen en grafieken herplotten
    changeOutput(prox, geiger)
    #pan/tilt verzetten
    if panpos!=pans.get():
        panpos=pans.get()
        sensoren["proma"].pan(pans.get())
    if tiltpos!=tilts.get():
        tiltpos=tils.get()
        sensoren["proma"].tilt(tilts.get())
    root.after(50, task)  # reschedule event

sensoren["proma"].tilt(tiltpos)
task()
root.mainloop()

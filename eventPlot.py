"""
  @package
  @file eventFitsPlot.py
  @brief plot the optical digram

  @brief Created by:
  @author Jun Cheng (Purdue), En-Hsin (Purdue)

  @warning This code is not fully validated
  and not ready for full release.  Please
  treat results with caution.

Usage: python eventFitsPlot.py eventFile.fits percentage

Notes: 1. Plot only part of the photons with 'percentage'

"""
import sys,os,commands
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from mpl_toolkits.mplot3d import Axes3D
from mayavi import mlab
#from mayavi.mlab import *



class photon(object):
    def  __init__(self):
        self.wavelength = 0
        self.numLayer = 0
        self.xdir = 0
        self.ydir = 0
        self.time = 0
        self.listX = []
        self.listY = []
        self.listZ = []
        self.listLayer = []
        self.opticX = []
        self.opticY = []
        self.opticZ = []

    def printPhoton(self):
        print "****************************PHOTON*********************************"
        print "wavelength " , self.wavelength
        print "X-direction ", self.xdir
        print "Y-direction ", self.ydir
        print "time ", self.time
        print "number of Layers ", self.numLayer
        print "*******"
        for i in range(0, self.numLayer):
            print self.listLayer[i], self.listX[i], self.listY[i], self.listZ[i]
        #print "******************************************************************"


class Surface(object): 
    # surface constructor: read one line for a specific surface
    def __init__(self, line): 
        self.name = line[0]
        self.type = line[1]
        self.curvature = float(line[2])
        self.thickness = float(line[3])
        self.outerRadius = float(line[4])
        self.innerRadius = float(line[5])
        self.conic = float(line[6])
        self.aspheric3 = float(line[7])
        self.aspheric4 = float(line[8])
        self.aspheric5 = float(line[9])
        self.aspheric6 = float(line[10])
        self.aspheric7 = float(line[11])
        self.aspheric8 = float(line[12])
        self.aspheric9 = float(line[13])
        self.aspheric10 = float(line[14])
        self.coatingFile = line[15]
        self.mediaFile = line[16]   
    def plotSurface(self, globalZ): 
        if(self.type!="det"):# or self.name=="lens"): 
            r, theta = np.mgrid[self.innerRadius:self.outerRadius:100j, -np.pi:np.pi:100j]
            x = r*np.cos(theta)
            y = r*np.sin(theta)

            r = np.sqrt(x**2 + y**2)
            if self.curvature<1.0e-12:
                z = globalZ + r*0
            else:
                z = globalZ + r**2/(self.curvature*(1+np.sqrt(1-(1+self.conic)*r**2/(self.curvature**2))))+r**3*self.aspheric3 + r**4*self.aspheric4
            if self.type=="filter": 
                mlab.mesh(x,y,z, opacity=0.3, color = (1,1,0))
            elif self.type=="none":
                mlab.mesh(x,y,z, opacity=0.05, color=(1,1,1))
            else:
                mlab.mesh(x,y,z, opacity=1.0, color=(0.9,0.9,0.9), colormap="Pastel2")
            mlab.show()
                
class Chip(object): 
        def __init__(self,line): 
            self.name = line[0]
            self.centerX = float(line[1])   # unit micro
            self.centerY = float(line[2])   # unit micro
            self.pixelSize = float(line[3])
            self.numX = float(line[4])
            self.numY = float(line[5])

            self.halfX = self.pixelSize *self.numX/2
            self.halfY = self.pixelSize *self.numY/2
        def plotChip(self, pos): 
            x, y = np.mgrid[-self.halfX:self.halfX:10j, -self.halfY:self.halfY:10j]
            x = (x+self.centerX)/1000
            y = (y+self.centerY)/1000
            z= x-x+pos
            mlab.mesh(x,y,z, opacity = 0.95, color=(0.1,0.1,0.1))
            mlab.show()
            



def readConfig(fileName):
    f = open(fileName,"r")
    config = {}
    for line in f:
        if line[0]!='#':# and not line.strip():
            tok = line.split()
            if len(tok)<2:
                continue
            config[tok[0]] = tok[1]
    if config["instrumentPath"][-1]!="/":       
        config["instrumentPath"] += "/"
    path = config["instrumentPath"]
    if "opticsFile" in config:
        config["opticsFile"] = path + config["opticsFile"] 
    if "focalplaneFile" in config:
        config["focalplaneFile"] = path + config["focalplaneFile"]
    if "segmentationFile" in config:
        config["segmentationFile"] = path + config["segmentationFile"] 

    return config

def readEvents(config):
    eventFits = config["eventFile"] #"output.fits"
    per = config["percentage"]
    f= fits.open(eventFits)
    event=f[1].data
    #print event.field
    xpos = []
    ypos = []
    zpos = []
    wavelength = []
    numLine = len(event.field(0))
    # set a small number for test.
    numLine = 10000
    numPhoton = 0
    photonList = []
    pre_p = photon()
    for i in range(0, numLine):
        if event.field(3)[i]==0:

            if i!=0:
                pre_p.numLayer=numLayer
                photonList.append(pre_p)
            numLayer = 0
            numPhoton += 1
            p = photon()
            p.wavelength = event.field(2)[i]
            p.xdir = event.field(0)[i]
            p.ydir = event.field(1)[i]
        elif event.field(3)[i]==1:
            p.time = event.field(0)[i]
        else :
            numLayer += 1
            p.listX.append(event.field(0)[i])
            p.listY.append(event.field(1)[i])
            p.listZ.append(event.field(2)[i])
            p.listLayer.append(event.field(3)[i])

        pre_p = p

    photonList.append(p)

    plotPhoton= int(float(per) * numPhoton)
    print plotPhoton, "out of", numPhoton

    for i in range(0,plotPhoton):
        length = len(photonList[i].listZ)
        if length > 8 :
            for n in range(8,length-2):
                mlab.plot3d(photonList[i].listX[n:2+n], photonList[i].listY[n:2+n],photonList[i].listZ[n:2+n],color=(1, 0.5, 0.5),
                        opacity=0.2, tube_radius=None)
    mlab.show()

def readOptics(config): 
    opticsFile = config["opticsFile"]
    height=0.0
    surfaces = []
    for line in open(opticsFile).readlines():
        if line[0]!= "#": 
            temp = line.split()
            surfaces.append(Surface(temp))
     
    globalZ=0
    for i in range(len(surfaces)): 
        globalZ += surfaces[i].thickness
        surfaces[i].plotSurface(globalZ)
    return globalZ

def readChips(config, detPosition): 
    layoutFile = config["focalplaneFile"]
    ampFile = config["segmentationFile"]
    chips = []
    for line in open(layoutFile).readlines():
        if line[0]!="#":
            temp = line.split()
            chips.append(Chip(temp))
    for i in range(len(chips)):
        chips[i].plotChip(detPosition)  



def main():
    configFileName = "/Users/cheng109/work/EventPlot/configuration.txt"
    #configFileName = sys.argv[1]
    config = readConfig(configFileName)
    if "opticsFile" in config: 
        detPosition = readOptics(config)
    if "focalplaneFile" in config:
        readChips(config,detPosition)
    if "eventFile" in config: 
        readEvents(config)
    
if __name__ == "__main__":
        main()

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
import os,sys
import numpy as np
from astropy.io import fits
from mayavi import mlab

def EulerRotation(phi,psi,theta): 
    phi, psi, theta = np.deg2rad(phi), np.deg2rad(psi), np.deg2rad(theta)
    matrixD = np.matrix([[np.cos(phi), np.sin(phi), 0], [-np.sin(phi), np.cos(phi), 0], [0, 0, 1]])
    matrixC = np.matrix([[1, 0, 0], [0, np.cos(theta), np.sin(theta)], [0, -np.sin(theta), np.cos(theta)]])
    matrixB = np.matrix([[np.cos(psi), np.sin(psi), 0], [-np.sin(psi), np.cos(psi), 0], [0, 0, 1]])   
    return matrixB * matrixC * matrixD

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
                mlab.mesh(x,y,z, opacity=1.0, color=(0.9,0.9,0.9), colormap="Accent")
            #mlab.show()

# def plotBox(x, y, z, dz): 
    
#     #mlab.mesh(x,z, y, opacity = 0.8, color=(0.3,0.3,0.3)); 
    # plot side 1; 
   

# def performRotationTranformation(x, y, z, phi, psi, theta, halfX, halfY, deltaZ):
#     M =  EulerRotation(phi, psi, theta)
#     new_x, new_y, new_z = x, y, z   

#     for i in range(x.shape[0]): 
#         for j in range(x.shape[1]): 
#             result = M * np.matrix([[x[i][j]], [y[i][j]], [z[i][j]]])
#             new_x[i][j], new_y[i][j], new_z[i][j] = result[0][0], result[1][0], result[2][0]                   
#             x = (new_x+centerX)/1000 + shiftX     # unit mm 
#             y = (new_y+centerY)/1000 + shiftY     # unit mm 
#             z =   new_z+deltaZ + self.shiftZ + self.deltaZ/1000 # unit mm
#     return x, y, z

             
class Chip(object): 
        def __init__(self,line): 
            self.name = line[0]
            self.centerX   = float(line[1])   # unit micron
            self.centerY   = float(line[2])   # unit micron
            self.pixelSize = float(line[3])
            self.numX      = float(line[4])
            self.numY      = float(line[5])
            self.thickness = float(line[8])    # unit micron
            self.phi       = float(line[10])
            self.psi       = float(line[11]) 
            self.theta     = float(line[12])
            
            self.shiftX    = float(line[13])
            self.shiftY    = float(line[14])
            self.shiftZ    = float(line[15])

            self.deltaZ    = float(line[17])  # for wavefront sensor delta z shift

            self.halfX     = self.pixelSize *self.numX/2
            self.halfY     = self.pixelSize *self.numY/2
            self.halfZ     = self.thickness/2

            self.centerZ   = 0

        def plotChip(self, pos): 
            M = EulerRotation(self.phi, self.psi, self.theta)
            self.centerZ   = 1000*pos + self.thickness/2   # unit micron
            opacity = 1.0
            color = (0.3,0.3,0.3)
            ###############  Group1  ###############
            x, y = np.mgrid[-self.halfX:self.halfX:10j, -self.halfY:self.halfY:10j]
            z = x-x
            tempX, tempY, tempZ = x, y, z   
            for i in range(x.shape[0]): 
                for j in range(x.shape[1]): 
                    result = M * np.matrix([[x[i][j]], [y[i][j]], [z[i][j]]])
                    tempX[i][j], tempY[i][j], tempZ[i][j] = result[0][0], result[1][0], result[2][0]                   
            x = (tempX+self.centerX)/1000 + self.shiftX     # unit mm 
            y = (tempY+self.centerY)/1000 + self.shiftY     # unit mm 
            z = (tempZ+self.centerZ)/1000 + self.shiftZ - self.deltaZ/1000 # unit mm
            mlab.mesh(x,y, z-self.halfZ/1000, opacity = opacity, color=color); 
            mlab.mesh(x,y, z+self.halfZ/1000, opacity = opacity, color=color); 

            ###############  Group2  ###############
            x, z = np.mgrid[-self.halfX:self.halfX:10j, -self.halfZ:self.halfZ:10j]
            y = x-x
            tempX, tempY, tempZ = x, y, z   
            for i in range(x.shape[0]): 
                for j in range(x.shape[1]): 
                    result = M * np.matrix([[x[i][j]], [y[i][j]], [z[i][j]]])
                    tempX[i][j], tempY[i][j], tempZ[i][j] = result[0][0], result[1][0], result[2][0]                   
            x = (tempX+self.centerX)/1000 + self.shiftX     # unit mm 
            z = (tempZ+self.centerZ)/1000 + self.shiftZ - self.deltaZ/1000    # unit mm 
            y = (tempY+self.centerY)/1000 + self.shiftY  # unit mm
            mlab.mesh(x,y-self.halfY/1000, z, opacity = opacity, color=color); 
            mlab.mesh(x,y+self.halfY/1000, z, opacity = opacity, color=color); 

            ###############  Group3  ###############
            y, z = np.mgrid[-self.halfY:self.halfY:10j, -self.halfZ:self.halfZ:10j]
            x = y-y
            tempX, tempY, tempZ = x, y, z   
            for i in range(x.shape[0]): 
                for j in range(x.shape[1]): 
                    result = M * np.matrix([[x[i][j]], [y[i][j]], [z[i][j]]])
                    tempX[i][j], tempY[i][j], tempZ[i][j] = result[0][0], result[1][0], result[2][0]                   
            x = (tempX+self.centerX)/1000 + self.shiftX     # unit mm 
            z = (tempZ+self.centerZ)/1000 + self.shiftZ - self.deltaZ/1000    # unit mm 
            y = (tempY+self.centerY)/1000 + self.shiftY  # unit mm
            mlab.mesh(x-self.halfX/1000,y, z, opacity = opacity, color=color); 
            mlab.mesh(x+self.halfX/1000,y, z, opacity = opacity, color=color); 



            #mlab.mesh(x,y,z, opacity = 1.0, color=(0.3,0.3,0.3))
            #mlab.show()
            
def updatePath(oldPath): 
    # if it is relative path, convert to full path
    newPath = oldPath
    if not os.path.exists(oldPath): 
        newPath = os.path.join(os.path.dirname(__file__), oldPath)
    return newPath


def readConfig(fileName):
    f = open(fileName,"r")
    config = {}
    eventFileList = []
    for line in f:
        if line[0]!='#':# and not line.strip():
            tok = line.split()
            if len(tok)<2:
                continue
            if(tok[0]=="eventFile"):                 
                eventFileList.append(updatePath(tok[1]))
            else:
                config[tok[0]] = tok[1]
    config["eventFile"] = eventFileList


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

def readMultpleEvents(config): 
    # read multiple event file
    for eventFits in config["eventFile"]: 
        readEvents(eventFits, config["percentage"])


def readEvents(eventFits, per):
    # read a single event file; 
    #eventFits = config["eventFile"] #"output.fits"
    #per = config["percentage"]
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
            for n in range(8,length):
                mlab.plot3d(photonList[i].listX[n:2+n], photonList[i].listY[n:2+n],photonList[i].listZ[n:2+n],color=(1, 0.5, 0.5),
                        opacity=0.2, tube_radius=None)
    #mlab.show()

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
    #configFileName = "/Users/cheng109/work/EventPlot/configuration.txt"
    detPosition = 0 
    configFileName = sys.argv[1]
    config = readConfig(configFileName)
    mlab.figure(bgcolor=(0.5,0.3,0.8))
    if "opticsFile" in config: 
        detPosition = readOptics(config)
    if "focalplaneFile" in config:
        readChips(config,detPosition)
    if "eventFile" in config: 
        readMultpleEvents(config)
    
    mlab.show()
    
if __name__ == "__main__":
    main()

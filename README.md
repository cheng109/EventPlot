# EventPlot
[PhoSim] Plot instruments and photon raytrace

--------------
Installation: 
--------------
The required packages include "mayavi" and "astropy". 
The best solution to install "mayavi" and "astropy" is to use the full Python distribution Enthought Canopy (available for Windows, MacOSX, and Linux)

Step 1.  Download Enthought Canopy, and install it. 

Step 2.  Open Canopy, go to "Tools"----> "Package Manager".  Search for "astropy" and click "free install"

Step 3.  Follow the same procedure, search for "mayavi" and click "free install" 


--------------
Usage: 
--------------
Go to "Canopy"---->"Tools" -----> "Canopy Terminal" 
> python eventPlot.py config.txt

------------------
Run the examples:
------------------
Two examples are included in the examples directory: LSST and DES. 
Before you run the examples, you should specify "instrumentPath" and "eventFile" location in the configure files. 

For LSST:  
> python eventPlot.py examples/config_lsst.txt

For DES: 
> python eventPlot.py examples/config_deCam.txt

---------------------------------
Using the latest stable version
---------------------------------
> git clone https://github.com/cheng109/EventPlot.git

> git tag -l

> git checkout tags/v1.1







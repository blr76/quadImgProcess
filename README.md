# quadImgProcess
Script How-to, Updated 3.22.18

The script’s current name is quadMergeNDVI.py, save this to any local directory. 

This script is invoked via command line and takes the directory path containing the four folders that make up the whole quad as an argument. 

This is the path the script 	This is the path to the quad directory
 
The script will ONLY process rasters in the quarter quad directories 
		County->Quad->QuarterQuad->raster.img
    
If the directory structure is different from this, the quad will have to be manually processed for now.

	The output name is pulled from the quad directory name and product name appended.
		 
	If a different name is required it will have to be manually renamed.

If there is issues with the copying either to or from the network location, map the 1_NAIP_Imagery directory to a new drive 
 
Other issues with data transfers will most likely be caused by the SLOW read times form the network location.

If you would like to batch process, an example of how the bat file would be produced is provided below
 
	


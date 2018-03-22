import os, arcpy, sys, tempfile, shutil, datetime

#testing git

def mosaicRasters(rasterList, outputDir, numBands, outName):
	
	print "\nRunning mosaic process"
	rasterListStr =""
	rasterListStr = ";".join(rasterList)
	arcpy.MosaicToNewRaster_management(rasterListStr, outputDir, "mosaicAlpha.tif", None, None, None, numBands, "LAST","MATCH")
	
	trunkToFourLayerTif(os.path.join(outputDir, "mosaicAlpha.tif"), outputDir, outName+'_mosaic.tif')
	
	return outputDir+outName+"_mosaic.tif"
	

def trunkToFourLayerTif(inputTif, workDir, outName):

	print "\nTruncating alpha band"
	vtab = arcpy.CreateObject("ValueTable")    
	vtab.addRow(os.path.join(inputTif, "Band_1")) 
	vtab.addRow(os.path.join(inputTif, "Band_2"))  
	vtab.addRow(os.path.join(inputTif, "Band_3"))  
	vtab.addRow(os.path.join(inputTif, "Band_4"))
	arcpy.CompositeBands_management(vtab, os.path.join(workDir,'fourComp.tif'))
	arcpy.Delete_management(inputTif)
	arcpy.Rename_management(os.path.join(workDir, 'fourComp.tif'), outName)
	
def addNDVI(inputTif, workDir, outName):

	arcpy.CheckOutExtension('spatial')
	
	print "\nCalculating NDVI and stacking to band 5"
	red = arcpy.sa.Raster(os.path.join(inputTif, "Band_1"))
	NIR = arcpy.sa.Raster(os.path.join(inputTif, "Band_4"))
	
	numerator = arcpy.sa.Float(NIR-red)
	denominator = arcpy.sa.Float(NIR+red)
	NDVI = arcpy.sa.Divide(numerator, denominator)
	NDVI_times = arcpy.sa.Times(NDVI, 100)
	NDVI_add = arcpy.sa.Plus(NDVI_times, 100)
	NDVI_int = arcpy.sa.Int(NDVI_add)
	
	vtab = arcpy.CreateObject("ValueTable")    
	vtab.addRow(os.path.join(inputTif, "Band_1")) 
	vtab.addRow(os.path.join(inputTif, "Band_2"))  
	vtab.addRow(os.path.join(inputTif, "Band_3"))  
	vtab.addRow(os.path.join(inputTif, "Band_4"))
	vtab.addRow(NDVI_int)
	arcpy.CompositeBands_management(vtab, os.path.join(workDir, outName+'_RGBNIR_NDVI.tif'))
	
	arcpy.CheckInExtension('spatial')

	return os.path.join(workDir, outName+'_RGBNIR_NDVI.tif')
	
def getRasters(quadFile):
	
	quarQuadsDir = [f for f in os.listdir(quadFile) if not os.path.isfile(quadFile+f)]

	quarQuads = list()
	for quart in quarQuadsDir:
		quarQuads.append(os.path.join(quadFile+quart,""))
	
	quarImage = list()
	for quarDir in quarQuads:
		for file in os.listdir(quarDir):
			#print file
			if file.endswith(".jp2"):
				quarImage.append(os.path.join(quarDir,file))
	
	return quarImage
	
def getOutputName(quadDir):

	return os.path.basename(quadDir)
	
def checkPath(path):

	if not os.path.exists(path):
		raise Exception('File path error, check input path')
	return path
	
def checkBandsRetNum(rastList):
	
	prevBandCount = arcpy.GetRasterProperties_management (rastList[0], "BANDCOUNT", None)
	for raster in rastList:
		currBandCount = arcpy.GetRasterProperties_management (raster, "BANDCOUNT", None)
		if str(currBandCount) != str(prevBandCount):
			print str(currBandCount) + " to " + str(prevBandCount)
			raise Exception('Number of bands do not match')
		
	return str(prevBandCount)
	
def makeTempLocalCopy(rasterList, tempDir):
	
	print "\nCopying rasters to temp directory"
	
	for raster in rasterList:
		dirname = os.path.dirname(raster)
		for file in os.listdir(dirname):
			shutil.copy(os.path.join(dirname,file), tempDir)
	# for raster in rasterList:
		# arcpy.Copy_management(raster,tempDir+str(raster).split('\\')[-1])
	
	tempRasDirList = list()
	for file in os.listdir(tempDir):
			if file.endswith(".jp2"):
				tempRasDirList.append(os.path.join(tempDir,file))
	
	return tempRasDirList
	
def copyToDestination(rasterPath,quadDir):

	arcpy.Copy_management(rasterPath,quadDir+rasterPath.split('\\')[-1])

def main(cmdLinePath):

	try:
		#arcpy.CheckOutExtension('spatial')
		tempDir = tempfile.mkdtemp()
		
		arcpy.env.pyramid = "NONE"
		
		userDir = cmdLinePath
			
		quadDir = checkPath(userDir) #Checks for valid path and adds backslash if there is none, returns directory path with slash

		print "\nQuarter-quad directory: " + quadDir
		
		rasterList = getRasters(quadDir) #Gets the list of rasters in quad directory, looks only for files in NW,NE,etc.. directories 
		
		print "\nQuarter-quad mosaic and NDVI stack process running for rasters listed below\n"
		
		for raster in rasterList:
			print raster

		print "\nProcessing started: " + str(datetime.datetime.now().strftime("%I:%M:%S %p %d %B %Y"))
		
		tempRasters= makeTempLocalCopy(rasterList,tempDir) #Returns list of rasters in temp directory as well as temp directory path 
		
		quadName = getOutputName(quadDir)
		
		arcpy.env.workspace = tempDir
		
		mosaicResult = mosaicRasters(tempRasters, tempDir, checkBandsRetNum(rasterList), quadName)
		
		mosaicWithNDVIPath = addNDVI(mosaicResult, tempDir, quadName)
		
		print "\nCopying results to " + quadName + " directory"
		copyToDestination(mosaicResult,quadDir)
		copyToDestination(mosaicWithNDVIPath, quadDir)
		
		print "\nProcessing finished: " + str(datetime.datetime.now().strftime("%I:%M:%S %p %d %B %Y"))
		#arcpy.CheckInExtension('spatial')
		
	except Exception as error:
		print "Exception caught: " + repr(str(error))
		print "\nPress enter to close..."
		raw_input()
		
	finally:
		shutil.rmtree(tempDir)
		print '\nClosing...'


if __name__ == '__main__':

	if (len(sys.argv)-1):
		main(sys.argv[1])
	else:
		print "Must have file path as argument"

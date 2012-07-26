import arcpy
import os
from arcpy import management as DM
from time import time
from string import zfill
from datetime import date
from arcpy.sa import *
arcpy.env.workspace = "C:/WorkSpace/Phase5/Objects/p5_working.gdb"
outf = open("c:/workspace/phase5/Objects/modellog.txt", "a")
outf.writelines("\n" + str(date.today()) + " --p5_working elevation,slope,insolation--\n")

def elapsed_time(t0):
	seconds = int(round(time() - t0))
	h,rsecs = divmod(seconds,3600)
	m,s = divmod(rsecs,60)
	return zfill(h,2) + ":" + zfill(m,2) + ":" + zfill(s,2)

starttime = time()

processstart = time()
# fcs = arcpy.ListFeatureClasses("*", "polygon")
fcs = ["p5_north_working", "p5_south_working"]
arcpy.CheckOutExtension("Spatial")

for fc in fcs:
	outf.writelines("\nProcessing: "+fc)
	print "Processing: " + fc
# Make layer name for objects feature class
	layername = "l_"+fc
	print "Layername for polys= " + layername
# Make layer for objects feature class
	DM.MakeFeatureLayer(fc, layername)
# Add fields for elevation, slope, and insolation in objects feature class
	print "Adding field to poly feature class for elevation, slope, and insolation"
#	DM.AddField(fc, "elev", "DOUBLE")
	DM.AddField(fc, "slp", "DOUBLE")
#	DM.AddField(fc, "insol", "LONG")
# Make name for point feature class
	ptFeatures = "p" + fc
# follwoing line used to produce point feature class with centroid of objects
	print "Building centroid file"
	DM.FeatureToPoint(fc, ptFeatures, "CENTROID")
# Make feature class names to accept extract values.
	ptFeatureElev = "e" + ptFeatures
	ptFeatureSlope = "s"+ptFeatures
#	ptFeatureInsol = "i" + ptFeatures
# following line used to extract elevation from DEM where DEM is called m_dem and resides in the geodatabase
#	print "Extracting elevation to points"
#	ExtractValuesToPoints(ptFeatures, "m_dem", ptFeatureElev, "INTERPOLATE", "VALUE_ONLY")
	print "Extracting slope to points"
	ExtractValuesToPoints(ptFeatures, "slope", ptFeatureSlope, "INTERPOLATE", "VALUE_ONLY")
#	print "Extracting insolation to points"
#	ExtractValuesToPoints(ptFeatures, "insol", ptFeatureInsol, "INTERPOLATE", "VALUE_ONLY")
	
#	elevfield = fc + ".elev"
	slopefield = fc + ".slp"
#	insolfield = fc + ".insol"
	
#	sourcefield = "["+ptFeatureElev+".RASTERVALU]"
#	print "Joining elevation points to polygons"
#	DM.AddJoin(layername, "OBJECTID", ptFeatureElev, "ORIG_FID", "KEEP_ALL")
#	print "Moving elevation data to objects"
#	DM.CalculateField(layername, elevfield, sourcefield, "VB", "")
#	DM.RemoveJoin(layername, ptFeatureElev)

	print "Joining slope points to polygons"
	DM.AddJoin(layername, "OBJECTID", ptFeatureSlope, "ORIG_FID", "KEEP_ALL")
	sourcefield = "[" + ptFeatureSlope + ".RASTERVALU]"
	print "Moving slope data to objects"
	DM.CalculateField(layername, slopefield, sourcefield, "VB", "")
	DM.RemoveJoin(layername, ptFeatureSlope)
	
#	print "Joining insol points to polygons"
#	DM.AddJoin(layername, "OBJECTID", ptFeatureInsol, "ORIG_FID", "KEEP_ALL")
#	sourcefield = "[" + ptFeatureInsol + ".RASTERVALU]"
#	print "Moving insolation data to objects"
#	DM.CalculateField(layername, insolfield, sourcefield, "VB", "")
#	DM.RemoveJoin(layername, ptFeatureInsol)

	DM.Delete(ptFeatures)
#	DM.Delete(ptFeatureElev)
	DM.Delete(ptFeatureSlope)
#	DM.Delete(ptFeatureInsol)
	
	print "process time = " + elapsed_time(processstart)
	outf.writelines("\nCompleted file processing. " + elapsed_time(processstart) + "\n")
	processstart = time()

	
print "Finished - Elapsed Time = " + elapsed_time(starttime)
outf.writelines("\nFinished. " + elapsed_time(starttime) + "\n\n")
outf.close()

import arcpy
import os
from arcpy import management as DM
from time import time
from string import zfill
from datetime import date
from arcpy.sa import *
arcpy.env.workspace = "C:/WorkSpace/Phase5/Objects/test.gdb"
outf = open("c:/workspace/phase5/Objects/modellog.txt", "a")
outf.writelines("\n" + str(date.today()) + " --Points for p5west-\n")
geodb = "test_lg.gdb/"

def elapsed_time(t0):
	seconds = int(round(time() - t0))
	h,rsecs = divmod(seconds,3600)
	m,s = divmod(rsecs,60)
	return zfill(h,2) + ":" + zfill(m,2) + ":" + zfill(s,2)

# Apply models from key in separate dbf for each landcover
#suffixes = ["01","03","05","07","09","11","13","15","19","21","23","25","27","31"]
#covers = [1,3,5,7,9,11,13,15,19,21,23,25,27,31]
starttime = time()

processstart = time()
fcs = arcpy.ListFeatureClasses("*", "polygon")

# drop_fields = ["VegNum1"]

#for fc in fcs:
#	try:
#		print fc
#		#DM.AddField(fc, "VegNum", "LONG")
#		#DM.DeleteField(fc, drop_fields)
#	except Exception, e:
#		# If an error occurred, print line number and error message
#		import traceback, sys
#		tb = sys.exc_info()[2]
#		print "Line %i" % tb.tb_lineno
#		print e.message
#print "process time = " + elapsed_time(processstart)
#outf.writelines("Completed adding field. " + elapsed_time(processstart) + "\n")
#processstart = time()
selectstring = "\"ECOCLASSNA\" = 'Gravelly, Hot Desert Shrub' and \"slope20\" = 0"
arcpy.CheckOutExtension("Spatial")
for fc in fcs:
	outf.writelines("\nProcessing: "+fc)
	print "Processing: " + fc
	layername = "l_"+fc
	DM.MakeFeatureLayer(fc, layername)
	DM.AddField(fc, "elev", "DOUBLE")
	ptFeatures = fc + "_pt"
# follwoing line used to produce point feature class with centroid of objects
	DM.FeatureToPoint(fc, ptFeatures, "CENTROID")
	ptFeatureElev = ptFeatures+"_elev"
# following line used to extract elevation from DEM where DEM is called m_dem and resides in the geodatabase
	ExtractValuesToPoints(ptFeatures, "m_dem", ptFeatureElev, "INTERPOLATE", "VALUE_ONLY")
	elevLayer = "e_" + ptFeatureElev
	DM.MakeFeatureLayer(ptFeatureElev, elevLayer)
	elevfield = fc + ".elev"
	sourcefield = "["+ptFeatureElev+".RASTERVALU]"
	DM.AddJoin(layername, "OBJECTID", elevLayer, "ORIG_FID", "KEEP_ALL")
	DM.CalculateField(layername, elevfield, sourcefield, "VB", "")
	DM.RemoveJoin(layername, ptFeatureElev)
	DM.Delete(ptFeatures)
	DM.Delete(ptFeatureElev)
	
	

print "process time = " + elapsed_time(processstart)
outf.writelines("\nCompleted select and calculate field. " + elapsed_time(processstart) + "\n")
processstart = time()

	
print "Finished - Elapsed Time = " + elapsed_time(starttime)
outf.writelines("\nFinished. " + elapsed_time(starttime) + "\n\n")
outf.close()

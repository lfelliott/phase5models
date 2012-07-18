from arcpy import management as DM
from time import time
from string import zfill
from datetime import date


gdbpath = "c:\\Workspace\\Phase5\\Objects\\p5_working_20120712.gdb\\"
cities = "D:\\GIS\\Texas Base Layers.gdb\\Cities"
citylayer = "l_cities"
DM.MakeFeatureLayer(cities, citylayer)
print "Making city layer."

selectstr = "\"lulc\" = 1 or \"lulc\" = 3 OR \"lulc\" = 5 or \"lulc\" = 19 or \"lulc\" = 11 or \"lulc\" = 31 or \"lulc\" =27"
print selectstr

starttime = time()

def elapsed_time(t0):
	seconds = int(round(time() - t0))
	h,rsecs = divmod(seconds,3600)
	m,s = divmod(rsecs,60)
	return zfill(h,2) + ":" + zfill(m,2) + ":" + zfill(s,2)

def applycities(fc):
	p5_working = "%s%s" % (gdbpath, fc)
	layername = "l_p5_%s" % fc
	print "Making working layer for " + fc
	DM.MakeFeatureLayer(p5_working, layername)
	print "selecting by location"
	DM.SelectLayerByLocation(layername, "COMPLETELY_WITHIN", citylayer, "", "NEW_SELECTION")
	print "selecting by attribute"
	DM.SelectLayerByAttribute(layername, "SUBSET_SELECTION", selectstr)
	if (int(str(DM.GetCount(layername))) > 0):
		print "calculating on " + str(DM.GetCount(layername)) + " objects."
#		DM.CalculateField(layername, "lulc", 25)
		DM.CalculateField(layername, "VegNum", 9411)
	else:
		print "nothing to calculate"
		
def applyroads(fc):
	roadselect = "\"road\" = 1 and not (\"VegNum\" = 9410 or \"VegNum\" = 9411)"
	p5_working = "%s%s" % (gdbpath, fc)
	layername = "lr_p5_%s" % fc
	print "Making working layer for " + fc
	DM.MakeFeatureLayer(p5_working, layername)
	print "selecting by attribute"
	DM.SelectLayerByAttribute(layername, "NEW_SELECTION", roadselect)
	if (int(str(DM.GetCount(layername))) > 0):
		print "calculating on " + str(DM.GetCount(layername)) + " objects."
		DM.CalculateField(layername, "VegNum", 9411)
	else:
		print "nothing to calculate"

fcs = ["west_working", "working", "north_working"]
for item in fcs:
	processstart = time()
	applycities(item)
	print "process time (cities)= " + elapsed_time(processstart) + " for " + item + "."
	processstart = time()
	applyroads(item)
	print "process time (roads)= " + elapsed_time(processstart) + " for " + item + "."

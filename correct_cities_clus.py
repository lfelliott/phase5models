from arcpy import management as DM
from time import time
from string import zfill
from datetime import date


gdbpath = "c:\\Workspace\\Phase5\\Objects\\p5_checksoils_20120725.gdb\\"
cities = "D:\\GIS\\Texas Base Layers.gdb\\Cities"
citylayer = "l_cities"
DM.MakeFeatureLayer(cities, citylayer)
print "Making city layer."

selectstr = "(\"lulc\" = 1 or \"lulc\" = 3 OR \"lulc\" = 5 or \"lulc\" = 19 or \"lulc\" = 11 or \"lulc\" = 31 or \"lulc\" =27) and not (\"VegNum\" = 9410 or \"VegNum\" = 9411)"
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

def fixclu(fc):
	p5_working = "%s%s" % (gdbpath, fc)
	layername = "lclu_p5_%s" % fc
	# Remember don't need to embed quotes for the calcfield
	calcfield = "%s.VegNum" % fc
	cluobjs_dbf = "C:\\WorkSpace\\Phase5\\Objects\\cluobjs.dbf"
	print "Making working layer for " + fc
	DM.MakeFeatureLayer(p5_working, layername)
	print "joining to clu dbf"
	DM.AddJoin(layername, "morap_objid", cluobjs_dbf, "morap_obji", "KEEP_COMMON")
	print "select all to see how many we have"
	DM.SelectLayerByAttribute(layername, "SWITCH_SELECTION", "")
	if (int(str(DM.GetCount(layername))) > 0):
		print "calculating for " + calcfield + " for " + str(DM.GetCount(layername)) + " objects"
		DM.CalculateField(layername, calcfield, "[cluobjs.VegNum]", "VB", "")
	else:
		print "no objects selected"
	DM.RemoveJoin(layername, "cluobjs")
	
def fixorchards(fc):
	p5_working = "%s%s" % (gdbpath, fc)
	layername = "lclu_p5_%s" % fc
	# Remember don't need to embed quotes for the calcfield
	calcfield = "%s.VegNum" % fc
	orchard_dbf = "C:\\WorkSpace\\Phase5\\Objects\\orchards.dbf"
	print "Making working layer for " + fc
	DM.MakeFeatureLayer(p5_working, layername)
	print "joining to orchard dbf"
	DM.AddJoin(layername, "morap_objid", orchard_dbf, "morap_obji", "KEEP_COMMON")
	print "select all to see how many we have"
	DM.SelectLayerByAttribute(layername, "SWITCH_SELECTION", "")
	if (int(str(DM.GetCount(layername))) > 0):
		print "calculating for " + calcfield + " for " + str(DM.GetCount(layername)) + " objects"
		DM.CalculateField(layername, calcfield, "[orchards.VegNum]", "VB", "")
	else:
		print "no objects selected"
	DM.RemoveJoin(layername, "orchards")

print "working on " + gdbpath	

fcs = ["south_checksoils", "west_checksoils", "north_checksoils"]
for item in fcs:
	processstart = time()
	applycities(item)
	print "process time (cities)= " + elapsed_time(processstart) + " for " + item + "."
#	fix roads in initial model application
#	processstart = time()
#	applyroads(item)
#	print "process time (roads)= " + elapsed_time(processstart) + " for " + item + "."

processstart = time()
fixclu("north_checksoils")
print "process time (clu)= " + elapsed_time(processstart)
processtart = time()
fixorchards("west_checksoils")
print "process time (orchards) = " + elapsed_time(processstart)
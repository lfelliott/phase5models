from arcpy import management as DM
from time import time
from string import zfill
from datetime import date

gdbpath = "c:\\Workspace\\Phase5\\Objects\\p5_checksoils_20120725.gdb\\"

juniper_range = "D:\\GIS\\US\\Little\\junipers.shp"
juniperlayer = "l_juniper"
print "Making juniper layer."
DM.MakeFeatureLayer(juniper_range, juniperlayer)

liveoakrange = "d:\\GIS\\US\\Little\\quervirg.shp"
lolayer = "l_liveoak"
print "Making live oak layer."
DM.MakeFeatureLayer(liveoakrange, lolayer)

selectstr = "(\"VegNum\" = 9101 or \"VegNum\" = 9105) and  \"epa_ecoreg\" like '25%'"
print selectstr
selectstrlo = "\"VegNum\" = 1402"
print selectstrlo

starttime = time()

def elapsed_time(t0):
	seconds = int(round(time() - t0))
	h,rsecs = divmod(seconds,3600)
	m,s = divmod(rsecs,60)
	return zfill(h,2) + ":" + zfill(m,2) + ":" + zfill(s,2)

def applyjuniper(fc):
	p5_working = "%s%s" % (gdbpath, fc)
	layername = "lj_p5_%s" % fc
	print "Making working layer for " + fc
	DM.MakeFeatureLayer(p5_working, layername)
	print "selecting by attribute"
	DM.SelectLayerByAttribute(layername, "NEW_SELECTION", selectstr)
	DM.SelectLayerByLocation(layername, "INTERSECT", juniperlayer, "", "REMOVE_FROM_SELECTION")	
	if (int(str(DM.GetCount(layername))) > 0):
		print "calculating on " + str(DM.GetCount(layername)) + " objects."
		DM.CalculateField(layername, "VegNum", 9204)
	else:
		print "nothing to calculate"
	print "selecting by location"

def fixsaltcedar(fc):
	# this is mostly on riparian or loamy, clay loam etc.
	selectstr2 = "(\"lulc\" = 11 or \"lulc\" = 19) and \"EcoGroup\" not like '%Bottomland%' and \"VegNum\" = 9204 and (\"epa_ecoreg\" like '30%' or \"epa_ecoreg\" like '26%' or \"epa_ecoreg\" = '24e')"
	p5_working = "%s%s" % (gdbpath, fc)
	layername = "ls_p5_%s" % fc
	print "Making working layer for " + fc
	DM.MakeFeatureLayer(p5_working, layername)
	print "selecting by attribute"
	DM.SelectLayerByAttribute(layername, "NEW_SELECTION", selectstr2)
	if (int(str(DM.GetCount(layername))) > 0):
		print "calculating on " + str(DM.GetCount(layername)) + " objects."
		DM.CalculateField(layername, "VegNum", 9105)
	else:
		print "nothing to calculate"	

def applyliveoak(fc):
	p5_working = "%s%s" % (gdbpath, fc)
	layername = "lo_p5_%s" % fc
	print "Making working layer for " + fc
	DM.MakeFeatureLayer(p5_working, layername)
	print "selecting by attribute"
	DM.SelectLayerByAttribute(layername, "NEW_SELECTION", selectstrlo)
	print "remove polys within live oak range from selection"
	DM.SelectLayerByLocation(layername, "COMPLETELY_WITHIN", lolayer, "", "REMOVE_FROM_SELECTION")	
	if (int(str(DM.GetCount(layername))) > 0):
		print "calculating on " + str(DM.GetCount(layername)) + " objects."
		DM.CalculateField(layername, "VegNum", 1401)
	else:
		print "nothing to calculate"
		

print "working on " + gdbpath
northfc = "north_checksoils"
fcs = ["south_checksoils", "north_checksoils"]
for item in fcs:
	processstart = time()
	# saltcedar fix needs to go first
	fixsaltcedar(item)
	print "process time (fixsaltcedar)= " + elapsed_time(processstart) + " for " + item + "."
	processstart = time()
	applyliveoak(item)
	print "process time (liveoak)= " + elapsed_time(processstart) + " for " + item + "."
processstart = time()
applyjuniper(northfc)
print "process time (juniper)= " + elapsed_time(processstart) + " for north."
from arcpy import management as DM
from arcpy import analysis as AN
from time import time
from string import zfill
from datetime import date

gdbpath = "c:\\Workspace\\Phase5\\Objects\\p5_checksoils_20120725.gdb\\"
north = "north_checksoils"
west = "west_checksoils"
south = "south_checksoils"

def elapsed_time(t0):
	seconds = int(round(time() - t0))
	h,rsecs = divmod(seconds,3600)
	m,s = divmod(rsecs,60)
	return zfill(h,2) + ":" + zfill(m,2) + ":" + zfill(s,2)

starttime = time()
	
# Variables for adding cliffs
selectbase = "\"slope100\" = 1 AND \"epa_ecoreg\" like "
vegtypes =[]
vegdict = {}

#define selectstrings for each cliff type
vegtypes.append(2100)
vegdict[2100] = selectbase + "'26%'"
vegtypes.append(3100)
vegdict[3100] = selectbase + "'25%' AND (\"lulc\" = 1 OR \"lulc\" = 15 OR \"lulc\" = 27)"
vegtypes.append(3104)
vegdict[3104] = selectbase + "'25%' AND (\"lulc\" = 3 OR \"lulc\" = 5 OR \"lulc\" = 7 OR \"lulc\" = 11 OR \"lulc\" = 19 OR \"lulc\" = 31)"
vegtypes.append(10100)
vegdict[10100] = selectbase + "'24%'"
vegtypes.append(807)
vegdict[807] = "\"slope100\" = 1 AND (\"epa_ecoreg\" like '30%' OR \"epa_ecoreg\" = '24e') AND (\"lulc\" = 1 OR \"lulc\" = 15 OR \"lulc\" = 27)"
vegtypes.append(806)
vegdict[806] = "\"slope100\" = 1 AND (\"epa_ecoreg\" like '30%' OR \"epa_ecoreg\" = '24e') AND (\"lulc\" = 3 OR \"lulc\" = 5 OR \"lulc\" = 7 OR \"lulc\" = 11 OR \"lulc\" = 19 OR \"lulc\" = 31)"

# Variables for eliminate objects
elim_objs = "%stemp_elim" % gdbpath

eliminated_result = "%stemp_eliminated" % gdbpath

intrsct_result = "%stemp_intrsct" % gdbpath
intrsct_lyr = "l_temp_intrsct"

elim_subset = "%stemp_elim_subset" % gdbpath
elim_subsetlyr = "l_temp_elim_subset"
test_subset = "%stest_suubset" % gdbpath

# Variables for correctin juniper and liveoak
juniper_range = "D:\\GIS\\US\\Little\\junipers.shp"
juniperlayer = "l_juniper"
print "Making juniper layer."
DM.MakeFeatureLayer(juniper_range, juniperlayer)

liveoakrange = "d:\\GIS\\US\\Little\\quervirg.shp"
lolayer = "l_liveoak"
print "Making live oak layer."
DM.MakeFeatureLayer(liveoakrange, lolayer)
selectstrj = "(\"VegNum\" = 9101 or \"VegNum\" = 9105) and  \"epa_ecoreg\" like '25%'"
selectstrlo = "\"VegNum\" = 1402"
selectstrsc = "(\"lulc\" = 11 or \"lulc\" = 19) and \"EcoGroup\" not like '%Bottomland%' and \"VegNum\" = 9204 and (\"epa_ecoreg\" like '30%' or \"epa_ecoreg\" like '26%' or \"epa_ecoreg\" = '24e')"

# Variables for cities, clus and orchards
cities = "D:\\GIS\\Texas Base Layers.gdb\\Cities"
citylayer = "l_cities"
print "Making city layer."
DM.MakeFeatureLayer(cities, citylayer)
selectstrc = "(\"lulc\" = 1 or \"lulc\" = 3 OR \"lulc\" = 5 or \"lulc\" = 19 or \"lulc\" = 11 or \"lulc\" = 31 or \"lulc\" =27) and not (\"VegNum\" = 9410 or \"VegNum\" = 9411)"

	
def applyelimupdate(fc):
	elim_count = 1
	passcnt = 1
	while (elim_count > 0):
		calcfield = "%s.VegNum" % fc
		selectstr = "\"%s.Vegnum\" = 99998" % fc
		p5_working = "%s%s" % (gdbpath, fc)
		layername = "l_p5_%s" % fc
		print "Pass " + str(passcnt)
		print "Making working layer for " + fc
		DM.MakeFeatureLayer(p5_working, layername)
		passcnt = passcnt + 1
		print "selecting for vegnum = 99998"
		DM.SelectLayerByAttribute(layername, "NEW_SELECTION", '"VegNum" = 99998')
		elim_count = int(str(DM.GetCount(layername)))
		if (elim_count > 0):
			print "copying " + str(elim_count) + " selected objects to temp"
			DM.CopyFeatures(layername, elim_objs)
			print "select touching polys in larger layer to limit eliminate and select those with VegNum = 99998"
			DM.SelectLayerByLocation(layername, "INTERSECT", elim_objs)
			DM.CopyFeatures(layername, elim_subset)
			DM.MakeFeatureLayer(elim_subset, elim_subsetlyr)
			DM.SelectLayerByAttribute(elim_subsetlyr, "NEW_SELECTION", '"VegNum" = 99998')
			print "eliminating " + str(DM.GetCount(elim_subsetlyr)) + " selected features"
			DM.Eliminate(elim_subsetlyr, eliminated_result, "LENGTH")
			print "intersect eliminated by elim objects"
			AN.Intersect([eliminated_result, elim_objs], intrsct_result)
			print "make feature layer for joining and join on ORIG_FID_1"
			DM.MakeFeatureLayer(intrsct_result, intrsct_lyr)
			DM.AddJoin(layername, "ORIG_FID", intrsct_lyr, "ORIG_FID_1", "KEEP_COMMON")
			print "select string = " + selectstr
			DM.SelectLayerByAttribute(layername, "NEW_SELECTION", selectstr)
			print "calculate vegnum to " + calcfield + " for " + str(DM.GetCount(layername)) + " objects"
			DM.CalculateField(layername, calcfield, "[temp_intrsct.VegNum]", "VB", "")
			DM.RemoveJoin(layername, "temp_intrsct")
			print "deleting temp layers"
			DM.Delete(layername)
			DM.Delete(elim_subsetlyr)
			DM.Delete(intrsct_lyr)
			DM.Delete(elim_objs)
			DM.Delete(eliminated_result)
			DM.Delete(intrsct_result)
			DM.Delete(elim_subset)
		else:
			print "no remaining problem polygons to eliminate in " + fc

def addcliffs(fc):
	p5_working = "%s%s" % (gdbpath,fc)
	layername = "l_p5_%s" % fc
	print "Making working layer for " + fc
	DM.MakeFeatureLayer(p5_working, layername)
	for clifftype in vegtypes:
		print vegdict[clifftype]
		DM.SelectLayerByAttribute(layername, "NEW_SELECTION", vegdict[clifftype])
		if (int(str(DM.GetCount(layername))) > 0):
			print "adding cliff to " + str(DM.GetCount(layername)) + " objects"
			DM.CalculateField(layername, "VegNum", clifftype, "VB", "")
	DM.Delete(layername)

def applyjuniper(fc):
	p5_working = "%s%s" % (gdbpath, fc)
	layername = "lj_p5_%s" % fc
	print "Making working layer for " + fc
	DM.MakeFeatureLayer(p5_working, layername)
	print "selecting by attribute"
	DM.SelectLayerByAttribute(layername, "NEW_SELECTION", selectstrj)
	DM.SelectLayerByLocation(layername, "INTERSECT", juniperlayer, "", "REMOVE_FROM_SELECTION")	
	if (int(str(DM.GetCount(layername))) > 0):
		print "calculating on " + str(DM.GetCount(layername)) + " objects."
		DM.CalculateField(layername, "VegNum", 9204)
	else:
		print "nothing to calculate"
	print "selecting by location"

def fixsaltcedar(fc):
	# this is mostly on riparian or loamy, clay loam etc.
	p5_working = "%s%s" % (gdbpath, fc)
	layername = "ls_p5_%s" % fc
	print "Making working layer for " + fc
	DM.MakeFeatureLayer(p5_working, layername)
	print "selecting by attribute"
	DM.SelectLayerByAttribute(layername, "NEW_SELECTION", selectstrsc)
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

def applycities(fc):
	p5_working = "%s%s" % (gdbpath, fc)
	layername = "l_p5_%s" % fc
	print "Making working layer for " + fc
	DM.MakeFeatureLayer(p5_working, layername)
	print "selecting by location"
	DM.SelectLayerByLocation(layername, "COMPLETELY_WITHIN", citylayer, "", "NEW_SELECTION")
	print "selecting by attribute"
	DM.SelectLayerByAttribute(layername, "SUBSET_SELECTION", selectstrc)
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
		DM.CalculateField(layername, calcfield, 9304, "VB", "")
	else:
		print "no objects selected"
	DM.RemoveJoin(layername, "orchards")

		
print "working on " + gdbpath

fcs = [south, west, north]
#fcs = ["west_working", "south_working"]
#fcs = ["north_working"]
for item in fcs:
	processstart = time()
	applyelimupdate(item)
	print "process time = " + elapsed_time(processstart) + " for " + item + ".\n"
	processstart = time()
	addcliffs(item)	
	print "process time (cliffs)= " + elapsed_time(processstart) + " for " + item + "."
	if (item != north):
		processstart = time()
		# saltcedar fix needs to go first
		fixsaltcedar(item)
		print "process time (fixsaltcedar)= " + elapsed_time(processstart) + " for " + item + "."
		processstart = time()
		applyliveoak(item)
		print "process time (liveoak)= " + elapsed_time(processstart) + " for " + item + "."
	else:
		processstart = time()
		applyjuniper(north)
		print "process time (juniper)= " + elapsed_time(processstart) + " for north."
	processstart = time()
	applycities(item)
	print "process time (cities)= " + elapsed_time(processstart) + " for " + item + "."
	if (item == north):
		processstart = time()
		fixclu("north_checksoils")
		print "process time (clu)= " + elapsed_time(processstart)
	if (item == west):
		processtart = time()
		fixorchards("west_checksoils")
		print "process time (orchards) = " + elapsed_time(processstart)
		
print "Total elapsed time: " + elapsed_time(starttime)